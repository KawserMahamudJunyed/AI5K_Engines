import uuid
import secrets
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from app.models.organization_capability import Organization, OrgMemberInvite, OrganizationMember
from app.models.identity import User, UserRole
from app.schemas.organization_capability import OrganizationCreate, InviteRequest, InviteAcceptRequest
from app.services.audit import write_audit_log

async def create_organization(db: AsyncSession, org_input: OrganizationCreate, creator_id: uuid.UUID) -> Organization:
    org = Organization(
        name=org_input.name,
        slug=org_input.slug,
        website_url=str(org_input.website_url) if org_input.website_url else None
    )
    db.add(org)
    await db.flush()
    
    user_role = UserRole(
        user_id=str(creator_id),
        role_name="org_admin",
        organization_id=org.id
    )
    db.add(user_role)
    await db.flush()
    
    await write_audit_log(
        actor_id=creator_id,
        action="organization.created",
        entity_type="Organization",
        entity_id=uuid.UUID(org.id),
        metadata={"name": org.name}
    )
    
    return org

async def generate_invite_token(db: AsyncSession, org_id: uuid.UUID, invite_input: InviteRequest) -> OrgMemberInvite:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.datetime.now(datetime.timezone.utc).timestamp() + (48 * 3600)
    
    invite = OrgMemberInvite(
        organization_id=str(org_id),
        email=invite_input.email,
        role=invite_input.role,
        is_exclusive=invite_input.is_exclusive,
        token=token,
        expires_at=expires_at,
        status="pending"
    )
    db.add(invite)
    await db.flush()
    return invite

async def accept_invitation(db: AsyncSession, accept_input: InviteAcceptRequest, current_user_id: uuid.UUID) -> OrganizationMember:
    stmt = select(User).where(User.id == str(current_user_id))
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        
    stmt = select(OrgMemberInvite).where(OrgMemberInvite.token == accept_input.token)
    invite = (await db.execute(stmt)).scalar_one_or_none()
    
    if not invite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found.")
        
    if invite.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invite is not pending.")
        
    now = datetime.datetime.now(datetime.timezone.utc).timestamp()
    if now > invite.expires_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token has expired.")
        
    if invite.email.lower() != user.email.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Invite email does not match authenticated user email."
        )
        
    invite.status = "accepted"
    
    member = OrganizationMember(
        organization_id=invite.organization_id,
        user_id=str(user.id),
        consent_given=True,
        is_exclusive=invite.is_exclusive,
        availability_capacity_percentage=100.0
    )
    db.add(member)
    
    user_role = UserRole(
        user_id=str(user.id),
        role_name=invite.role,
        organization_id=invite.organization_id
    )
    db.add(user_role)
    await db.flush()
    
    await write_audit_log(
        actor_id=uuid.UUID(str(user.id)),
        action="organization.member_joined",
        entity_type="Organization",
        entity_id=uuid.UUID(invite.organization_id),
        metadata={"role": invite.role, "exclusive": invite.is_exclusive}
    )
    
    return member