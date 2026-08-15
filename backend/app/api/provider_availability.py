from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.provider import Provider
from app.models.category import Category
from app.models.provider_category import ProviderCategory
from app.models.provider_availability import ProviderAvailability
from app.schemas.provider_availability import (
    ProviderAvailabilityCreate,
    ProviderAvailabilityUpdate,
)


router = APIRouter(
    prefix="/providers",
    tags=["Provider Availability"]
)


def _availability_overlap(start_time, end_time, existing):
    if not existing.is_available or existing.start_time is None or existing.end_time is None:
        return False

    return start_time < existing.end_time and existing.start_time < end_time


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
    # Check category exists
    # --------------------------------------------------------

    category = (
        db.query(Category)
        .filter(Category.id == data.category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found."
        )

    # --------------------------------------------------------
    # Check provider offers this category
    # --------------------------------------------------------

    provider_category = (
        db.query(ProviderCategory)
        .filter(
            ProviderCategory.provider_id == provider.id,
            ProviderCategory.category_id == category.id
        )
        .first()
    )

    if not provider_category:
        raise HTTPException(
            status_code=400,
            detail="Provider does not offer this service category."
        )

    # --------------------------------------------------------
    # Prevent overlapping time slots for same provider/category/day
    # --------------------------------------------------------

    if data.is_available:
        existing = (
            db.query(ProviderAvailability)
            .filter(
                ProviderAvailability.provider_id == provider_id,
                ProviderAvailability.category_id == data.category_id,
                ProviderAvailability.day_of_week == data.day_of_week,
                ProviderAvailability.is_available.is_(True)
            )
            .all()
        )

        for slot in existing:
            if _availability_overlap(data.start_time, data.end_time, slot):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "This availability overlaps an existing time slot for the same "
                        "service category and day."
                    )
                )

    # --------------------------------------------------------
    # Create availability
    # --------------------------------------------------------

    availability = ProviderAvailability(
        provider_id=provider_id,
        category_id=data.category_id,
        day_of_week=data.day_of_week,
        start_time=data.start_time,
        end_time=data.end_time,
        is_available=data.is_available
    )

    db.add(availability)
    db.commit()
    db.refresh(availability)

    return {
        "message": "Provider availability added successfully.",
        "availability": {
            "id": str(availability.id),
            "provider_id": str(availability.provider_id),
            "category_id": str(availability.category_id),
            "category_name": category.name,
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
            ProviderAvailability.day_of_week,
            ProviderAvailability.category_id,
            ProviderAvailability.start_time
        )
        .all()
    )

    return [
        {
            "id": str(item.id),
            "provider_id": str(item.provider_id),
            "category_id": str(item.category_id),
            "category_name": item.category.name if item.category else None,
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

    category = (
        db.query(Category)
        .filter(Category.id == data.category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found."
        )

    provider_category = (
        db.query(ProviderCategory)
        .filter(
            ProviderCategory.provider_id == availability.provider_id,
            ProviderCategory.category_id == data.category_id
        )
        .first()
    )

    if not provider_category:
        raise HTTPException(
            status_code=400,
            detail="Provider does not offer this service category."
        )

    # --------------------------------------------------------
    # Prevent overlapping time slots for same provider/category/day
    # --------------------------------------------------------

    if data.is_available:
        existing = (
            db.query(ProviderAvailability)
            .filter(
                ProviderAvailability.provider_id == availability.provider_id,
                ProviderAvailability.category_id == data.category_id,
                ProviderAvailability.day_of_week == data.day_of_week,
                ProviderAvailability.id != availability_id,
                ProviderAvailability.is_available.is_(True)
            )
            .all()
        )

        for slot in existing:
            if _availability_overlap(data.start_time, data.end_time, slot):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "This availability overlaps an existing time slot for the same "
                        "service category and day."
                    )
                )

    # --------------------------------------------------------
    # Update record
    # --------------------------------------------------------

    availability.category_id = data.category_id
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
            "category_id": str(availability.category_id),
            "category_name": category.name,
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