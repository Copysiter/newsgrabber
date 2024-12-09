from pydantic import BaseModel


class ScrapydRequest(BaseModel):
    source_name: str
    source_url: str
    spider_name: str