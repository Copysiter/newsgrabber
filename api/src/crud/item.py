from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase  # noqa
from models.item import Item  # noqa
from schemas.item import ItemCreate, ItemUpdate  # noqa


class CRUDItem(CRUDBase[Item, ItemCreate, ItemUpdate]):
    async def create_with_user(
        self, db: AsyncSession, *, obj_in: ItemCreate, user_id: int
    ) -> Item:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, user_id=user_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_rows_by_user(
        self, db: AsyncSession, *, user_id: int,
        skip: int = 0, limit: int = 100
    ) -> List[Item]:
        statement = (select(self.model).
                     where(self.model.user_id == user_id).
                     offset(skip).
                     limit(limit))
        results = await db.execute(statement=statement)
        return results.scalars().all()

    async def get_count_by_user(
        self, db: AsyncSession, *, user_id: int
    ) -> int:
        statement = (select(func.count(self.model.id)).
                     where(self.model.user_id == user_id))
        results = await db.execute(statement=statement)
        return results.scalar_one()

    async def get_by_url(
        self, db: AsyncSession, *, url: str
    ) -> Optional[Item]:
        statement = select(Item).where(Item.url == url)
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def get_by_job_id(
        self, db: AsyncSession, *, job_id: str
    ) -> Optional[Item]:
        statement = select(Item).where(Item.job_id == job_id)
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()


item = CRUDItem(Item)
