from typing import TYPE_CHECKING
from enum import Enum as PyEnum
from datetime import datetime

from sqlalchemy import (
    Column, ForeignKey, Integer, String, Text, DateTime, Enum
)  # noqa
from sqlalchemy.orm import relationship

from db.base_class import Base  # noqa

from schemas.status import Status

if TYPE_CHECKING:
    from .user import User  # noqa: F401


class Item(Base):
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, nullable=False)
    job_id = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    title = Column(String, nullable=True)
    text = Column(Text, nullable=True)
    html = Column(Text, nullable=True)
    telegraph_url = Column(String, nullable=True)
    tags = Column(String, nullable=True)
    status = Column(Enum(Status), default=Status.NEW)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship('User', back_populates='items', lazy='joined')
