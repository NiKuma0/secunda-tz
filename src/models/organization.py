from typing import TYPE_CHECKING

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

    # Non-optional association - every organization must have a building
    building_assoc: orm.Mapped['OrganizationBuilding'] = orm.relationship(
        'OrganizationBuilding', uselist=False)

    # Convenience property to get the building directly
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
    )
