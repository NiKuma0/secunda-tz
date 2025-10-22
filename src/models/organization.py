from sqlalchemy import orm

from .base import Base


class Organization(Base):
    __tablename__ = 'organizations'

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    name: orm.Mapped[str]
    phone: orm.Mapped[str]
