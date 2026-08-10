"""Opportunity Matching schemas."""

import uuid
from typing import List
from pydantic import BaseModel, Field

class OpportunityInput(BaseModel):
    source_url: str | None = None
    raw_text: str | None = None
    client_name: str | None = None
    rate_offered: float | None = None
    timezone_req: str | None = None

class ParsedOpportunity(OpportunityInput):
    """Structured fields extracted by the LLM."""
    model_config = {"frozen": True}

    id: uuid.UUID | None = Field(default=None, description="The DB ID of the opportunity")
    required_skills: List[str] = Field(default_factory=list, description="Extracted required skills")
    industry_vertical: str = Field(..., description="Target industry vertical")
    budget_tier: str = Field(..., description="High, Medium, or Low based on market rates")
    estimated_effort_hours: float = Field(..., description="Estimated total hours required")

class FactorScores(BaseModel):
    skill_fit: float       # 40%
    evidence_quality: float # 20%
    industry_fit: float    # 20%
    timezone_fit: float    # 10%
    budget_fit: float      # 10%

class ReqIntersection(BaseModel):
    requirement: str
    verified_proof: str | None = None
    unverified_proof: str | None = None
    is_missing: bool = False

class OpportunityMatchScore(BaseModel):
    overall_match_score: float
    factors: FactorScores
    requirements_grid: list[ReqIntersection]

class ProposalDraft(BaseModel):
    raw_xml: str
    publishable: bool
    retained_claims: List[uuid.UUID]
    skill_gaps: List[str]