from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class ProviderCreate(BaseModel):
    bio: str = Field(
        min_length=20,
        max_length=1000
    )

    county: str = Field(
        min_length=2,
        max_length=100
    )

    town: str = Field(
        min_length=2,
        max_length=100
    )

    latitude: float = Field(
        ge=-90,
        le=90
    )

    longitude: float = Field(
        ge=-180,
        le=180
    )

    experience_years: int = Field(
        ge=0,
        le=60
    )

    hourly_rate: float = Field(
        gt=0
    )

    daily_rate: float = Field(
        gt=0
    )


class ProviderLocationUpdate(BaseModel):
    latitude: float = Field(
        ge=-90,
        le=90
    )

    longitude: float = Field(
        ge=-180,
        le=180
    )


class ServiceRadiusUpdate(BaseModel):
    service_radius_km: float = Field(
        gt=0,
        le=100
    )


class ServiceLocationRequest(BaseModel):
    category_id: UUID

    latitude: float = Field(
        ge=-90,
        le=90
    )

    longitude: float = Field(
        ge=-180,
        le=180
    )


class ProviderCategoryAdd(BaseModel):
    category_id: UUID


class ProviderCategoryResponse(BaseModel):
    category_id: UUID
    name: str
    description: str | None = None


class ProviderResponse(BaseModel):
    id: UUID

    name: str | None = None

    phone: str | None = None

    bio: str

    county: str

    town: str

    latitude: float | None = None

    longitude: float | None = None

    service_radius_km: float

    experience_years: int

    hourly_rate: float

    daily_rate: float

    approved: bool

    available: bool

    average_rating: float

    total_reviews: int

    completed_jobs: int

    profile_picture: str | None = None

    national_id_document: str | None = None

    good_conduct_certificate: str | None = None

    services: list[ProviderCategoryResponse] = []

    model_config = ConfigDict(
        from_attributes=True
    )


class NearbyProviderResponse(ProviderResponse):
    distance_km: float


class PublicProviderResponse(BaseModel):
    """
    Information that can safely be shown to customers
    when viewing a provider profile.
    """

    id: UUID

    name: str | None = None

    phone: str | None = None

    bio: str

    county: str

    town: str

    latitude: float | None = None

    longitude: float | None = None

    experience_years: int

    hourly_rate: float

    daily_rate: float

    available: bool

    average_rating: float

    total_reviews: int

    completed_jobs: int

    profile_picture: str | None = None

    services: list[ProviderCategoryResponse] = []

    model_config = ConfigDict(
        from_attributes=True
    )