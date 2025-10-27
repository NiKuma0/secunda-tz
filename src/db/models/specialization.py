import sqlalchemy as sa
from sqlalchemy import orm

from .base import Base


class Specialization(Base):
    __tablename__ = 'specializations'

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    name: orm.Mapped[str] = orm.mapped_column(sa.String(128), nullable=False)

    parent_id: orm.Mapped[int | None] = orm.mapped_column(sa.ForeignKey('specializations.id'), nullable=True)

    parent: orm.Mapped['Specialization | None'] = orm.relationship(
        back_populates='children',
        remote_side='Specialization.id',
    )
    children: orm.Mapped[list['Specialization']] = orm.relationship(
        back_populates='parent',
        cascade='all, delete-orphan',
    )
