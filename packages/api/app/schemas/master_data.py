from pydantic import BaseModel, Field


# ── Department ──
class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)


class DepartmentResponse(BaseModel):
    id: str
    site_id: str
    name: str
    model_config = {"from_attributes": True}


# ── Process ──
class ProcessCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)


class ProcessResponse(BaseModel):
    id: str
    site_id: str
    name: str
    model_config = {"from_attributes": True}


# ── Equipment ──
class EquipmentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    process_id: str | None = None


class EquipmentResponse(BaseModel):
    id: str
    site_id: str
    process_id: str | None = None
    name: str
    model_config = {"from_attributes": True}


# ── WorkZone ──
class WorkZoneCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)


class WorkZoneResponse(BaseModel):
    id: str
    site_id: str
    name: str
    model_config = {"from_attributes": True}
