from crud.base import CRUDBase  # noqa
from models.config import Config  # noqa
from schemas.config import ConfigCreate, ConfigUpdate  # noqa


class CRUDConfig(CRUDBase[Config, ConfigCreate, ConfigUpdate]):
    pass


config = CRUDConfig(Config)
