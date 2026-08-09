from datetime import time
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class ProviderAvailabilityCreate(BaseModel):
    day_of_week: int = Field(
        ge=0,
        le=6
    )

    start_time: time | None = None

    end_time: time | None = None

    is_available: bool = True

    @model_validator(mode="after")
    def validate_times(self):
        if self.is_available:
            if self.start_time is None or self.end_time is None:
                raise ValueError(
                    "Start time and end time are required when the day is available."
                )

            if self.start_time >= self.end_time:
                raise ValueError(
                    "Start time must be earlier than end time."
                )

        return self


class ProviderAvailabilityUpdate(BaseModel):
    start_time: time | None = None

    end_time: time | None = None

    is_available: bool

    @model_validator(mode="after")
    def validate_times(self):
        if self.is_available:
            if self.start_time is None or self.end_time is None:
                raise ValueError(
                    "Start time and end time are required when the day is available."
                )

            if self.start_time >= self.end_time:
                raise ValueError(
                    "Start time must be earlier than end time."
                )

        return self


class ProviderAvailabilityResponse(BaseModel):
    id: UUID
    provider_id: UUID
    day_of_week: int
    start_time: time | None = None
    end_time: time | None = None
    is_available: bool

    model_config = {
        "from_attributes": True
    }