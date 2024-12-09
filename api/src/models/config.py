from sqlalchemy import Column, Integer, Float, String, Text # noqa

from db.base_class import Base  # noqa


class Config(Base):
    id = Column(Integer, primary_key=True, index=True)
    proxy_url = Column(String)
    telegraph_token = Column(String)
    openai_api_key = Column(String)
    openai_model = Column(String, nullable=False, default='gpt-4o')
    openai_max_tokens = Column(Integer, nullable=False, default=500)
    openai_temperature = Column(Float, nullable=False, default=0.7)
    openai_prompt = Column(Text)
