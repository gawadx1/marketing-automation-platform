from typing import Generic, TypeVar, Type, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from sqlalchemy.sql import Select
from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def create(self, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        self.db.add(instance)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def get(self, id: int) -> Optional[ModelType]:
        result = await self.db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict] = None,
        order_by: Optional[str] = None,
        descending: bool = True,
    ) -> tuple[list[ModelType], int]:
        query = select(self.model)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    column = getattr(self.model, field)
                    query = query.where(column == value)

        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query)

        if order_by and hasattr(self.model, order_by):
            column = getattr(self.model, order_by)
            query = query.order_by(column.desc() if descending else column.asc())

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        items = list(result.scalars().all())
        return items, total or 0

    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        instance = await self.get(id)
        if not instance:
            return None
        for key, value in kwargs.items():
            if value is not None and hasattr(instance, key):
                setattr(instance, key, value)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def delete(self, id: int) -> bool:
        instance = await self.get(id)
        if not instance:
            return False
        await self.db.delete(instance)
        await self.db.flush()
        return True

    async def count(self, filters: Optional[dict] = None) -> int:
        query = select(func.count()).select_from(self.model)
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.where(getattr(self.model, field) == value)
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def execute_raw(self, stmt: str, params: Optional[dict] = None):
        result = await self.db.execute(text(stmt), params or {})
        return result
