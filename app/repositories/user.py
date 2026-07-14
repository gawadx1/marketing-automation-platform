from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.user import User
from app.core.security import get_password_hash, verify_password


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_username(self, username: str):
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str):
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create_user(
        self, username: str, email: str, password: str, full_name: str = ""
    ):
        hashed = get_password_hash(password)
        return await self.create(
            username=username,
            email=email,
            hashed_password=hashed,
            full_name=full_name,
        )

    async def authenticate(self, username: str, password: str):
        user = await self.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
