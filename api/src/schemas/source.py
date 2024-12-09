from typing import List, Optional

from pydantic import BaseModel


# Shared properties
class SourceBase(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    spider_name: Optional[str] = None
    proxy_url: Optional[str] = None


# Properties to receive on item creation
class SourceCreate(SourceBase):
    nmae: str
    domain: str
    spider_name: str


# Properties to receive on item update
class SourceUpdate(SourceBase):
    pass


# Properties shared by models stored in DB
class SourceInDBBase(SourceBase):
    id: int

    class Config:
        from_attributes = True


# Properties to return to client
class Source(SourceInDBBase):
    pass


# Additional properties stored in DB
class SourceInDB(SourceInDBBase):
    pass


# List of items to return via API
class SourceRows(BaseModel):
    data: List[Source]
    total: int
