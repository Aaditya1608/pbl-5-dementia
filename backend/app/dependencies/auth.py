from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.models.revoked_tokens import RevokedTokens

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    jti = payload.get("jti")

    if not jti:
        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )
    revoked_token = db.query(RevokedTokens).filter(
        RevokedTokens.token_jti == jti
    ).first()

    if revoked_token:
        raise HTTPException(
            status_code=401,
            detail="Token has been revoked"
    )

    user_id = payload.get("sub")

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user

def require_role(required_role: str):

    def role_checker(
        current_user: User = Depends(get_current_user)
    ):

        if current_user.role.value != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this resource"
            )

        return current_user

    return role_checker