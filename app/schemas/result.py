"""Result and Pipeline status schemas."""

import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel

__all__ = ["Result", "PipelineInput", "PipelineStatus"]
class GapAction(BaseModel):
    action_title: str
    effort_hours_est: int
    score_gain_est: int
    remediation_link: str | None = None

class Result(BaseModel):
    """Final result of the pipeline evaluation."""
    model_config = {"frozen": True, "extra": "ignore"}
    
    profile_run_id: str | None = None
    status: str | None = None
    run_id: uuid.UUID | None = None
    readiness_score: float = 0.0
    dimension_scores: dict[str, float] = {}
    blocking_items: list[str] = []
    generated_assets: dict[str, Any] = {}
    provenance_metrics: dict[str, int] = {}
    generation_incomplete: bool = False
    overview_blocked_by_evidence_tier: bool = False
    gap_actions: list[GapAction] = []
    claims: list[Any] | None = None
    scores: Any | None = None
    gaps: list[Any] | None = None
    skill_gaps: list[Any] | None = None
    draft_asset: Any | None = None
    created_at: datetime | None = None

class PipelineInput(BaseModel):
    """Input payload for a pipeline execution."""
    model_config = {"extra": "ignore"}
    cv_text: str | None = None
    cv_pdf_bytes: bytes | None = None
    cv_pdf_path: str | None = None
    github_data: dict[str, Any] | None = None
    github_url: str | None = None
    upwork_text: str | None = None
    upwork_url: str | None = None
    rate_desired: float | None = None
    niche: str | None = None
    version: str | None = None
    claims: list[Any] | None = None

class PipelineStatus(BaseModel):
    """Status update for an executing pipeline."""
    model_config = {"extra": "ignore"}
    run_id: uuid.UUID | None = None
    profile_run_id: str | None = None
    stage: str | None = None
    stage_index: int = 0
    total_stages: int = 6
    progress_pct: float = 0.0
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error: str | None = None
    status: str = "pending"