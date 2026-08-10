from __future__ import annotations
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr

__all__ = ["Base", "UUIDMixin", "TimestampMixin"]

class Base(DeclarativeBase):
    pass

class UUIDMixin:
    @declared_attr
    def id(cls) -> Mapped[str]:
        return mapped_column(
            String(36),
            primary_key=True,
            default=lambda: str(uuid.uuid4()),
        )

class TimestampMixin:
    @declared_attr
    def created_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            server_default=func.now(),
        )

    @declared_attr
    def updated_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
            server_default=func.now(),
        )