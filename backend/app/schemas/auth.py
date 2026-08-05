from pydantic import BaseModel, EmailStr, Field


class CustomerRegister(BaseModel):
    first_name: str = Field(min_length=2, max_length=100)
    last_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str
    password: str = Field(min_length=8)


class ProviderRegister(CustomerRegister):
    bio: str
    county: str
    town: str
    experience_years: int
    hourly_rate: float
    daily_rate: float


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"