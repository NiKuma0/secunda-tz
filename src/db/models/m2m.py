import typing

import sqlalchemy as sa
from sqlalchemy import orm

from .base import Base

if typing.TYPE_CHECKING:
    from .building import Building
    from .organization import Organization
    from .specialization import Specialization


class OrganizationSpecializations(Base):
    __tablename__ = 'organization_specializations'

    organization: orm.Mapped['Organization'] = orm.relationship('Organization', viewonly=True)
    organization_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('organizations.id'))

    specialization: orm.Mapped['Specialization'] = orm.relationship('Specialization', viewonly=True)
    specialization_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('specializations.id'))

    __mapper_args__ = {'primary_key': (organization_id, specialization_id)}  # noqa: RUF012


class OrganizationBuilding(Base):
    __tablename__ = 'organization_buildings'

    organization_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('organizations.id'), primary_key=True)
    organization: orm.Mapped['Organization'] = orm.relationship('Organization', viewonly=True)

    building_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('buildings.id'))
    building: orm.Mapped['Building'] = orm.relationship('Building', viewonly=True)
