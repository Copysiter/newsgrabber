from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from .user import User
from schemas.status import Status


# Shared properties
class ItemBase(BaseModel):
    source_id: Optional[str] = None
    url: Optional[str] = None
    job_id: Optional[str] = None
    chat_id: Optional[int] = None
    title: Optional[str] = None
    title_ru: Optional[str] = None
    summary: Optional[str] = None
    summary_ru: Optional[str] = None
    text: Optional[str] = None
    text_ru: Optional[str] = None
    html: Optional[str] = None
    html_ru: Optional[str] = None
    telegraph_url: Optional[str] = None
    telegraph_url_ru: Optional[str] = None
    date: Optional[datetime] = None
    status: Optional[Status] = None
    created_at: Optional[datetime] = None


# Properties to receive on item creation
class ItemCreate(ItemBase):
    source_id: int
    url: str


# Properties to receive on item update
class ItemUpdate(ItemBase):
    pass


# Properties shared by models stored in DB
class ItemInDBBase(ItemBase):
    id: int
    title: str
    source_id: int
    user_id: Optional[int]

    class Config:
        from_attributes = True


# Properties to return to client
class Item(ItemInDBBase):
    user: Optional[User]


# Additional properties stored in DB
class ItemInDB(ItemInDBBase):
    pass


# List of items to return via API
class ItemRows(BaseModel):
    data: List[Item]
    total: int
