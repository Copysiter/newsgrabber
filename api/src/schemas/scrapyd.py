from pydantic import BaseModel


class ScrapydRequest(BaseModel):
    url: str
    spider_name: str