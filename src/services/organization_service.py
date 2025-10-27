import typing

import fastapi

from src import schemas
from src.repositories import OrganizationRepositoryDep


class OrganizationService:
    def __init__(self, repo: OrganizationRepositoryDep) -> None:
        self._repo = repo

    async def get_by_building(self, building_id: int, *, limit: int = 10, offset: int = 0) -> schemas.ListOrganizations:
        return await self._repo.get_by_building_id(building_id=building_id, limit=limit, offset=offset)

    async def get_by_building_address(
        self, address: str, *, limit: int = 10, offset: int = 0
    ) -> schemas.ListOrganizations:
        return await self._repo.get_by_building_address(address=address, limit=limit, offset=offset)

    async def get_by_specializations(
        self, specs: list[int], *, limit: int = 10, offset: int = 0
    ) -> schemas.ListOrganizations:
        return await self._repo.get_by_specializations(specs=specs, limit=limit, offset=offset)

    async def get_by_building_location_radius(
        self,
        longitude: float,
        latitude: float,
        radius_m: int,
        *,
        limit: int = 10,
        offset: int = 10,
    ) -> schemas.ListOrganizations:
        return await self._repo.get_by_building_location_radius(
            longitude=longitude,
            latitude=latitude,
            radius_m=radius_m,
            limit=limit,
            offset=offset,
        )

    async def get_by_building_location_box(
        self,
        ll_longitude: float,
        ll_latitude: float,
        ur_longitude: float,
        ur_latitude: float,
        *,
        limit: int = 10,
        offset: int = 10,
    ) -> schemas.ListOrganizations:
        return await self._repo.get_by_building_location_box(
            ll_longitude=ll_longitude,
            ll_latitude=ll_latitude,
            ur_longitude=ur_longitude,
            ur_latitude=ur_latitude,
            limit=limit,
            offset=offset,
        )

    async def get_by_id(self, organization_id: int) -> schemas.Organization:
        res = await self._repo.get_by_id(organization_id=organization_id)
        if res is None:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_404_NOT_FOUND,
                detail=f'Organization (id={organization_id}) not found',
            )
        return res

    async def get_by_name(self, name: str, *, limit: int = 10, offset: int = 0) -> schemas.ListOrganizations:
        return await self._repo.get_by_name(name=name, limit=limit, offset=offset)


OrganizationServiceDep = typing.Annotated[OrganizationService, fastapi.Depends(OrganizationService)]
