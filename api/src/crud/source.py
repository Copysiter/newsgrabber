from crud.base import CRUDBase  # noqa
from models.source import Source  # noqa
from schemas.source import SourceCreate, SourceUpdate  # noqa


class CRUDSource(CRUDBase[Source, SourceCreate, SourceUpdate]):
    pass


source = CRUDSource(Source)
