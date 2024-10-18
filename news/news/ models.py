from sqlalchemy import create_engine, Column, String, Text, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, unique=True, nullable=False)
    job_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    html = Column(Text, nullable=False)
    tags = Column(String, nullable=True)
    telegraph_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Функция для создания таблиц, если их нет
def create_tables(engine):
    Base.metadata.create_all(engine)