import typing

import fastapi

from src import schemas
from src.services import OrganizationServiceDep

router = fastapi.APIRouter()


@router.get('/building/{building_id:int}')
async def get_by_building(
    building_id: int,
    service: OrganizationServiceDep,
    limit: int = 10,
    offset: int = 0,
) -> schemas.ListOrganizations:
    return await service.get_by_building(building_id=building_id, limit=limit, offset=offset)


@router.get('/building')
async def get_by_building_address(
    address: str,
    service: OrganizationServiceDep,
    limit: int = 10,
    offset: int = 0,
) -> schemas.ListOrganizations:
    return await service.get_by_building_address(address=address, limit=limit, offset=offset)


@router.get('/radius')
async def get_by_building_location_radius(
    lon: typing.Annotated[float, fastapi.Query(description='Longitude')],
    lat: typing.Annotated[float, fastapi.Query(description='Latitude')],
    radius_m: typing.Annotated[int, fastapi.Query(description='Radius of search in meters')],
    service: OrganizationServiceDep,
    limit: int = 10,
    offset: int = 0,
) -> schemas.ListOrganizations:
    """Get organizations by its location in area."""
    return await service.get_by_building_location_radius(
        latitude=lat, longitude=lon, radius_m=radius_m, limit=limit, offset=offset
    )


@router.get('/box')
async def get_by_building_location_box(
    ll_lon: typing.Annotated[float, fastapi.Query(description='Low left longitude')],
    ll_lat: typing.Annotated[float, fastapi.Query(description='Low left latitude')],
    ur_lon: typing.Annotated[float, fastapi.Query(description='Upper right longitude')],
    ur_lat: typing.Annotated[float, fastapi.Query(description='Upper right latitude')],
    service: OrganizationServiceDep,
    limit: int = 10,
    offset: int = 0,
) -> schemas.ListOrganizations:
    """Get organizations by its location in box area."""
    return await service.get_by_building_location_box(
        ll_longitude=ll_lon,
        ll_latitude=ll_lat,
        ur_longitude=ur_lon,
        ur_latitude=ur_lat,
        limit=limit,
        offset=offset,
    )


@router.get('/specs', operation_id='get_by_specializations')
async def get_by_specializations(
    specs: typing.Annotated[list[int], fastapi.Query(description='Ids of specializations')],
    service: OrganizationServiceDep,
    limit: int = 10,
    offset: int = 0,
) -> schemas.ListOrganizations:
    return await service.get_by_specializations(specs=specs, limit=limit, offset=offset)


@router.get('/{organization_id:int}')
async def get_organization(organization_id: int, service: OrganizationServiceDep) -> schemas.Organization:
    return await service.get_by_id(organization_id=organization_id)


@router.get('')
async def get_by_name(
    name: str,
    service: OrganizationServiceDep,
    limit: int = 10,
    offset: int = 0,
) -> schemas.ListOrganizations:
    return await service.get_by_name(name=name, limit=limit, offset=offset)
