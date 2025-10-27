from typing import TYPE_CHECKING

import sqlalchemy.dialects.postgresql as psql
from sqlalchemy import orm

from .base import Base

if TYPE_CHECKING:
    from .building import Building
    from .m2m import OrganizationBuilding
    from .specialization import Specialization


class Organization(Base):
    __tablename__ = 'organizations'

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    name: orm.Mapped[str]
    phone: orm.Mapped[str]

    building_assoc: orm.Mapped['OrganizationBuilding'] = orm.relationship(
        'OrganizationBuilding',
        uselist=False,
        viewonly=True,
    )

    building: orm.Mapped['Building'] = orm.relationship(
        'Building',
        secondary='organization_buildings',
        uselist=False,
        viewonly=True,
    )
    specializations: orm.Mapped[list['Specialization']] = orm.relationship(
        'Specialization',
        secondary='organization_specializations',
        backref='organizations',
        viewonly=True,
    )
    search_vector: orm.Mapped[str] = orm.mapped_column(psql.TSVECTOR, nullable=True)
