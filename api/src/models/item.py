from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import (
    Column, ForeignKey, Integer, BigInteger, String, Text, DateTime, Enum
)  # noqa
from sqlalchemy.orm import relationship

from db.base_class import Base  # noqa

from schemas.status import Status

if TYPE_CHECKING:
    from .source import Source  # noqa: F401
    from .user import User  # noqa: F401


class Item(Base):
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey('source.id'))
    job_id = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    chat_id = Column(BigInteger, index=True)
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
    user = relationship('User', back_populates='items', lazy='joined')
