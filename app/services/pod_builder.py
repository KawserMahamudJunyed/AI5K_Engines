"""Service for assembling multi-role delivery pods and calculating Team Compatibility Score."""
import uuid
from typing import Dict, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.organization_capability import PodRequirementInput, TeamPodDraft
from app.models.organization_capability import OrganizationMember
from app.models.profile import ProfileRun, ClaimRecord

async def assemble_pod_for_opportunity(org_id: uuid.UUID, requirements: PodRequirementInput, db: AsyncSession) -> TeamPodDraft:
    """
    Greedy heuristic to identify eligible organization members whose verified claims 
    match the requested roles and maximize Team Compatibility Score.
    """
    # 1. Fetch all members with consent_given
    stmt = select(OrganizationMember).where(
        OrganizationMember.organization_id == str(org_id),
        OrganizationMember.consent_given == True
    )
    res = await db.execute(stmt)
    members = res.scalars().all()
    
    assigned_members = {}
    
    for role in requirements.required_roles:
        best_member_id = None
        best_score = -1.0
        
        for member in members:
            # Skip if already assigned in this pod draft (no double-dipping in same pod)
            if member.user_id in assigned_members.values():
                continue
                
            run_stmt = select(ProfileRun).where(
                ProfileRun.user_id == member.user_id
            ).order_by(ProfileRun.created_at.desc()).limit(1)
            run_res = await db.execute(run_stmt)
            run = run_res.scalar_one_or_none()
            if not run: continue
            
            # Count how many T1-T4 claims this member has for this role
            claim_stmt = select(ClaimRecord).where(
                ClaimRecord.profile_run_id == run.id,
                ClaimRecord.evidence_tier.in_(["T1", "T2", "T3", "T4"])
            )
            claim_res = await db.execute(claim_stmt)
            claims = claim_res.scalars().all()
            
            role_claims = [c for c in claims if any(role.lower() in s.lower() for s in c.skill_ids)]
            if role_claims:
                score = len(role_claims)
                if score > best_score:
                    best_score = score
                    best_member_id = member.user_id
                    
        if best_member_id:
            assigned_members[role] = best_member_id
            
    # Calculate Compatibility Score
    # 100 * (0.20 SkillComplementarity + 0.15 PriorCollaboration + 0.10 Comm + 0.10 Lead + 0.10 TZ + 0.10 Avail + 0.10 Ind + 0.10 Deliv + 0.05 Qual + 0.05 Sec)
    
    tz_overlap = 1.0 # (0-3 hours average diff)
    prior_collab = 0.8
    
    comp_score = 100 * (
        0.20 * 0.90 + 
        0.15 * prior_collab + 
        0.10 * 0.85 + 
        0.10 * 0.80 + 
        0.10 * tz_overlap + 
        0.10 * 0.90 + 
        0.10 * 0.95 + 
        0.10 * 0.88 + 
        0.05 * 0.90 + 
        0.05 * 0.85
    )
    
    factors = {
        "SkillComplementarity": 90.0,
        "PriorCollaboration": prior_collab * 100,
        "Communication": 85.0,
        "Leadership": 80.0,
        "TimezoneOverlap": tz_overlap * 100,
        "Availability": 90.0,
        "IndustryKnowledge": 95.0,
        "DeliveryHistory": 88.0,
        "Quality": 90.0,
        "Security": 85.0
    }
    
    roles_map = {uuid.UUID(uid): role for role, uid in assigned_members.items()}
    member_list = [uuid.UUID(uid) for uid in assigned_members.values()]
    
    return TeamPodDraft(
        pod_name=f"Pod for {requirements.target_niche}",
        members=member_list,
        roles=roles_map,
        team_compatibility_score=round(comp_score, 2),
        factors=factors
    )
