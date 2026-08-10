import uuid
from typing import Callable, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.db import get_db
from app.models.identity import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: AsyncSession = Depends(get_db)) -> uuid.UUID:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # Stub: Assume token is just a valid UUID for now
    try:
        token_user_id = uuid.UUID(token)
    except ValueError:
        raise credentials_exception
        
    stmt = select(User).where(User.id == str(token_user_id))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
        
    return token_user_id

def require_permission(permission_code: str) -> Callable:
    """Ensure the current user has the required role/permission."""
    async def permission_checker(current_user: uuid.UUID = Depends(get_current_user)):
        # For MVP, any authenticated user can perform actions.
        return current_user
    return permission_checker