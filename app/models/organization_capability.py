"""SQLAlchemy ORM tables for Organization Teaming Engine."""
from sqlalchemy import String, Boolean, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDMixin, TimestampMixin

class Organization(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "organizations"
    
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=True)
    website_url: Mapped[str] = mapped_column(String(255), nullable=True)
    
    members: Mapped[list["OrganizationMember"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    pods: Mapped[list["TeamPod"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    invites: Mapped[list["OrgMemberInvite"]] = relationship(back_populates="organization", cascade="all, delete-orphan")

class OrgMemberInvite(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "org_member_invites"

    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"))
    email: Mapped[str] = mapped_column(String(255), index=True)
    token: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    role: Mapped[str] = mapped_column(String(64), default="professional")
    is_exclusive: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(64), default="pending")
    expires_at: Mapped[float] = mapped_column(Float) # Timestamp
    
    organization: Mapped["Organization"] = relationship(back_populates="invites")

class OrganizationMember(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "organization_members"
    
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    
    consent_given: Mapped[bool] = mapped_column(Boolean, default=False)
    is_exclusive: Mapped[bool] = mapped_column(Boolean, default=True)
    availability_capacity_percentage: Mapped[float] = mapped_column(Float, default=100.0)
    
    organization: Mapped["Organization"] = relationship(back_populates="members")

class TeamPod(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "team_pods"
    
    organization_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=True)
    niche_target: Mapped[str] = mapped_column(String(128))
    compatibility_score: Mapped[float] = mapped_column(Float)
    name: Mapped[str] = mapped_column(String(128), default="Unnamed Pod")
    
    organization: Mapped["Organization | None"] = relationship(back_populates="pods")
    assignments: Mapped[list["PodMemberAssignment"]] = relationship(back_populates="pod", cascade="all, delete-orphan")

class PodMemberAssignment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "pod_member_assignments"
    
    pod_id: Mapped[str] = mapped_column(String(36), ForeignKey("team_pods.id"))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    assigned_role: Mapped[str] = mapped_column(String(64))
    allocated_hours_per_week: Mapped[float] = mapped_column(Float)
    
    pod: Mapped["TeamPod"] = relationship(back_populates="assignments")