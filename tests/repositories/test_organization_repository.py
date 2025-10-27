import dataclasses
import typing
from collections.abc import Mapping
from unittest import mock

import pytest
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy.ext.asyncio import AsyncSession

from src import models, schemas
from src.repositories import OrganizationRepository


async def fill_db(session: AsyncSession, instances: list[models.Base]):
    session.add_all(instances)
    await session.flush()


class ArgsKwargsProtocol(typing.Protocol):
    @property
    def args(self) -> tuple[typing.Any, ...]: ...
    @property
    def kwargs(self) -> Mapping[str, typing.Any]: ...


@dataclasses.dataclass
class TestCase:
    db_fixtures: list[models.Base]
    call: ArgsKwargsProtocol = dataclasses.field(default_factory=mock.call())

    expected_value: typing.Any = dataclasses.field(default_factory=mock.ANY)


class TestOrganizationRepository:
    @pytest.mark.parametrize(
        'case',
        [
            # Test case 1: Non-existent organization
            TestCase(
                db_fixtures=[],
                call=mock.call(organization_id=1),
                expected_value=None,
            ),
            # Test case 2: Organization with no specializations
            TestCase(
                db_fixtures=[
                    models.Building(id=1, address='456 High St', point=from_shape(Point(40.7128, -74.0060), srid=4326)),
                    models.Organization(id=1, name='Simple Org', phone='+1234567890'),
                    models.OrganizationBuilding(organization_id=1, building_id=1),
                ],
                call=mock.call(organization_id=1),
                expected_value=schemas.Organization(
                    id=1,
                    building_id=1,
                    name='Simple Org',
                    phone='+1234567890',
                    building_address='456 High St',
                    building_coordinates=(40.7128, -74.0060),
                    specializations=[],
                ),
            ),
            # Test case 3: Organization with specializations
            TestCase(
                db_fixtures=[
                    models.Building(id=1, address='456 High St', point=from_shape(Point(40.7128, -74.0060), srid=4326)),
                    models.Organization(id=1, name='Complex Org', phone='+0987654321'),
                    models.OrganizationBuilding(organization_id=1, building_id=1),
                    models.Specialization(id=1, name='Main Spec'),
                    models.Specialization(id=2, name='Sub Spec', parent_id=1),
                    models.OrganizationSpecializations(organization_id=1, specialization_id=1),
                    models.OrganizationSpecializations(organization_id=1, specialization_id=2),
                ],
                call=mock.call(organization_id=1),
                expected_value=schemas.Organization(
                    id=1,
                    building_id=1,
                    name='Complex Org',
                    phone='+0987654321',
                    building_address='456 High St',
                    building_coordinates=(40.7128, -74.0060),
                    specializations=[
                        schemas.Specialization(id=1, name='Main Spec', parent_id=None),
                        schemas.Specialization(id=2, name='Sub Spec', parent_id=1),
                    ],
                ),
            ),
            # Test case 4: Non-sequential ID
            TestCase(
                db_fixtures=[
                    models.Building(
                        id=100, address='789 Park Ave', point=from_shape(Point(35.6762, 139.6503), srid=4326)
                    ),
                    models.Organization(id=50, name='High ID Org', phone='+1122334455'),
                    models.OrganizationBuilding(organization_id=50, building_id=100),
                ],
                call=mock.call(organization_id=50),
                expected_value=schemas.Organization(
                    id=50,
                    building_id=100,
                    name='High ID Org',
                    phone='+1122334455',
                    building_address='789 Park Ave',
                    building_coordinates=(35.6762, 139.6503),
                    specializations=[],
                ),
            ),
            # Test case 5: Invalid ID (negative)
            TestCase(
                db_fixtures=[
                    models.Building(id=1, address='Test St', point=from_shape(Point(0, 0), srid=4326)),
                    models.Organization(id=1, name='Test Org', phone='123'),
                    models.OrganizationBuilding(organization_id=1, building_id=1),
                ],
                call=mock.call(organization_id=-1),
                expected_value=None,
            ),
        ],
    )
    async def test_get_by_id(self, session: AsyncSession, case: TestCase):
        await fill_db(session, case.db_fixtures)
        repo = OrganizationRepository(session=session)

        res = await repo.get_by_id(*case.call.args, **case.call.kwargs)

        assert res == case.expected_value

    @pytest.mark.parametrize(
        'case',
        [
            # Test case 1: Non-existent address
            TestCase(
                db_fixtures=[
                    models.Building(id=1, address='123 Main St', point=from_shape(Point(51.5074, -0.1278), srid=4326)),
                    models.Organization(id=1, name='Test Org', phone='+1234567890'),
                    models.OrganizationBuilding(organization_id=1, building_id=1),
                ],
                call=mock.call(address='456 Missing St'),
                expected_value=schemas.ListOrganizations(organizations=[]),
            ),
            # Test case 2: Single organization at address
            TestCase(
                db_fixtures=[
                    models.Building(id=1, address='123 Main St', point=from_shape(Point(51.5074, -0.1278), srid=4326)),
                    models.Organization(id=1, name='Single Org', phone='+1234567890'),
                    models.OrganizationBuilding(organization_id=1, building_id=1),
                ],
                call=mock.call(address='123 Main St'),
                expected_value=schemas.ListOrganizations(
                    organizations=[
                        schemas.Organization(
                            id=1,
                            name='Single Org',
                            phone='+1234567890',
                            building_address='123 Main St',
                            building_coordinates=(51.5074, -0.1278),
                            building_id=1,
                            specializations=[],
                        ),
                    ]
                ),
            ),
            # Test case 3: Multiple organizations at the same address
            TestCase(
                db_fixtures=[
                    models.Building(id=1, address='456 High St', point=from_shape(Point(40.7128, -74.0060), srid=4326)),
                    models.Organization(id=1, name='First Org', phone='+1111111111'),
                    models.Organization(id=2, name='Second Org', phone='+2222222222'),
                    models.OrganizationBuilding(organization_id=1, building_id=1),
                    models.OrganizationBuilding(organization_id=2, building_id=1),
                    models.Specialization(id=1, name='Shared Spec'),
                    models.OrganizationSpecializations(organization_id=1, specialization_id=1),
                    models.OrganizationSpecializations(organization_id=2, specialization_id=1),
                ],
                call=mock.call(address='456 High St', limit=5),
                expected_value=schemas.ListOrganizations(
                    organizations=[
                        schemas.Organization(
                            id=1,
                            building_id=1,
                            name='First Org',
                            phone='+1111111111',
                            building_address='456 High St',
                            building_coordinates=(40.7128, -74.0060),
                            specializations=[
                                schemas.Specialization(id=1, name='Shared Spec', parent_id=None),
                            ],
                        ),
                        schemas.Organization(
                            id=2,
                            building_id=1,
                            name='Second Org',
                            phone='+2222222222',
                            building_address='456 High St',
                            building_coordinates=(40.7128, -74.0060),
                            specializations=[
                                schemas.Specialization(id=1, name='Shared Spec', parent_id=None),
                            ],
                        ),
                    ]
                ),
            ),
            # Test case 4: Address with special characters
            TestCase(
                db_fixtures=[
                    models.Building(
                        id=1, address="42/3 O'Brien St., #101-A", point=from_shape(Point(35.6762, 139.6503), srid=4326)
                    ),
                    models.Organization(id=1, name='Special Chars Org', phone='+1234567890'),
                    models.OrganizationBuilding(organization_id=1, building_id=1),
                ],
                call=mock.call(address="42/3 O'Brien St., #101-A"),
                expected_value=schemas.ListOrganizations(
                    organizations=[
                        schemas.Organization(
                            id=1,
                            building_id=1,
                            name='Special Chars Org',
                            phone='+1234567890',
                            building_address="42/3 O'Brien St., #101-A",
                            building_coordinates=(35.6762, 139.6503),
                            specializations=[],
                        ),
                    ]
                ),
            ),
            # Test case 5: Pagination test
            TestCase(
                db_fixtures=[
                    models.Building(id=1, address='Shared Address', point=from_shape(Point(0, 0), srid=4326)),
                    models.Organization(id=1, name='Org 1', phone='111'),
                    models.Organization(id=2, name='Org 2', phone='222'),
                    models.Organization(id=3, name='Org 3', phone='333'),
                    models.OrganizationBuilding(organization_id=1, building_id=1),
                    models.OrganizationBuilding(organization_id=2, building_id=1),
                    models.OrganizationBuilding(organization_id=3, building_id=1),
                ],
                call=mock.call(address='Shared Address', limit=2, offset=1),
                expected_value=schemas.ListOrganizations(
                    organizations=[
                        schemas.Organization(
                            id=2,
                            building_id=1,
                            name='Org 2',
                            phone='222',
                            building_address='Shared Address',
                            building_coordinates=(0, 0),
                            specializations=[],
                        ),
                        schemas.Organization(
                            id=3,
                            building_id=1,
                            name='Org 3',
                            phone='333',
                            building_address='Shared Address',
                            building_coordinates=(0, 0),
                            specializations=[],
                        ),
                    ]
                ),
            ),
        ],
    )
    async def test_get_by_building_address(self, session: AsyncSession, case: TestCase):
        await fill_db(session, case.db_fixtures)
        repo = OrganizationRepository(session=session)

        res = await repo.get_by_building_address(*case.call.args, **case.call.kwargs)

        assert res == case.expected_value

    @pytest.mark.parametrize(
        'case',
        [
            # Base case: multiple organizations sharing same building (you already have this)
            TestCase(
                db_fixtures=[
                    models.Building(id=1, address='Shared Address', point=from_shape(Point(0, 0), srid=4326)),
                    models.Organization(id=2, name='Org 2', phone='222'),
                    models.Organization(id=3, name='Org 3', phone='333'),
                    models.OrganizationBuilding(organization_id=2, building_id=1),
                    models.OrganizationBuilding(organization_id=3, building_id=1),
                ],
                call=mock.call(longitude=0, latitude=0, radius_m=1),
                expected_value=schemas.ListOrganizations(
                    organizations=[
                        schemas.Organization(
                            id=2,
                            building_id=1,
                            name='Org 2',
                            phone='222',
                            building_address='Shared Address',
                            building_coordinates=(0, 0),
                            specializations=[],
                        ),
                        schemas.Organization(
                            id=3,
                            building_id=1,
                            name='Org 3',
                            phone='333',
                            building_address='Shared Address',
                            building_coordinates=(0, 0),
                            specializations=[],
                        ),
                    ]
                ),
            ),
            # ✅ Case 1: organization within radius, another one outside
            TestCase(
                db_fixtures=[
                    models.Building(id=1, address='Near', point=from_shape(Point(0.0, 0.0), srid=4326)),
                    models.Building(id=2, address='Far', point=from_shape(Point(100.0, 100.0), srid=4326)),
                    models.Organization(id=1, name='Org Near', phone='111'),
                    models.Organization(id=2, name='Org Far', phone='999'),
                    models.OrganizationBuilding(organization_id=1, building_id=1),
                    models.OrganizationBuilding(organization_id=2, building_id=2),
                ],
                call=mock.call(longitude=0, latitude=0, radius_m=1),
                expected_value=schemas.ListOrganizations(
                    organizations=[
                        schemas.Organization(
                            id=1,
                            building_id=1,
                            name='Org Near',
                            phone='111',
                            building_address='Near',
                            building_coordinates=(0.0, 0.0),
                            specializations=[],
                        )
                    ]
                ),
            ),
            # ✅ Case 2: no organizations in radius
            TestCase(
                db_fixtures=[
                    models.Building(id=1, address='Too Far', point=from_shape(Point(50.0, 50.0), srid=4326)),
                    models.Organization(id=1, name='Lonely Org', phone='000'),
                    models.OrganizationBuilding(organization_id=1, building_id=1),
                ],
                call=mock.call(longitude=0, latitude=0, radius_m=1),
                expected_value=schemas.ListOrganizations(organizations=[]),
            ),
            # ✅ Case 3: organization without any building link
            TestCase(
                db_fixtures=[
                    models.Organization(id=1, name='No Building Org', phone='404'),
                ],
                call=mock.call(longitude=0, latitude=0, radius_m=1),
                expected_value=schemas.ListOrganizations(organizations=[]),
            ),
            # ✅ Case 4: multiple organizations in different buildings within radius
            TestCase(
                db_fixtures=[
                    models.Building(id=1, address='A', point=from_shape(Point(0.0, 0.0), srid=4326)),
                    models.Building(id=2, address='B', point=from_shape(Point(0.5, 0.5), srid=4326)),
                    models.Organization(id=1, name='Org A', phone='111'),
                    models.Organization(id=2, name='Org B', phone='222'),
                    models.OrganizationBuilding(organization_id=1, building_id=1),
                    models.OrganizationBuilding(organization_id=2, building_id=2),
                ],
                call=mock.call(longitude=0, latitude=0, radius_m=1_000 * 100),
                expected_value=schemas.ListOrganizations(
                    organizations=[
                        schemas.Organization(
                            id=2,
                            building_id=2,
                            name='Org B',
                            phone='222',
                            building_address='B',
                            building_coordinates=(0.5, 0.5),
                            specializations=[],
                        ),
                        schemas.Organization(
                            id=1,
                            building_id=1,
                            name='Org A',
                            phone='111',
                            building_address='A',
                            building_coordinates=(0.0, 0.0),
                            specializations=[],
                        ),
                    ]
                ),
            ),
            # ✅ Case 5: same org in multiple buildings, both within radius
            TestCase(
                db_fixtures=[
                    models.Building(id=1, address='Main', point=from_shape(Point(0, 0), srid=4326)),
                    models.Building(id=2, address='Branch', point=from_shape(Point(0.1, 0.1), srid=4326)),
                    models.Organization(id=1, name='Multi Org', phone='777'),
                    models.OrganizationBuilding(organization_id=1, building_id=1),
                ],
                call=mock.call(longitude=0, latitude=0, radius_m=1),
                expected_value=schemas.ListOrganizations(
                    organizations=[
                        schemas.Organization(
                            id=1,
                            building_id=1,
                            name='Multi Org',
                            phone='777',
                            building_address='Main',
                            building_coordinates=(0.0, 0.0),
                            specializations=[],
                        ),
                    ]
                ),
            ),
        ],
    )
    async def test_get_by_radius(self, session: AsyncSession, case: TestCase):
        await fill_db(session, case.db_fixtures)
        repo = OrganizationRepository(session=session)

        res = await repo.get_by_building_location_radius(*case.call.args, **case.call.kwargs)

        assert res == case.expected_value

    @pytest.mark.parametrize(
        'case',
        [
            TestCase(
                db_fixtures=[
                    models.Building(id=1, address='Shared Address', point=from_shape(Point(0, 0), srid=4326)),
                    models.Organization(id=2, name='Org 2', phone='222'),
                    models.Organization(id=3, name='Org 3', phone='333'),
                    models.OrganizationBuilding(organization_id=2, building_id=1),
                    models.OrganizationBuilding(organization_id=3, building_id=1),
                ],
                call=mock.call(ll_longitude=0, ll_latitude=0, ur_longitude=0.01, ur_latitude=0.01),
                expected_value=schemas.ListOrganizations(
                    organizations=[
                        schemas.Organization(
                            id=2,
                            building_id=1,
                            name='Org 2',
                            phone='222',
                            building_address='Shared Address',
                            building_coordinates=(0, 0),
                            specializations=[],
                        ),
                        schemas.Organization(
                            id=3,
                            building_id=1,
                            name='Org 3',
                            phone='333',
                            building_address='Shared Address',
                            building_coordinates=(0, 0),
                            specializations=[],
                        ),
                    ]
                ),
            ),
            TestCase(
                db_fixtures=[
                    models.Building(id=1, address='Near', point=from_shape(Point(0.0, 0.0), srid=4326)),
                    models.Building(id=2, address='Far', point=from_shape(Point(0.011, 0.0), srid=4326)),
                    models.Organization(id=1, name='Org Near', phone='111'),
                    models.Organization(id=2, name='Org Far', phone='999'),
                    models.OrganizationBuilding(organization_id=1, building_id=1),
                    models.OrganizationBuilding(organization_id=2, building_id=2),
                ],
                call=mock.call(ll_longitude=0, ll_latitude=0, ur_longitude=0.01, ur_latitude=0.01),
                expected_value=schemas.ListOrganizations(
                    organizations=[
                        schemas.Organization(
                            id=1,
                            building_id=1,
                            name='Org Near',
                            phone='111',
                            building_address='Near',
                            building_coordinates=(0.0, 0.0),
                            specializations=[],
                        )
                    ]
                ),
            ),
            TestCase(
                db_fixtures=[
                    models.Building(id=1, address='Too Far', point=from_shape(Point(50.0, 50.0), srid=4326)),
                    models.Organization(id=1, name='Lonely Org', phone='000'),
                    models.OrganizationBuilding(organization_id=1, building_id=1),
                ],
                call=mock.call(ll_longitude=0, ll_latitude=0, ur_longitude=0.01, ur_latitude=0.01),
                expected_value=schemas.ListOrganizations(organizations=[]),
            ),
            TestCase(
                db_fixtures=[
                    models.Building(id=1, address='A', point=from_shape(Point(0.0, 0.0), srid=4326)),
                    models.Building(id=2, address='B', point=from_shape(Point(0, 0.005), srid=4326)),
                    models.Organization(id=1, name='Org A', phone='111'),
                    models.Organization(id=2, name='Org B', phone='222'),
                    models.OrganizationBuilding(organization_id=1, building_id=1),
                    models.OrganizationBuilding(organization_id=2, building_id=2),
                ],
                call=mock.call(ll_longitude=0, ll_latitude=0, ur_longitude=0.01, ur_latitude=0.01),
                expected_value=schemas.ListOrganizations(
                    organizations=[
                        schemas.Organization(
                            id=2,
                            building_id=2,
                            name='Org B',
                            phone='222',
                            building_address='B',
                            building_coordinates=(0, 0.005),
                            specializations=[],
                        ),
                        schemas.Organization(
                            id=1,
                            building_id=1,
                            name='Org A',
                            phone='111',
                            building_address='A',
                            building_coordinates=(0.0, 0.0),
                            specializations=[],
                        ),
                    ]
                ),
            ),
        ],
    )
    async def test_get_by_box(self, session: AsyncSession, case: TestCase):
        await fill_db(session, case.db_fixtures)
        repo = OrganizationRepository(session=session)

        res = await repo.get_by_building_location_box(*case.call.args, **case.call.kwargs)

        assert res == case.expected_value
