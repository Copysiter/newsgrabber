from enum import Enum


class Status(Enum):
    NEW = 'NEW'
    IN_PROGRESS = 'IN_PROGRESS'
    DONE = 'DONE'
    FAILED = 'FAILED'