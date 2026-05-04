from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=200)
    business_number: str | None = Field(None, max_length=20)
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=1, max_length=100)


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    company_id: str
    site_id: str | None = None

    model_config = {"from_attributes": True}


class CreateUserRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(..., description="field_manager | worker")
    site_id: str | None = None
