from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.review import (
    ReviewCreate,
    ReviewResponse,
)

from app.services.review_service import (
    create_review,
    get_review,
    get_provider_reviews,
    get_customer_reviews,
)


router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)


# ============================================================
# CREATE REVIEW
# ============================================================

@router.post(
    "",
    response_model=ReviewResponse
)
def create_new_review(
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a review for a completed booking.
    """

    try:

        return create_review(
            db,
            current_user,
            review
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ============================================================
# GET PROVIDER REVIEWS
# ============================================================

@router.get(
    "/provider/{provider_id}",
    response_model=list[ReviewResponse]
)
def get_reviews_for_provider(
    provider_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get all reviews for a provider.
    """

    return get_provider_reviews(
        db,
        provider_id
    )


# ============================================================
# GET MY REVIEWS
# ============================================================

@router.get(
    "/me",
    response_model=list[ReviewResponse]
)
def get_my_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all reviews created by the current customer.
    """

    return get_customer_reviews(
        db,
        current_user
    )


# ============================================================
# GET SINGLE REVIEW
# ============================================================

@router.get(
    "/{review_id}",
    response_model=ReviewResponse
)
def get_single_review(
    review_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a single review.
    """

    review = get_review(
        db,
        review_id
    )

    if not review:

        raise HTTPException(
            status_code=404,
            detail="Review not found."
        )

    return review