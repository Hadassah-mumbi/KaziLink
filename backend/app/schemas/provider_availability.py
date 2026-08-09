from datetime import time

from pydantic import BaseModel, Field, field_validator


class ProviderAvailabilityCreate(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)
    start_time: time
    end_time: time

    @field_validator("end_time")
    @classmethod
    def validate_time_range(cls, value, info):
        start_time = info.data.get("start_time")

        if start_time is not None and value <= start_time:
            raise ValueError("end_time must be later than start_time.")

        return value


class ProviderAvailabilityUpdate(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)
    start_time: time
    end_time: time
    is_available: bool = True

    @field_validator("end_time")
    @classmethod
    def validate_time_range(cls, value, info):
        start_time = info.data.get("start_time")

        if start_time is not None and value <= start_time:
            raise ValueError("end_time must be later than start_time.")

        return value