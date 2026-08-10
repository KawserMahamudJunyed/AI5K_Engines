"""Service for calculating multi-factor matching scores."""
from __future__ import annotations

import uuid
from typing import List

from app.schemas.opportunity import ParsedOpportunity, OpportunityMatchScore
from app.schemas.claim import Claim

__all__ = ["calculate_match_score"]

def _get_tier_weight(tier: str) -> float:
    if tier in {"T1", "T2", "T3", "T4"}:
        return 1.0
    if tier in {"T5", "T6", "T7"}:
        return 0.5
    return 0.2  # T8

def _calculate_evidence_quality(matched_skills: set[str], user_claims: List[Claim]) -> float:
    if not matched_skills:
        return 0.0
        
    scores = []
    for skill in matched_skills:
        # Find best tier for this skill across all claims
        best_tier_weight = 0.0
        for claim in user_claims:
            if skill.lower() in [s.lower() for s in claim.skill_ids]:
                weight = _get_tier_weight(claim.evidence_tier)
                if weight > best_tier_weight:
                    best_tier_weight = weight
        scores.append(best_tier_weight)
        
    return (sum(scores) / len(scores)) * 100.0

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.profile import ProfileRun, ClaimRecord
from app.services.vector_service import generate_embedding

async def calculate_match_score(opportunity: ParsedOpportunity, user_claims: List[Claim], user_id: uuid.UUID, db: AsyncSession = None) -> OpportunityMatchScore:
    """Calculate the 5-factor match score between an opportunity and candidate claims using pgvector."""
    
    # 1. Skill Fit (40%) - Using pgvector Semantic Matching
    req_skills = set(s for s in opportunity.required_skills)
    matched_skills = set()
    
    if req_skills and db:
        # Get active profile run
        stmt = select(ProfileRun.id).order_by(ProfileRun.created_at.desc()).limit(1)
        active_profile_run_id = (await db.execute(stmt)).scalar_one_or_none()
        
        if active_profile_run_id:
            for req_skill in req_skills:
                # Generate embedding for the job's required skill
                req_vector = await generate_embedding(req_skill)
                
                # Query PostgreSQL for semantically similar verified claims (cosine similarity >= 0.78)
                # Cosine distance <= 0.22 means similarity >= 0.78
                match_stmt = select(ClaimRecord).where(
                    ClaimRecord.profile_run_id == active_profile_run_id,
                    ClaimRecord.embedding.cosine_distance(req_vector) <= 0.22,
                    ClaimRecord.evidence_tier.in_(["T1", "T2", "T3", "T4"])
                ).limit(1)
                
                hit = (await db.execute(match_stmt)).scalar_one_or_none()
                if hit:
                    matched_skills.add(req_skill.lower())
    
    # Fallback to static matching for any remaining skills (or if DB is unavailable)
    candidate_skills = set()
    for claim in user_claims:
        for skill in claim.skill_ids:
            candidate_skills.add(skill.lower())
            
    matched_skills.update(set(s.lower() for s in req_skills) & candidate_skills)
    
    missing_qualifications = list(set(s.lower() for s in req_skills) - matched_skills)
    
    skill_fit = 0.0
    if req_skills:
        skill_fit = (len(matched_skills) / len(req_skills)) * 100.0
    else:
        skill_fit = 100.0

    # 2. Evidence Quality Fit (20%)
    evidence_quality_fit = _calculate_evidence_quality(matched_skills, user_claims)
    
    # 3. Industry Fit (20%)
    # For MVP, we assume a static user industry. In a full system, this would pull from user profile.
    # Let's say the user is always 'AI/ML' for this test context.
    user_industry = "AI/ML"
    industry_fit = 10.0 # completely unrelated
    if opportunity.industry_vertical.lower() == user_industry.lower():
        industry_fit = 100.0
    elif "ai" in opportunity.industry_vertical.lower() or "software" in opportunity.industry_vertical.lower():
        industry_fit = 50.0
        
    # 4. Timezone Fit (10%)
    # Assume user is UTC (0) for MVP test context
    user_offset = 0
    diff = abs(user_offset - opportunity.timezone_offset)
    if diff <= 3:
        timezone_fit = 100.0
    elif diff <= 6:
        timezone_fit = 50.0
    else:
        timezone_fit = 10.0
        
    # 5. Budget Fit (10%)
    # Assume user desired rate is extracted from elsewhere; we will use 100 as fallback
    user_desired_rate = 100.0
    if user_desired_rate <= opportunity.budget:
        budget_fit = 100.0
    else:
        # Graded exponentially
        ratio = opportunity.budget / user_desired_rate
        budget_fit = (ratio ** 2) * 100.0
        
    # Overall Score
    overall_score = (
        (skill_fit * 0.40) +
        (evidence_quality_fit * 0.20) +
        (industry_fit * 0.20) +
        (timezone_fit * 0.10) +
        (budget_fit * 0.10)
    )

    # Ensure opportunity_id is populated (assume caller assigns it or it's a temp UUID if not yet committed)
    # The caller must pass a valid ParsedOpportunity containing an ID if it extends from DB,
    # but ParsedOpportunity doesn't have an ID. We will generate one if not present, or accept one.
    opp_id = getattr(opportunity, "id", None)
    if opp_id is None:
        opp_id = uuid.uuid4()

    return OpportunityMatchScore(
        opportunity_id=opp_id,
        user_id=user_id,
        overall_score=round(overall_score, 2),
        skill_fit=round(skill_fit, 2),
        evidence_quality_fit=round(evidence_quality_fit, 2),
        industry_fit=round(industry_fit, 2),
        timezone_fit=round(timezone_fit, 2),
        budget_fit=round(budget_fit, 2),
        missing_qualifications=missing_qualifications
    )
