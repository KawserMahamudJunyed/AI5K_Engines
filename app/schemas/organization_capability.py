"""Frozen Pydantic schemas for Organization Teaming Engine."""
import uuid
from typing import List, Dict
from pydantic import BaseModel, ConfigDict

class OrganizationCreate(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: str
    slug: str | None = None
    website_url: str | None = None

class OrganizationResponse(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: uuid.UUID
    name: str
    slug: str | None
    website_url: str | None

class InviteRequest(BaseModel):
    model_config = ConfigDict(frozen=True)
    email: str
    role_in_org: str = "professional"
    is_exclusive: bool = True

class InviteAcceptRequest(BaseModel):
    model_config = ConfigDict(frozen=True)
    token: str

class InviteResponse(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: uuid.UUID
    organization_id: uuid.UUID
    email: str
    role: str
    is_exclusive: bool
    status: str
    expires_at: float
class SkillStrengthDetail(BaseModel):
    model_config = ConfigDict(frozen=True)
    skill_id: str
    proficiency: float
    evidence_weight: float
    recency_factor: float
    industry_relevance: float
    availability_factor: float
    final_strength: float

class OrgCapabilityResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    organization_id: uuid.UUID
    overall_score: float
    skills_graph: Dict[str, SkillStrengthDetail]
    factors: dict
    penalties_applied: List[str]

class PodRequirementInput(BaseModel):
    model_config = ConfigDict(frozen=True)
    required_roles: List[str]
    target_niche: str
    min_compatibility_threshold: float

class TeamPodDraft(BaseModel):
    model_config = ConfigDict(frozen=True)
    pod_name: str
    members: List[uuid.UUID]
    roles: Dict[uuid.UUID, str]
    team_compatibility_score: float
    factors: dict
