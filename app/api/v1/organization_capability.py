"""REST Endpoints for Organization Capability and Teaming Engine."""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.deps import get_current_user, require_permission
from app.schemas.organization_capability import OrgCapabilityResult, PodRequirementInput, TeamPodDraft
from app.services.org_scorer import calculate_org_capability_score
from app.services.pod_builder import assemble_pod_for_opportunity
from app.services.audit import write_audit_log

router = APIRouter(prefix="/api/v1/organizations", tags=["Organization Capability"])

@router.get("/{org_id}/capability", response_model=OrgCapabilityResult)
async def get_org_capability(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user)
) -> OrgCapabilityResult:
    """Generates and returns the full OrgCapabilityResult JSON payload."""
    
    # We pass a mocked required_project_hours of 160.0 (e.g. 4 weeks * 40 hours) for MVP endpoint default
    result = await calculate_org_capability_score(org_id, required_project_hours=160.0, db=db)
    
    await write_audit_log(
        actor_id=user_id,
        action="org.capability_calculated",
        entity_type="Organization",
        entity_id=org_id,
        metadata={"overall_score": result.overall_score}
    )
    
    return result

@router.post("/{org_id}/pod", response_model=TeamPodDraft)
async def generate_org_pod(
    org_id: uuid.UUID,
    requirements: PodRequirementInput,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user)
) -> TeamPodDraft:
    """Accepts PodRequirementInput and returns the generated TeamPodDraft proposing the best pod."""
    
    draft = await assemble_pod_for_opportunity(org_id, requirements, db)
    
    await write_audit_log(
        actor_id=user_id,
        action="pod.assembled",
        entity_type="Organization",
        entity_id=org_id,
        metadata={"pod_name": draft.pod_name, "score": draft.team_compatibility_score}
    )
    
    return draft
