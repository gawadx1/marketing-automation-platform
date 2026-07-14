from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import get_settings
from app.core.exceptions import AuthenticationException

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_PREFIX}/auth/login",
    auto_error=False,
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
    refresh: bool = False,
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS if refresh else settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )
    to_encode.update(
        {
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "iss": settings.JWT_ISSUER,
            "type": "refresh" if refresh else "access",
        }
    )
    return jwt.encode(
        to_encode,
        settings.get_jwt_secret(),
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.get_jwt_secret(),
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.JWT_ISSUER,
        )
        return payload
    except JWTError as exc:
        raise AuthenticationException(detail=f"Invalid or expired token: {str(exc)}")


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)):
    if token is None:
        raise AuthenticationException(detail="Authentication required")
    payload = decode_access_token(token)
    username: str = payload.get("sub")
    user_id: int = payload.get("id")
    token_type: str = payload.get("type", "access")

    if username is None:
        raise AuthenticationException(detail="Invalid token payload")
    if token_type != "access":
        raise AuthenticationException(detail="Refresh token cannot be used for access")

    return {"username": username, "id": user_id}


async def get_optional_user(token: Optional[str] = Depends(oauth2_scheme)):
    if token is None:
        return None
    try:
        return await get_current_user(token)
    except Exception:
        return None
