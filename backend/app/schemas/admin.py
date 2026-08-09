from pydantic import BaseModel

class ProviderApplicationResponse(BaseModel):
id: str
user_id: str

first_name: str
last_name: str
email: str
phone: str

bio: str
county: str
town: str

experience_years: int
hourly_rate: float
daily_rate: float

approved: bool

class Config:
    from_attributes = True


class AdminUserResponse(BaseModel):
id: str
first_name: str
last_name: str
email: str
phone: str

is_provider: bool
is_admin: bool
is_active: bool

created_at: str | None = None
updated_at: str | None = None

class Config:
    from_attributes = True
