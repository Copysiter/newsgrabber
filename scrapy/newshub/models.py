from datetime import datetime

from sqlalchemy import create_engine, Column, ForeignKey, String, Text, Integer, DateTime, Enum
from sqlalchemy.orm import declarative_base, relationship

from enum import Enum as PyEnum

Base = declarative_base()

class Status(PyEnum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    FAILED = "failed"

class Source(Base):
    __tablename__ = 'source'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    spider_name = Column(String, nullable=False)
    proxy_url = Column(String)

class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey('source.id'))
    job_id = Column(String, nullable=True)
    url = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=True)
    title_ru = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    summary_ru = Column(Text, nullable=True)
    text = Column(Text, nullable=True)
    text_ru = Column(Text, nullable=True)
    html = Column(Text, nullable=True)
    html_ru = Column(Text, nullable=True)
    telegraph_url = Column(String, nullable=True)
    telegraph_url_ru = Column(String, nullable=True)
    date = Column(DateTime)
    tags = Column(String, nullable=True)
    status = Column(Enum(Status), default=Status.NEW)
    created_at = Column(DateTime, default=datetime.utcnow)
    source = relationship('Source', lazy='joined')

# Функция для создания таблиц, если их нет
def create_tables(engine):
    Base.metadata.create_all(engine)