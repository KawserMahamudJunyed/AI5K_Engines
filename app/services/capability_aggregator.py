"""Service for aggregating member capabilities across an organization."""
import uuid
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.organization_capability import OrganizationMember
from app.models.profile import ProfileRun, ClaimRecord

async def aggregate_organization_claims(org_id: uuid.UUID, db: AsyncSession) -> List[Tuple[ClaimRecord, float, float]]:
    """
    Fetch all verified claims for consenting members of an organization.
    
    Returns:
        List of tuples: (ClaimRecord, exclusivity_weight, availability_percentage)
    """
    stmt = select(OrganizationMember).where(
        OrganizationMember.organization_id == str(org_id),
        OrganizationMember.consent_given == True
    )
    result = await db.execute(stmt)
    members = result.scalars().all()
    
    aggregated_claims = []
    
    for member in members:
        # Fetch the latest ProfileRun for this user
        run_stmt = select(ProfileRun).where(
            ProfileRun.user_id == member.user_id
        ).order_by(ProfileRun.created_at.desc()).limit(1)
        
        run_res = await db.execute(run_stmt)
        latest_run = run_res.scalar_one_or_none()
        
        if not latest_run:
            continue
            
        # Determine weight based on exclusivity
        # Exclusivity & Double-Counting Filter: 1.0 for exclusive, 0.50 for non-exclusive
        weight = 1.0 if member.is_exclusive else 0.50
        
        # Fetch all claims for this ProfileRun
        claim_stmt = select(ClaimRecord).where(
            ClaimRecord.profile_run_id == latest_run.id
        )
        claim_res = await db.execute(claim_stmt)
        claims = claim_res.scalars().all()
        
        for c in claims:
            aggregated_claims.append((c, weight, member.availability_capacity_percentage))
            
    return aggregated_claims
