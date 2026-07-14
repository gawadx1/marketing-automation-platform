from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from app.repositories.base import BaseRepository
from app.models.contact import Contact
from app.models.lead_event import LeadEvent


class ContactRepository(BaseRepository[Contact]):
    def __init__(self, db: AsyncSession):
        super().__init__(Contact, db)

    async def get_by_email(self, email: str):
        result = await self.db.execute(select(Contact).where(Contact.email == email))
        return result.scalar_one_or_none()

    async def search(self, query_str: str, skip: int = 0, limit: int = 100) -> tuple:
        query = select(Contact).where(
            or_(
                Contact.email.ilike(f"%{query_str}%"),
                Contact.first_name.ilike(f"%{query_str}%"),
                Contact.last_name.ilike(f"%{query_str}%"),
                Contact.company.ilike(f"%{query_str}%"),
            )
        )
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query)

        query = query.offset(skip).limit(limit).order_by(Contact.created_at.desc())
        result = await self.db.execute(query)
        items = list(result.scalars().all())
        return items, total or 0


class LeadEventRepository(BaseRepository[LeadEvent]):
    def __init__(self, db: AsyncSession):
        super().__init__(LeadEvent, db)
