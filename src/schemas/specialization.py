import pydantic as pd


class Specialization(pd.BaseModel):
    id: int
    name: str
    parent_id: int | None
