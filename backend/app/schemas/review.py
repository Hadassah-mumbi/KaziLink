from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class ReviewCreate(BaseModel):
    booking_id: UUID

    rating: int = Field(
        ge=1,
        le=5
    )

    comment: str | None = Field(
        default=None,
        max_length=1000
    )


class ReviewResponse(BaseModel):
    id: UUID

    booking_id: UUID

    customer_id: UUID

    provider_id: UUID

    rating: int

    comment: str | None

    created_at: datetime | None = None

    updated_at: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True
    )