import geoalchemy2 as geosa
import sqlalchemy.dialects.postgresql as psql
from sqlalchemy import orm

from .base import Base


class Building(Base):
    __tablename__ = 'buildings'

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    address: orm.Mapped[str]
    point: orm.Mapped[geosa.WKBElement] = orm.mapped_column(geosa.Geography('POINT', srid=4326))
    search_vector: orm.Mapped[str] = orm.mapped_column(psql.TSVECTOR, nullable=True)
