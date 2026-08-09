from uuid import UUID
from datetime import date, time, datetime

from pydantic import BaseModel, Field, ConfigDict


# ============================================================
# CREATE BOOKING
# ============================================================

class BookingCreate(BaseModel):

    provider_id: UUID

    category_id: UUID

    booking_date: date

    booking_time: time

    county: str = Field(
        min_length=2,
        max_length=100
    )

    town: str = Field(
        min_length=2,
        max_length=100
    )

    address: str | None = Field(
        default=None,
        max_length=500
    )

    description: str | None = Field(
        default=None,
        max_length=2000
    )


# ============================================================
# BOOKING RESPONSE
# ============================================================

class BookingResponse(BaseModel):

    id: UUID

    customer_id: UUID

    provider_id: UUID

    category_id: UUID

    booking_date: date

    booking_time: time

    county: str

    town: str

    address: str | None = None

    description: str | None = None

    status: str

    created_at: datetime | None = None

    updated_at: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# BOOKING STATUS UPDATE
# ============================================================

class BookingStatusUpdate(BaseModel):

    status: str = Field(
        min_length=1,
        max_length=30
    )