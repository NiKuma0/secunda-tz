
from sqlalchemy import orm

from .base import Base


class Building(Base):
    __tablename__ = 'buildings'

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    address: orm.Mapped[str]
    longitude: orm.Mapped[float]
    latitude: orm.Mapped[float]
