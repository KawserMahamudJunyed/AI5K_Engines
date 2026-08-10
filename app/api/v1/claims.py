"""Claims REST API for fetching evidence lineage."""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.db import get_db
from app.core.deps import get_current_user
from app.models.profile import ClaimRecord
from app.schemas.claim import Claim, SourceSpan

router = APIRouter(prefix="/api/v1/claims", tags=["Claims"])

@router.get("/{claim_id}", response_model=Claim)
async def get_claim_lineage(
    claim_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user)
) -> Claim:
    """Fetch exact verbatim claim lineages on hover."""
    
    stmt = select(ClaimRecord).where(ClaimRecord.id == str(claim_id))
    result = await db.execute(stmt)
    claim_record = result.scalar_one_or_none()
    
    if not claim_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found."
        )
        
    source_span = None
    if claim_record.document_id and claim_record.span_start is not None and claim_record.span_end is not None and claim_record.span_text:
        source_span = SourceSpan(
            document_id=uuid.UUID(claim_record.document_id),
            start_index=claim_record.span_start,
            end_index=claim_record.span_end,
            text=claim_record.span_text
        )
        
    return Claim(
        claim_text=claim_record.claim_text,
        skill_ids=claim_record.skill_ids,
        source_type=claim_record.source_type,
        source_span=source_span,
        evidence_tier=claim_record.evidence_tier,
        observed_date=claim_record.created_at,
        recency_factor=1.0,
        tier_rule=claim_record.tier_rule
    )
