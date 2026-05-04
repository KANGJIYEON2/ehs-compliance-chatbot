from pydantic import BaseModel, Field


class SiteCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    address: str | None = None


class SiteUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    address: str | None = None


class SiteResponse(BaseModel):
    id: str
    company_id: str
    name: str
    address: str | None = None

    model_config = {"from_attributes": True}
