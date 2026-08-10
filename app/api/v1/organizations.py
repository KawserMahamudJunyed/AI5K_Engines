import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.deps import get_current_user, require_permission
from app.schemas.organization_capability import (
    OrgCapabilityResult, PodRequirementInput, TeamPodDraft,
    OrganizationCreate, OrganizationResponse, InviteRequest, InviteAcceptRequest, InviteResponse
)
from app.services.org_scorer import calculate_org_capability_score
from app.services.pod_builder import assemble_pod_for_opportunity
from app.services.org_onboarding import create_organization, generate_invite_token, accept_invitation
from app.services.audit import write_audit_log
from app.models.identity import User

router = APIRouter(prefix="/api/v1/organizations", tags=["Organization Capability"])

@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def register_organization(
    org_input: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user)
) -> OrganizationResponse:
    org = await create_organization(db, org_input, user_id)
    await db.commit()
    await db.refresh(org)
    return OrganizationResponse(
        id=uuid.UUID(org.id),
        name=org.name,
        slug=org.slug,
        website_url=org.website_url
    )

@router.post("/{org_id}/invites", response_model=InviteResponse, status_code=status.HTTP_201_CREATED)
async def create_invite(
    org_id: uuid.UUID,
    invite_input: InviteRequest,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(require_permission("organization:manage"))
) -> InviteResponse:
    invite = await generate_invite_token(db, org_id, invite_input)
    await db.commit()
    await db.refresh(invite)
    return InviteResponse(
        id=uuid.UUID(invite.id),
        organization_id=uuid.UUID(invite.organization_id),
        email=invite.email,
        role=invite.role,
        is_exclusive=invite.is_exclusive,
        status=invite.status,
        expires_at=invite.expires_at
    )

@router.post("/invites/accept", status_code=status.HTTP_200_OK)
async def accept_invite(
    accept_input: InviteAcceptRequest,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user)
):
    member = await accept_invitation(db, accept_input, user_id)
    await db.commit()
    return {"status": "success", "message": "Invitation accepted."}

@router.get("/{org_id}/capability", response_model=OrgCapabilityResult)
async def get_org_capability(
    org_id: uuid.UUID,
    required_project_hours: float = 40.0,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user)
) -> OrgCapabilityResult:
    result = await calculate_org_capability_score(org_id, required_project_hours, db)
    return result

@router.post("/{org_id}/pod-drafts", response_model=TeamPodDraft)
async def create_pod_draft(
    org_id: uuid.UUID,
    requirements: PodRequirementInput,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user)
) -> TeamPodDraft:
    draft = await assemble_pod_for_opportunity(org_id, requirements, db)
    return draft