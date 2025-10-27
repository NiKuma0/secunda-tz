import typing

import fastapi
import sqlalchemy as sa
from geoalchemy2 import Geography
from geoalchemy2.shape import to_shape
from sqlalchemy import orm

from src import schemas
from src.db import SessionDep, models

if typing.TYPE_CHECKING:
    from shapely import Point


class OrganizationRepository:
    def __init__(self, session: SessionDep):
        self._session = session

    @staticmethod
    def _model_to_schema(model: models.Organization) -> schemas.Organization:
        coords = typing.cast('Point', to_shape(model.building.point))
        return schemas.Organization(
            id=model.id,
            name=model.name,
            phone=model.phone,
            building_id=model.building.id,
            building_address=model.building.address,
            building_coordinates=(coords.x, coords.y),
            specializations=[
                schemas.Specialization(id=spec.id, name=spec.name, parent_id=spec.parent_id)
                for spec in model.specializations
            ],
        )

    async def get_by_id(self, organization_id: int) -> schemas.Organization | None:
        query = (
            sa.select(models.Organization)
            .options(
                orm.joinedload(models.Organization.building),
                orm.joinedload(models.Organization.specializations),
            )
            .where(models.Organization.id == organization_id)
            .limit(1)
        )
        result = await self._session.scalar(query)
        if result is None:
            return None
        return self._model_to_schema(result)

    async def get_by_building_address(
        self,
        address: str,
        limit: int = 10,
        offset: int = 0,
    ) -> schemas.ListOrganizations:
        query = (
            sa.select(models.Organization)
            .options(
                orm.joinedload(models.Organization.building),
                orm.joinedload(models.Organization.specializations),
            )
            .where(models.Building.address == address)
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.scalars(query)
        organizations = result.unique().all()
        return schemas.ListOrganizations(organizations=list(map(self._model_to_schema, organizations)))

    async def get_by_building_id(
        self,
        building_id: int,
        limit: int = 10,
        offset: int = 0,
    ) -> schemas.ListOrganizations:
        query = (
            sa.select(models.Organization)
            .options(
                orm.joinedload(models.Organization.building),
                orm.joinedload(models.Organization.specializations),
            )
            .where(models.Building.id == building_id)
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.scalars(query)
        organizations = result.unique().all()
        return schemas.ListOrganizations(organizations=list(map(self._model_to_schema, organizations)))

    async def get_by_specializations(
        self,
        specs: list[int],
        limit: int = 10,
        offset: int = 0,
    ) -> schemas.ListOrganizations:
        query = (
            sa.select(models.Organization)
            .join(models.OrganizationSpecializations)
            .where(models.OrganizationSpecializations.specialization_id.in_(specs))
            .group_by(models.Organization.id)
            # Having count(distinct specialization_id) = len(spec_ids) ensures
            # the organization has ALL requested specializations
            .having(sa.func.count(sa.distinct(models.OrganizationSpecializations.specialization_id)) == len(specs))
            .options(
                orm.joinedload(models.Organization.building),
                orm.joinedload(models.Organization.specializations),
            )
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.scalars(query)
        organizations = result.all()
        return schemas.ListOrganizations(organizations=list(map(self._model_to_schema, organizations)))

    async def get_by_building_location_radius(
        self,
        latitude: float,
        longitude: float,
        radius_m: int,
        *,
        limit: int = 10,
        offset: int = 0,
    ) -> schemas.ListOrganizations:
        """Find organizations within a radius of a point using Haversine formula.

        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            radius_m: Search radius in meters
            limit: Max results to return
            offset: Number of results to skip

        Returns:
            ListOrganizations: Organizations within the specified radius

        """
        query = (
            sa.select(models.Organization)
            .join(models.OrganizationBuilding)
            .join(models.Building)
            .where(
                sa.func.ST_DWithin(
                    models.Building.point,
                    sa.func.ST_Point(longitude, latitude, 4326).cast(Geography('POINT')),
                    radius_m,
                )
            )
            .options(
                orm.joinedload(models.Organization.building),
                orm.joinedload(models.Organization.specializations),
            )
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.scalars(query)
        organizations = result.unique().all()
        return schemas.ListOrganizations(organizations=list(map(self._model_to_schema, organizations)))

    async def get_by_building_location_box(
        self,
        ll_latitude: float,
        ll_longitude: float,
        ur_latitude: float,
        ur_longitude: float,
        *,
        limit: int = 10,
        offset: int = 0,
    ) -> schemas.ListOrganizations:
        """Find organizations within a rectangular bounding box around a point.

        Args:
            ll_latitude: Low left point latitude
            ll_longitude: Low left point longitude
            ur_latitude: Upper right point latitude
            ur_longitude: Upper right point longitude
            limit: Max results to return
            offset: Number of results to skip

        Returns:
            ListOrganizations: Organizations within the bounding box

        """
        query = (
            sa.select(models.Organization)
            .join(models.OrganizationBuilding)
            .join(models.Building)
            .where(
                sa.func.ST_DWithin(
                    models.Building.point,
                    sa.func.ST_MakeEnvelope(
                        ll_longitude,
                        ll_latitude,
                        ur_longitude,
                        ur_latitude,
                        4326,
                    ).cast(Geography('polygon')),
                    0,
                )
            )
            .options(
                orm.joinedload(models.Organization.building),
                orm.joinedload(models.Organization.specializations),
            )
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.scalars(query)
        organizations = result.unique().all()
        return schemas.ListOrganizations(organizations=list(map(self._model_to_schema, organizations)))

    async def get_by_name(self, name: str, *, limit: int = 10, offset: int = 0) -> schemas.ListOrganizations:
        query = (
            sa.select(models.Organization)
            .where(models.Organization.name == name)
            .options(
                orm.joinedload(models.Organization.building),
                orm.joinedload(models.Organization.specializations),
            )
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.scalars(query)
        organizations = result.unique().all()
        return schemas.ListOrganizations(organizations=list(map(self._model_to_schema, organizations)))


OrganizationRepositoryDep = typing.Annotated[OrganizationRepository, fastapi.Depends(OrganizationRepository)]
