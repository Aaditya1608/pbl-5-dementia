from pwdlib import PasswordHash
import jwt
import uuid
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone

from app.core.config import settings

password_hasher = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hasher.hash(password)

ALGORITHM = "HS256"

def create_access_token(user_id: str, role: str):

    expire = datetime.now(timezone.utc) + timedelta(minutes=30)

    payload = {
        "sub": user_id,
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": str(uuid.uuid4)
    }

    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token

def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            return None

        return payload

    except InvalidTokenError:
        return None