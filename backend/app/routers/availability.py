from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User
from app.models.provider import Provider

from app.schemas.availability import (
    ProviderAvailabilityCreate,
    ProviderAvailabilityUpdate,
    ProviderAvailabilityResponse,
)

from app.services.availability_service import (
    get_provider_availability,
    create_provider_availability,
    update_provider_availability,
    delete_provider_availability,
)


router = APIRouter(
    prefix="/providers/me/availability",
    tags=["Provider Availability"]
)


def get_current_provider(
    db: Session,
    current_user: User
):
    """
    Get the provider profile belonging to
    the currently authenticated user.
    """

    provider = (
        db.query(Provider)
        .filter(
            Provider.user_id == current_user.id
        )
        .first()
    )

    if not provider:
        raise HTTPException(
            status_code=404,
            detail="Provider profile not found."
        )

    return provider


@router.get(
    "",
    response_model=list[ProviderAvailabilityResponse]
)
def get_my_availability(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the current provider's complete
    weekly availability schedule.
    """

    provider = get_current_provider(
        db,
        current_user
    )

    return get_provider_availability(
        db,
        provider
    )


@router.post(
    "",
    response_model=ProviderAvailabilityResponse
)
def add_my_availability(
    data: ProviderAvailabilityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add availability for a day of the week.
    """

    provider = get_current_provider(
        db,
        current_user
    )

    try:
        return create_provider_availability(
            db,
            provider,
            data
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.put(
    "/{day_of_week}",
    response_model=ProviderAvailabilityResponse
)
def update_my_availability(
    day_of_week: int,
    data: ProviderAvailabilityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update availability for one day of the week.
    """

    if day_of_week < 0 or day_of_week > 6:
        raise HTTPException(
            status_code=400,
            detail="day_of_week must be between 0 and 6."
        )

    provider = get_current_provider(
        db,
        current_user
    )

    try:
        return update_provider_availability(
            db,
            provider,
            day_of_week,
            data
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.delete(
    "/{day_of_week}"
)
def delete_my_availability(
    day_of_week: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove availability for one day.

    Removing the record means the provider
    has no working schedule for that day.
    """

    if day_of_week < 0 or day_of_week > 6:
        raise HTTPException(
            status_code=400,
            detail="day_of_week must be between 0 and 6."
        )

    provider = get_current_provider(
        db,
        current_user
    )

    deleted = delete_provider_availability(
        db,
        provider,
        day_of_week
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Availability for this day was not found."
        )

    return {
        "message": "Availability removed successfully."
    }