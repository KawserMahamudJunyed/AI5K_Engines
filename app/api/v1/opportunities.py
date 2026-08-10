"""FastAPI router for the Opportunity Intelligence Engine."""
from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.db import get_db
from app.core.deps import get_current_user, require_permission
from app.schemas.opportunity import OpportunityInput, ParsedOpportunity, OpportunityMatchScore, ProposalDraft
from app.schemas.claim import Claim, SourceSpan
from app.models.opportunity import Opportunity, OpportunityMatch, ProposalDraftModel
from app.models.profile import ProfileRun, ClaimRecord
from app.services.opportunity_ingest import ingest_and_normalize, check_deduplication
from app.services.matcher import calculate_match_score
from app.services.proposal_draft import draft_verifiable_proposal
from app.services.audit import write_audit_log

router = APIRouter(prefix="/api/v1/opportunities", tags=["Opportunities"])


@router.post("", response_model=ParsedOpportunity, status_code=status.HTTP_201_CREATED)

async def ingest_opportunity(
    raw_post: OpportunityInput,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user)
) -> ParsedOpportunity:
    """Ingest, normalize, and save a new job opportunity."""
    # 1. Deduplication Check
    existing_opp = await check_deduplication(raw_post.title, raw_post.description, db)
    if existing_opp:
        return ParsedOpportunity(
            id=uuid.UUID(existing_opp.id),
            title=existing_opp.title,
            description=existing_opp.description,
            budget=existing_opp.budget,
            timezone_offset=existing_opp.timezone_offset,
            estimated_duration_weeks=existing_opp.estimated_duration_weeks,
            source_channel=existing_opp.source_channel,
            required_skills=existing_opp.required_skills,
            industry_vertical=existing_opp.industry_vertical,
            budget_tier=existing_opp.budget_tier,
            estimated_effort_hours=existing_opp.estimated_effort_hours
        )
        
    # 2. Normalize
    parsed_opp = await ingest_and_normalize(raw_post)
    
    # 3. Save to DB
    opp_model = Opportunity(
        title=parsed_opp.title,
        description=parsed_opp.description,
        budget=parsed_opp.budget,
        timezone_offset=parsed_opp.timezone_offset,
        estimated_duration_weeks=parsed_opp.estimated_duration_weeks,
        source_channel=parsed_opp.source_channel,
        required_skills=parsed_opp.required_skills,
        industry_vertical=parsed_opp.industry_vertical,
        budget_tier=parsed_opp.budget_tier,
        estimated_effort_hours=parsed_opp.estimated_effort_hours
    )
    db.add(opp_model)
    await db.flush()
    
    # Audit log must be written before committing
    await write_audit_log(
        action="opportunity.ingested",
        entity_type="Opportunity",
        entity_id=uuid.UUID(opp_model.id),
        metadata={"title": opp_model.title, "source": opp_model.source_channel}
    )
    
    await db.commit()
    await db.refresh(opp_model)
    
    # Return with generated ID
    dump = parsed_opp.model_dump()
    dump.pop("id", None)
    return ParsedOpportunity(
        **dump,
        id=uuid.UUID(opp_model.id)
    )

async def _get_active_user_claims(db: AsyncSession) -> List[Claim]:
    """Helper to fetch the active user's claims. 
    For MVP, we fetch claims from the most recent ProfileRun.
    """
    stmt = select(ProfileRun).order_by(ProfileRun.created_at.desc()).limit(1)
    result = await db.execute(stmt)
    latest_run = result.scalar_one_or_none()
    
    if not latest_run:
        return []
        
    claim_stmt = select(ClaimRecord).where(ClaimRecord.profile_run_id == latest_run.id)
    claim_result = await db.execute(claim_stmt)
    records = claim_result.scalars().all()
    
    claims = []
    for r in records:
        span = None
        if r.document_id and r.span_text is not None and r.span_start is not None and r.span_end is not None:
            span = SourceSpan(
                document_id=uuid.UUID(r.document_id),
                start_index=r.span_start,
                end_index=r.span_end,
                text=r.span_text
            )
            
        claims.append(Claim(
            claim_text=r.claim_text,
            skill_ids=r.skill_ids,
            source_type=r.source_type,
            evidence_tier=r.evidence_tier,
            tier_rule=r.tier_rule,
            source_span=span
        ))
    return claims


@router.post("/{opp_id}/match", response_model=OpportunityMatchScore)

async def match_opportunity(
    opp_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user)
) -> OpportunityMatchScore:
    """Calculate match score between the opportunity and the active candidate's claims."""
    
    stmt = select(Opportunity).where(Opportunity.id == str(opp_id))
    result = await db.execute(stmt)
    opp_model = result.scalar_one_or_none()
    
    if not opp_model:
        raise HTTPException(status_code=404, detail="Opportunity not found")
        
    parsed_opp = ParsedOpportunity(
        title=opp_model.title,
        description=opp_model.description,
        budget=opp_model.budget,
        timezone_offset=opp_model.timezone_offset,
        estimated_duration_weeks=opp_model.estimated_duration_weeks,
        source_channel=opp_model.source_channel,
        required_skills=opp_model.required_skills,
        industry_vertical=opp_model.industry_vertical,
        budget_tier=opp_model.budget_tier,
        estimated_effort_hours=opp_model.estimated_effort_hours
    )
    
    # Inject ID manually onto the Pydantic model for the matcher
    parsed_opp.__dict__["id"] = uuid.UUID(opp_model.id)
    
    user_claims = await _get_active_user_claims(db)
    
    match_score = await calculate_match_score(parsed_opp, user_claims, user_id)
    
    match_model = OpportunityMatch(
        opportunity_id=opp_model.id,
        user_id=str(user_id),
        overall_score=match_score.overall_score,
        skill_fit=match_score.skill_fit,
        evidence_quality_fit=match_score.evidence_quality_fit,
        industry_fit=match_score.industry_fit,
        timezone_fit=match_score.timezone_fit,
        budget_fit=match_score.budget_fit,
        missing_qualifications=match_score.missing_qualifications
    )
    db.add(match_model)
    await db.flush()
    
    await write_audit_log(
        action="opportunity.matched",
        entity_type="OpportunityMatch",
        entity_id=uuid.UUID(match_model.id),
        metadata={"overall_score": match_score.overall_score}
    )
    
    await db.commit()
    
    return match_score


@router.post("/{opp_id}/proposal", response_model=ProposalDraft)

async def generate_proposal(
    opp_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user)
) -> ProposalDraft:
    """Draft a verifiable proposal restricted to T1-T4 claims."""
    
    # 1. Fetch Opportunity
    stmt = select(Opportunity).where(Opportunity.id == str(opp_id))
    result = await db.execute(stmt)
    opp_model = result.scalar_one_or_none()
    
    if not opp_model:
        raise HTTPException(status_code=404, detail="Opportunity not found")
        
    parsed_opp = ParsedOpportunity(
        title=opp_model.title,
        description=opp_model.description,
        budget=opp_model.budget,
        timezone_offset=opp_model.timezone_offset,
        estimated_duration_weeks=opp_model.estimated_duration_weeks,
        source_channel=opp_model.source_channel,
        required_skills=opp_model.required_skills,
        industry_vertical=opp_model.industry_vertical,
        budget_tier=opp_model.budget_tier,
        estimated_effort_hours=opp_model.estimated_effort_hours
    )
    parsed_opp.__dict__["id"] = uuid.UUID(opp_model.id)
    
    # 2. Fetch Latest Match Score
    match_stmt = select(OpportunityMatch).where(
        OpportunityMatch.opportunity_id == opp_model.id,
        OpportunityMatch.user_id == str(user_id)
    ).order_by(OpportunityMatch.created_at.desc()).limit(1)
    match_result = await db.execute(match_stmt)
    match_model = match_result.scalar_one_or_none()
    
    if not match_model:
        raise HTTPException(status_code=400, detail="Must run match before generating proposal")
        
    match_score = OpportunityMatchScore(
        opportunity_id=uuid.UUID(match_model.opportunity_id),
        user_id=uuid.UUID(match_model.user_id),
        overall_score=match_model.overall_score,
        skill_fit=match_model.skill_fit,
        evidence_quality_fit=match_model.evidence_quality_fit,
        industry_fit=match_model.industry_fit,
        timezone_fit=match_model.timezone_fit,
        budget_fit=match_model.budget_fit,
        missing_qualifications=match_model.missing_qualifications
    )
    
    # 3. Fetch Claims & Draft
    user_claims = await _get_active_user_claims(db)
    
    draft = await draft_verifiable_proposal(parsed_opp, match_score, user_claims)
    
    # 4. Save to DB
    draft_model = ProposalDraftModel(
        opportunity_id=opp_model.id,
        draft_text=draft.draft_text,
        used_claims=draft.used_claims,
        validated=draft.validated
    )
    db.add(draft_model)
    await db.flush()
    
    await write_audit_log(
        actor_id=user_id,
        action="proposal.drafted",
        entity_type="ProposalDraft",
        entity_id=uuid.UUID(draft_model.id),
        metadata={"validated": draft.validated}
    )
    
    await db.commit()
    
    return draft
