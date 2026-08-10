from __future__ import annotations
from sqlalchemy import String, Float, Text, JSON, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from app.models.base import Base, UUIDMixin, TimestampMixin

__all__ = ["ProfileRun", "ClaimRecord", "PipelineLog"]


class ProfileRun(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "profile_runs"

    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    niche: Mapped[str] = mapped_column(String(128))
    version: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), default="pending")
    readiness_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    dimension_scores: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    blocking_items: Mapped[list | None] = mapped_column(JSON, nullable=True)
    generated_assets: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    provenance_metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    claims: Mapped[list[ClaimRecord]] = relationship(back_populates="profile_run", cascade="all, delete-orphan")
    logs: Mapped[list[PipelineLog]] = relationship(back_populates="profile_run", cascade="all, delete-orphan")


class ClaimRecord(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "claim_records"

    profile_run_id: Mapped[str] = mapped_column(String(36), ForeignKey("profile_runs.id"))
    claim_text: Mapped[str] = mapped_column(Text)
    skill_ids: Mapped[list] = mapped_column(JSON)
    source_type: Mapped[str] = mapped_column(String(32))
    evidence_tier: Mapped[str] = mapped_column(String(4))
    tier_rule: Mapped[str] = mapped_column(String(128))
    document_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    span_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    span_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    span_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    publishable: Mapped[bool] = mapped_column(default=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(384), nullable=True)

    profile_run: Mapped[ProfileRun] = relationship(back_populates="claims")


class PipelineLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "pipeline_logs"

    profile_run_id: Mapped[str] = mapped_column(String(36), ForeignKey("profile_runs.id"))
    stage: Mapped[str] = mapped_column(String(64))
    stage_index: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32))
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    profile_run: Mapped[ProfileRun] = relationship(back_populates="logs")