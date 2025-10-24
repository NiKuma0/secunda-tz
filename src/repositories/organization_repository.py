import logging
from math import cos, radians

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.asyncio import AsyncSession

from src import models, schemas

logger = logging.getLogger(__name__)

# Earth's radius in kilometers - used for geographic distance calculations
EARTH_RADIUS_KM = 6371.0
# Approximate length of 1 degree of latitude in kilometers
LATITUDE_KM_PER_DEGREE = 111.32


class OrganizationRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    @staticmethod
    def _model_to_schema(model: models.Organization) -> schemas.Organization:
        return schemas.Organization(
            id=model.id,
            name=model.name,
            phone=model.phone,
            building_address=model.building.address,
            building_coordinates=(model.building.latitude, model.building.longitude),
            specializations=[
                schemas.Specialization(id=spec.id, name=spec.name, parent_id=spec.parent_id)
                for spec in model.specializations
            ],
        )

    async def get_by_id(self, _id: int) -> schemas.Organization | None:
        query = (
            sa.select(models.Organization)
            .options(
                orm.joinedload(models.Organization.building),
                orm.joinedload(models.Organization.specializations),
            )
            .where(models.Organization.id == _id)
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
        return schemas.ListOrganizations(
            organizations=list(map(self._model_to_schema, organizations))
        )

    async def get_by_specialization(
        self,
        spec_ids: list[int],
        limit: int = 10,
        offset: int = 0,
    ) -> schemas.ListOrganizations:
        query = (
            sa.select(models.Organization)
            .join(models.OrganizationSpecializations)
            .where(models.OrganizationSpecializations.specialization_id.in_(spec_ids))
            .group_by(models.Organization.id)
            # Having count(distinct specialization_id) = len(spec_ids) ensures
            # the organization has ALL requested specializations
            .having(
                sa.func.count(sa.distinct(
                    models.OrganizationSpecializations.specialization_id
                )) == len(spec_ids)
            )
            .options(
                orm.joinedload(models.Organization.building),
                orm.joinedload(models.Organization.specializations),
            )
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.scalars(query)
        organizations = result.all()
        return schemas.ListOrganizations(
            organizations=list(map(self._model_to_schema, organizations))
        )

    async def get_by_radius(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
        *,
        limit: int = 10,
        offset: int = 0,
    ) -> schemas.ListOrganizations:
        """Find organizations within a radius of a point using Haversine formula.

        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            radius_km: Search radius in kilometers
            limit: Max results to return
            offset: Number of results to skip

        Returns:
            ListOrganizations: Organizations within the specified radius

        """
        # Circle search using Haversine formula
        # acos(sin(lat1)sin(lat2) + cos(lat1)cos(lat2)cos(lon2-lon1)) * R
        # where R is Earth's radius
        query = (
            sa.select(models.Organization)
            .join(models.OrganizationBuilding)
            .join(models.Building)
            .where(
                sa.func.acos(
                    sa.func.sin(sa.func.radians(latitude)) *
                    sa.func.sin(sa.func.radians(models.Building.latitude)) +
                    sa.func.cos(sa.func.radians(latitude)) *
                    sa.func.cos(sa.func.radians(models.Building.latitude)) *
                    sa.func.cos(
                        sa.func.radians(models.Building.longitude - longitude)
                    )
                ) * EARTH_RADIUS_KM <= radius_km
            )
            .options(
                orm.joinedload(models.Organization.building),
                orm.joinedload(models.Organization.specializations),
            )
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.scalars(query)
        organizations = result.all()
        return schemas.ListOrganizations(
            organizations=list(map(self._model_to_schema, organizations))
        )

    async def get_by_box(
        self,
        latitude: float,
        longitude: float,
        box_width_km: float,
        box_height_km: float,
        *,
        limit: int = 10,
        offset: int = 0,
    ) -> schemas.ListOrganizations:
        """Find organizations within a rectangular bounding box around a point.

        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            box_width_km: Box width in kilometers
            box_height_km: Box height in kilometers
            limit: Max results to return
            offset: Number of results to skip

        Returns:
            ListOrganizations: Organizations within the bounding box

        """
        # Convert km to approximate degrees at the given latitude
        # Length of 1° of latitude = ~111.32 km (near constant)
        # Length of 1° of longitude varies with latitude: 111.32 * cos(lat) km
        lat_delta = box_height_km / (2 * LATITUDE_KM_PER_DEGREE)
        lon_delta = box_width_km / (2 * LATITUDE_KM_PER_DEGREE * cos(radians(latitude)))

        # Rectangle search using simple bounds on lat/lon
        query = (
            sa.select(models.Organization)
            .join(models.OrganizationBuilding)
            .join(models.Building)
            .where(
                models.Building.latitude.between(latitude - lat_delta, latitude + lat_delta),
                models.Building.longitude.between(longitude - lon_delta, longitude + lon_delta),
            )
            .options(
                orm.joinedload(models.Organization.building),
                orm.joinedload(models.Organization.specializations),
            )
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.scalars(query)
        organizations = result.all()
        return schemas.ListOrganizations(
            organizations=list(map(self._model_to_schema, organizations))
        )

    async def get_by_location(
        self,
        latitude: float,
        longitude: float,
        *,
        radius_km: float | None = None,
        box_width_km: float | None = None,
        box_height_km: float | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> schemas.ListOrganizations:
        """Find organizations within a radius or bounding box of a point.

        This is a convenience method that combines get_by_radius and get_by_box.

        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            radius_km: Search radius in kilometers (circle search)
            box_width_km: Box width in kilometers (rectangle search)
            box_height_km: Box height in kilometers (rectangle search)
            limit: Max results to return
            offset: Number of results to skip

        Returns:
            ListOrganizations: Organizations within the specified area

        Raises:
            ValueError: If neither radius nor box dimensions are provided,
                      or if both are provided simultaneously.

        """
        if radius_km is not None and (box_width_km is not None or box_height_km is not None):
            msg = 'Specify either radius OR box dimensions, not both'
            raise ValueError(msg)

        if radius_km is not None:
            return await self.get_by_radius(
                latitude, longitude, radius_km, limit=limit, offset=offset
            )

        if box_width_km is not None and box_height_km is not None:
            return await self.get_by_box(
                latitude, longitude, box_width_km, box_height_km,
                limit=limit, offset=offset
            )

        msg = 'Must specify either radius_km or both box dimensions'
        raise ValueError(msg)

