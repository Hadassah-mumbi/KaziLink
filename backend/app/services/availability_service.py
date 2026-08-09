from datetime import time
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.provider import Provider
from app.models.provider_availability import ProviderAvailability
from app.schemas.availability import (
    ProviderAvailabilityCreate,
    ProviderAvailabilityUpdate,
)


def get_provider_availability(
    db: Session,
    provider: Provider
):
    """
    Get the complete weekly availability schedule
    for a provider.

    Results are ordered from Monday to Sunday.
    """

    return (
        db.query(ProviderAvailability)
        .filter(
            ProviderAvailability.provider_id == provider.id
        )
        .order_by(
            ProviderAvailability.day_of_week
        )
        .all()
    )


def get_availability_for_day(
    db: Session,
    provider: Provider,
    day_of_week: int
):
    """
    Get a provider's availability for one specific day.
    """

    return (
        db.query(ProviderAvailability)
        .filter(
            ProviderAvailability.provider_id == provider.id,
            ProviderAvailability.day_of_week == day_of_week
        )
        .first()
    )


def create_provider_availability(
    db: Session,
    provider: Provider,
    availability_data: ProviderAvailabilityCreate
):
    """
    Create availability for a specific day.

    A provider can only have one availability
    record for each day of the week.
    """

    existing = get_availability_for_day(
        db,
        provider,
        availability_data.day_of_week
    )

    if existing:
        raise ValueError(
            "Availability for this day already exists."
        )

    availability = ProviderAvailability(
        provider_id=provider.id,
        day_of_week=availability_data.day_of_week,
        start_time=availability_data.start_time,
        end_time=availability_data.end_time,
        is_available=availability_data.is_available,
    )

    db.add(availability)
    db.commit()
    db.refresh(availability)

    return availability


def update_provider_availability(
    db: Session,
    provider: Provider,
    day_of_week: int,
    availability_data: ProviderAvailabilityUpdate
):
    """
    Update the availability for a specific day.
    """

    availability = get_availability_for_day(
        db,
        provider,
        day_of_week
    )

    if not availability:
        raise ValueError(
            "Availability for this day has not been set."
        )

    availability.start_time = availability_data.start_time
    availability.end_time = availability_data.end_time
    availability.is_available = availability_data.is_available

    db.commit()
    db.refresh(availability)

    return availability


def delete_provider_availability(
    db: Session,
    provider: Provider,
    day_of_week: int
):
    """
    Delete the availability record for a specific day.
    """

    availability = get_availability_for_day(
        db,
        provider,
        day_of_week
    )

    if not availability:
        return False

    db.delete(availability)
    db.commit()

    return True


def is_provider_working_at(
    db: Session,
    provider: Provider,
    day_of_week: int,
    requested_time: time
) -> bool:
    """
    Check whether a provider is scheduled to work
    at a specific day and time.

    This checks only the provider's working schedule.

    Booking conflicts are handled separately.
    """

    availability = get_availability_for_day(
        db,
        provider,
        day_of_week
    )

    if not availability:
        return False

    if not availability.is_available:
        return False

    if availability.start_time is None:
        return False

    if availability.end_time is None:
        return False

    return (
        availability.start_time
        <= requested_time
        < availability.end_time
    )