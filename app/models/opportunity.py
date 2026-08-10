"""SQLAlchemy ORM models for Opportunities, Matches, and Proposals."""
from __future__ import annotations

from sqlalchemy import String, Integer, Float, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin

__all__ = ["Opportunity", "OpportunityMatch", "ProposalDraftModel"]


class Opportunity(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "opportunities"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    budget: Mapped[float] = mapped_column(Float, nullable=False)
    timezone_offset: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_duration_weeks: Mapped[int] = mapped_column(Integer, nullable=False)
    source_channel: Mapped[str] = mapped_column(String(100), nullable=False)

    required_skills: Mapped[list[str]] = mapped_column(JSON, default=list)
    industry_vertical: Mapped[str] = mapped_column(String(100), nullable=False)
    budget_tier: Mapped[str] = mapped_column(String(50), nullable=False)
    estimated_effort_hours: Mapped[float] = mapped_column(Float, nullable=False)

    matches: Mapped[list["OpportunityMatch"]] = relationship("OpportunityMatch", back_populates="opportunity", cascade="all, delete-orphan")
    proposals: Mapped[list["ProposalDraftModel"]] = relationship("ProposalDraftModel", back_populates="opportunity", cascade="all, delete-orphan")


class OpportunityMatch(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "opportunity_matches"

    opportunity_id: Mapped[str] = mapped_column(ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    skill_fit: Mapped[float] = mapped_column(Float, nullable=False)
    evidence_quality_fit: Mapped[float] = mapped_column(Float, nullable=False)
    industry_fit: Mapped[float] = mapped_column(Float, nullable=False)
    timezone_fit: Mapped[float] = mapped_column(Float, nullable=False)
    budget_fit: Mapped[float] = mapped_column(Float, nullable=False)

    missing_qualifications: Mapped[list[str]] = mapped_column(JSON, default=list)

    opportunity: Mapped["Opportunity"] = relationship("Opportunity", back_populates="matches")


class ProposalDraftModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "proposal_drafts"

    opportunity_id: Mapped[str] = mapped_column(ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False)
    
    draft_text: Mapped[str] = mapped_column(Text, nullable=False)
    used_claims: Mapped[list[dict]] = mapped_column(JSON, default=list)
    validated: Mapped[bool] = mapped_column(Boolean, default=False)

    opportunity: Mapped["Opportunity"] = relationship("Opportunity", back_populates="proposals")
