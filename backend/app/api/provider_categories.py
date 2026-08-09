from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User
from app.models.provider import Provider

from app.schemas.provider import (
    ProviderCategoryAdd,
    ProviderCategoryResponse
)

from app.services.provider_service import (
    add_provider_category,
    get_provider_categories,
    remove_provider_category
)


router = APIRouter(
    prefix="/providers/me/services",
    tags=["Provider Services"]
)


@router.get(
    "",
    response_model=list[ProviderCategoryResponse]
)
def get_my_services(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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

    services = get_provider_categories(
        db,
        provider
    )

    return [
        {
            "id": service.id,
            "category_id": service.category_id,
            "name": service.category.name,
            "description": service.category.description
        }
        for service in services
    ]


@router.post(
    "",
    response_model=ProviderCategoryResponse
)
def add_my_service(
    data: ProviderCategoryAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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

    try:

        provider_category = add_provider_category(
            db,
            provider,
            data.category_id
        )

        return {
            "id": provider_category.id,
            "category_id": provider_category.category_id,
            "name": provider_category.category.name,
            "description": provider_category.category.description
        }

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.delete(
    "/{category_id}"
)
def remove_my_service(
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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

    deleted = remove_provider_category(
        db,
        provider,
        category_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Service not found for this provider."
        )

    return {
        "message": "Service removed successfully."
    }