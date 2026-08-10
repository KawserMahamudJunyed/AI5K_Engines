"""Service for calculating the 9-Factor Organization Capability Score."""
import uuid
import datetime
from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.organization_capability import OrgCapabilityResult, SkillStrengthDetail
from app.services.capability_aggregator import aggregate_organization_claims
from app.models.organization_capability import PodMemberAssignment

def _get_evidence_weight(tier: str) -> float:
    mapping = {
        "T1": 1.00, # Client-verified
        "T2": 0.90, # Project-demonstrated
        "T3": 0.80, # Assessed
        "T4": 0.70, # Certification-backed
        "T5": 0.60, # Organization-endorsed
        "T6": 0.50, # Peer-endorsed
        "T7": 0.42, # Fallback
        "T8": 0.35, # Self-declared
    }
    return mapping.get(tier, 0.35)

def _get_recency_factor(observed_date: datetime.datetime) -> float:
    now = datetime.datetime.now(datetime.timezone.utc)
    if observed_date.tzinfo is None:
        observed_date = observed_date.replace(tzinfo=datetime.timezone.utc)
    delta_days = (now - observed_date).days
    
    if delta_days < 365:
        return 1.0
    if delta_days < 730:
        return 0.85
    if delta_days < 1095:
        return 0.65
    return 0.45

async def calculate_org_capability_score(org_id: uuid.UUID, required_project_hours: float, db: AsyncSession) -> OrgCapabilityResult:
    """Calculates the 9-Factor Org Score and constructs the aggregated skills graph."""
    aggregated_claims = await aggregate_organization_claims(org_id, db)
    
    skills_map: Dict[str, SkillStrengthDetail] = {}
    total_claims = 0
    t8_claims = 0
    
    for claim, exclusivity_weight, availability_percentage in aggregated_claims:
        total_claims += 1
        if claim.evidence_tier == "T8":
            t8_claims += 1
            
        evidence_weight = _get_evidence_weight(claim.evidence_tier)
        recency = _get_recency_factor(claim.created_at)
        industry_relevance = 1.0 # Static for MVP
        
        available_member_hours = 40.0 * (availability_percentage / 100.0)
        availability_factor = min(1.0, available_member_hours / max(1.0, required_project_hours))
        
        proficiency = 0.8 # Static base for verified MVP claims
        
        strength = (proficiency * evidence_weight * recency * industry_relevance * availability_factor) * exclusivity_weight
        
        for skill in claim.skill_ids:
            skill = skill.lower()
            if skill not in skills_map or strength > skills_map[skill].final_strength:
                skills_map[skill] = SkillStrengthDetail(
                    skill_id=skill,
                    proficiency=proficiency,
                    evidence_weight=evidence_weight,
                    recency_factor=recency,
                    industry_relevance=industry_relevance,
                    availability_factor=availability_factor,
                    final_strength=round(strength, 4)
                )
    
    penalties = []
    penalty_score = 0.0
    
    # Penalty 1: Overbooked Capacity
    stmt = select(PodMemberAssignment).where(
        PodMemberAssignment.pod.has(organization_id=str(org_id))
    )
    res = await db.execute(stmt)
    assignments = res.scalars().all()
    user_hours = {}
    for a in assignments:
        user_hours[a.user_id] = user_hours.get(a.user_id, 0.0) + a.allocated_hours_per_week
        
    for uid, hours in user_hours.items():
        if hours > 40.0:
            penalties.append("Overbooked Capacity")
            penalty_score += 5.0
            break 
            
    # Penalty 2: Excessive Unverified Claims
    if total_claims > 0 and (t8_claims / total_claims) > 0.50:
        penalties.append("Excessive Unverified Claims")
        penalty_score += 5.0
        
    # Calculate 9-Factor Org Score
    avg_strength = sum(s.final_strength for s in skills_map.values()) / max(1, len(skills_map))
    
    skill_depth = avg_strength * 100
    delivery_outcomes = 80.0
    available_cap = 90.0
    coverage = 70.0
    quality = 85.0
    ind_rel = 100.0
    sec_readiness = 90.0
    gov_readiness = 80.0
    tz_align = 100.0
    
    base_score = 100 * (
        0.20 * (skill_depth/100) + 
        0.18 * (delivery_outcomes/100) + 
        0.12 * (available_cap/100) + 
        0.10 * (coverage/100) + 
        0.10 * (quality/100) + 
        0.10 * (ind_rel/100) + 
        0.08 * (sec_readiness/100) + 
        0.07 * (gov_readiness/100) + 
        0.05 * (tz_align/100)
    )
    
    final_score = max(0.0, base_score - penalty_score)
    
    factors = {
        "SkillDepth": round(skill_depth, 2),
        "DeliveryOutcomes": delivery_outcomes,
        "AvailableCapacity": available_cap,
        "CoverageRedundancy": coverage,
        "QualityReliability": quality,
        "IndustryRelevance": ind_rel,
        "SecurityReadiness": sec_readiness,
        "GovernanceReadiness": gov_readiness,
        "TimezoneAlign": tz_align
    }
    
    return OrgCapabilityResult(
        organization_id=org_id,
        overall_score=round(final_score, 2),
        skills_graph=skills_map,
        factors=factors,
        penalties_applied=penalties
    )
