from sqlalchemy import Column, Integer, String  # noqa

from db.base_class import Base  # noqa


class Source(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    spider_name = Column(String, nullable=False)
    proxy_url = Column(String)
