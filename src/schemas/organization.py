import pydantic as pd

from .specialization import Specialization


class Organization(pd.BaseModel):
    id: int
    name: str
    phone: str
    building_address: str
    building_coordinates: tuple[float, float]
    specializations: list[Specialization]


class ListOrganizations(pd.BaseModel):
    organizations: list[Organization]
