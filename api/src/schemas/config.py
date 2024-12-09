from typing import List, Optional, Literal

from pydantic import BaseModel


# Shared properties
class ConfigBase(BaseModel):
    proxy_url: Optional[str] = None
    telegraph_token: Optional[str] = None
    openai_api_key: Optional[str] = None
    openai_model: Optional[str] = None
    openai_max_tokens: Optional[int] = None
    openai_temperature: Optional[float] = None
    openai_prompt: Optional[str] = None


# Properties to receive on item creation
class ConfigCreate(ConfigBase):
   pass

# Properties to receive on item update
class ConfigUpdate(ConfigBase):
    proxy_url: str
    telegraph_token: str
    openai_api_key: str
    openai_model: Literal[
        'gpt-4o', 'gpt-4o-mini', 'o1-preview', 'o1-mini', 'gpt-3.5-turbo']
    openai_max_tokens: int
    openai_temperature: float
    openai_prompt: str


# Properties shared by models stored in DB
class ConfigInDBBase(ConfigBase):
    pass

    class Config:
        from_attributes = True


# Properties to return to client
class Config(ConfigInDBBase):
    pass


# Additional properties stored in DB
class ConfigInDB(ConfigInDBBase):
    pass


# List of items to return via API
class ConfigRows(BaseModel):
    data: List[Config]
    total: int
