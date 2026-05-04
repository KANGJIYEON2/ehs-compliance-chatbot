from datetime import datetime
from pydantic import BaseModel, Field


class IncidentCreate(BaseModel):
    site_id: str
    incident_type: str = Field(..., description="caught|fall|collision|electric|fire|suffocation|falling_object|chemical|other")
    severity: str = Field(..., description="death|serious|minor|near_miss")
    occurred_at: datetime
    work_zone_id: str | None = None
    process_id: str | None = None
    equipment_id: str | None = None
    department_id: str | None = None
    description: str = Field(..., min_length=1)
    cause_estimate: str | None = None
    action_taken: str | None = None


class IncidentUpdate(BaseModel):
    incident_type: str | None = None
    severity: str | None = None
    occurred_at: datetime | None = None
    work_zone_id: str | None = None
    process_id: str | None = None
    equipment_id: str | None = None
    department_id: str | None = None
    description: str | None = None
    cause_estimate: str | None = None
    action_taken: str | None = None
    status: str | None = Field(None, description="reported|investigating|resolved|monitoring")


class AttachmentResponse(BaseModel):
    id: str
    file_name: str
    file_type: str | None = None
    file_size: int | None = None
    uploaded_at: datetime
    model_config = {"from_attributes": True}


class IncidentResponse(BaseModel):
    id: str
    site_id: str
    reporter_id: str
    incident_type: str
    severity: str
    occurred_at: datetime
    work_zone_id: str | None = None
    process_id: str | None = None
    equipment_id: str | None = None
    department_id: str | None = None
    description: str
    cause_estimate: str | None = None
    action_taken: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime
    attachments: list[AttachmentResponse] = []
    model_config = {"from_attributes": True}


class IncidentListResponse(BaseModel):
    items: list[IncidentResponse]
    total: int
    page: int
    size: int
