from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_user_repo
from app.schemas.auth import Token, LoginRequest, UserCreate, UserResponse
from app.core.security import create_access_token
from app.core.exceptions import AuthenticationException, DuplicateException

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    repo = await get_user_repo(db)
    user = await repo.authenticate(request.username, request.password)
    if not user:
        raise AuthenticationException(detail="Invalid username or password")
    token = create_access_token({"sub": user.username, "id": user.id})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    repo = await get_user_repo(db)
    existing = await repo.get_by_username(user_data.username)
    if existing:
        raise DuplicateException("User", "username", user_data.username)
    existing_email = await repo.get_by_email(user_data.email)
    if existing_email:
        raise DuplicateException("User", "email", user_data.email)
    user = await repo.create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
    )
    return user
