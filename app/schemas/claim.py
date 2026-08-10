"""Claim and SourceSpan schemas."""

from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator, computed_field

__all__ = ["SourceSpan", "Claim"]

class SourceSpan(BaseModel):
    """A specific span of text from a document."""
    model_config = {"frozen": True}
    
    document_id: uuid.UUID
    start_index: int
    end_index: int
    text: str

    @field_validator("text")
    @classmethod
    def _validate_text_length(cls, v: str, info) -> str:
        """Validate that the text length matches the index span."""
        data = info.data
        start_index = data.get("start_index", 0)
        end_index = data.get("end_index", 0)
        expected = end_index - start_index
        if len(v) != expected:
            raise ValueError(
                f"text length {len(v)} != end_index - start_index ({expected})"
            )
        return v

class Claim(BaseModel):
    """An evidence-based claim about a candidate's skills or experience."""
    model_config = {"frozen": True}
    
    claim_text: str
    skill_ids: list[str]
    source_type: str  # "cv", "github", "upwork"
    source_span: Optional[SourceSpan] = None
    evidence_tier: str  # T1-T8
    observed_date: datetime
    recency_factor: float  # 0.0-1.0, decay based on age
    tier_rule: str  # human-readable rule that assigned this tier

    @computed_field
    @property
    def publishable(self) -> bool:
        """Indicates if the claim has a source span and can be published."""
        return self.source_span is not None