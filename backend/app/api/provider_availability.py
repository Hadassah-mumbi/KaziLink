from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.provider import Provider
from app.models.provider_availability import ProviderAvailability
from app.schemas.provider_availability import (
    ProviderAvailabilityCreate,
    ProviderAvailabilityUpdate,
)


router = APIRouter(
    prefix="/providers",
    tags=["Provider Availability"]
)


# ============================================================
# ADD AVAILABILITY
# ============================================================

@router.post("/{provider_id}/availability")
def add_provider_availability(
    provider_id: str,
    data: ProviderAvailabilityCreate,
    db: Session = Depends(get_db)
):
    """
    Add working hours for a provider.

    day_of_week:
        0 = Monday
        1 = Tuesday
        2 = Wednesday
        3 = Thursday
        4 = Friday
        5 = Saturday
        6 = Sunday
    """

    # --------------------------------------------------------
    # Check provider exists
    # --------------------------------------------------------

    provider = (
        db.query(Provider)
        .filter(Provider.id == provider_id)
        .first()
    )

    if not provider:
        raise HTTPException(
            status_code=404,
            detail="Provider not found."
        )

    # --------------------------------------------------------
    # Check whether availability already exists for this day
    # --------------------------------------------------------

    existing = (
        db.query(ProviderAvailability)
        .filter(
            ProviderAvailability.provider_id == provider_id,
            ProviderAvailability.day_of_week == data.day_of_week
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Availability for this day already exists."
        )

    # --------------------------------------------------------
    # Create availability
    # --------------------------------------------------------

    availability = ProviderAvailability(
        provider_id=provider_id,
        day_of_week=data.day_of_week,
        start_time=data.start_time,
        end_time=data.end_time,
        is_available=True
    )

    db.add(availability)
    db.commit()
    db.refresh(availability)

    return {
        "message": "Provider availability added successfully.",
        "availability": {
            "id": str(availability.id),
            "provider_id": str(availability.provider_id),
            "day_of_week": availability.day_of_week,
            "start_time": availability.start_time,
            "end_time": availability.end_time,
            "is_available": availability.is_available
        }
    }


# ============================================================
# GET PROVIDER AVAILABILITY
# ============================================================

@router.get("/{provider_id}/availability")
def get_provider_availability(
    provider_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all working hours for a provider.
    """

    # --------------------------------------------------------
    # Check provider exists
    # --------------------------------------------------------

    provider = (
        db.query(Provider)
        .filter(Provider.id == provider_id)
        .first()
    )

    if not provider:
        raise HTTPException(
            status_code=404,
            detail="Provider not found."
        )

    # --------------------------------------------------------
    # Get availability
    # --------------------------------------------------------

    availability = (
        db.query(ProviderAvailability)
        .filter(
            ProviderAvailability.provider_id == provider_id
        )
        .order_by(
            ProviderAvailability.day_of_week
        )
        .all()
    )

    return [
        {
            "id": str(item.id),
            "provider_id": str(item.provider_id),
            "day_of_week": item.day_of_week,
            "start_time": item.start_time,
            "end_time": item.end_time,
            "is_available": item.is_available
        }
        for item in availability
    ]


# ============================================================
# UPDATE AVAILABILITY
# ============================================================

@router.put("/availability/{availability_id}")
def update_provider_availability(
    availability_id: str,
    data: ProviderAvailabilityUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing provider availability record.
    """

    # --------------------------------------------------------
    # Find availability record
    # --------------------------------------------------------

    availability = (
        db.query(ProviderAvailability)
        .filter(
            ProviderAvailability.id == availability_id
        )
        .first()
    )

    if not availability:
        raise HTTPException(
            status_code=404,
            detail="Availability record not found."
        )

    # --------------------------------------------------------
    # Check if another availability already exists
    # for this provider on the new day
    # --------------------------------------------------------

    existing = (
        db.query(ProviderAvailability)
        .filter(
            ProviderAvailability.provider_id == availability.provider_id,
            ProviderAvailability.day_of_week == data.day_of_week,
            ProviderAvailability.id != availability_id
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Availability for this day already exists."
        )

    # --------------------------------------------------------
    # Update record
    # --------------------------------------------------------

    availability.day_of_week = data.day_of_week
    availability.start_time = data.start_time
    availability.end_time = data.end_time
    availability.is_available = data.is_available

    db.commit()
    db.refresh(availability)

    return {
        "message": "Provider availability updated successfully.",
        "availability": {
            "id": str(availability.id),
            "provider_id": str(availability.provider_id),
            "day_of_week": availability.day_of_week,
            "start_time": availability.start_time,
            "end_time": availability.end_time,
            "is_available": availability.is_available
        }
    }


# ============================================================
# DELETE AVAILABILITY
# ============================================================

@router.delete("/availability/{availability_id}")
def delete_provider_availability(
    availability_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete an availability record.
    """

    # --------------------------------------------------------
    # Find availability record
    # --------------------------------------------------------

    availability = (
        db.query(ProviderAvailability)
        .filter(
            ProviderAvailability.id == availability_id
        )
        .first()
    )

    if not availability:
        raise HTTPException(
            status_code=404,
            detail="Availability record not found."
        )

    # --------------------------------------------------------
    # Delete record
    # --------------------------------------------------------

    db.delete(availability)
    db.commit()

    return {
        "message": "Provider availability deleted successfully."
    }