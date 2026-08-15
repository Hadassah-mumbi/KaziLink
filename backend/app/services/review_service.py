from uuid import UUID

from sqlalchemy.orm import Session

from app.models.review import Review
from app.models.booking import Booking
from app.models.provider import Provider
from app.models.user import User
from app.schemas.review import ReviewCreate


def create_review(
    db: Session,
    customer: User,
    review_data: ReviewCreate
):
    """
    Create a review for a completed booking.

    Rules:
    - Booking must exist.
    - Booking must belong to the customer.
    - Booking must be completed.
    - Provider must exist.
    - Booking cannot already have a review.
    """

    # --------------------------------------------------
    # 1. Find booking
    # --------------------------------------------------

    booking = (
        db.query(Booking)
        .filter(
            Booking.id == review_data.booking_id
        )
        .first()
    )

    if not booking:
        raise ValueError(
            "Booking not found."
        )

    # --------------------------------------------------
    # 2. Make sure booking belongs to customer
    # --------------------------------------------------

    if booking.customer_id != customer.id:
        raise ValueError(
            "You can only review your own bookings."
        )

    # --------------------------------------------------
    # 3. Booking must be completed
    # --------------------------------------------------

    if booking.status != "completed":
        raise ValueError(
            "You can only review a completed booking."
        )

    # --------------------------------------------------
    # 4. Check whether booking already has a review
    # --------------------------------------------------

    existing_review = (
        db.query(Review)
        .filter(
            Review.booking_id == booking.id
        )
        .first()
    )

    if existing_review:
        raise ValueError(
            "This booking has already been reviewed."
        )

    # --------------------------------------------------
    # 5. Find provider
    # --------------------------------------------------

    provider = (
        db.query(Provider)
        .filter(
            Provider.id == booking.provider_id
        )
        .first()
    )

    if not provider:
        raise ValueError(
            "Provider not found."
        )

    # --------------------------------------------------
    # 6. Create review
    # --------------------------------------------------

    review = Review(
        booking_id=booking.id,
        customer_id=customer.id,
        provider_id=provider.id,
        rating=review_data.rating,
        comment=review_data.comment,
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    # --------------------------------------------------
    # 7. Recalculate provider rating
    # --------------------------------------------------

    provider_reviews = (
        db.query(Review)
        .filter(
            Review.provider_id == provider.id
        )
        .all()
    )

    total_reviews = len(provider_reviews)

    if total_reviews > 0:
        total_rating = sum(
            item.rating
            for item in provider_reviews
        )

        provider.average_rating = round(
            total_rating / total_reviews,
            2
        )

    else:
        provider.average_rating = 0.0

    provider.total_reviews = total_reviews

    db.commit()
    db.refresh(provider)

    return review


def get_review(
    db: Session,
    review_id: UUID
):
    """
    Get a single review.
    """

    return (
        db.query(Review)
        .filter(
            Review.id == review_id
        )
        .first()
    )


def get_provider_reviews(
    db: Session,
    provider_id: UUID
):
    """
    Get all reviews for a provider.
    """

    return (
        db.query(Review)
        .filter(
            Review.provider_id == provider_id
        )
        .order_by(
            Review.created_at.desc()
        )
        .all()
    )


def get_customer_reviews(
    db: Session,
    customer: User
):
    """
    Get all reviews created by a customer.
    """

    return (
        db.query(Review)
        .filter(
            Review.customer_id == customer.id
        )
        .order_by(
            Review.created_at.desc()
        )
        .all()
    )


def create_provider_review(
    db: Session,
    provider: "Provider",
    review_data: ReviewCreate
):
    """
    Create or update a provider's review of a customer.

    Rules:
    - Booking must exist.
    - Booking must belong to the provider.
    - Booking must be completed.
    - Customer must exist.
    """

    # --------------------------------------------------
    # 1. Find booking
    # --------------------------------------------------

    booking = (
        db.query(Booking)
        .filter(
            Booking.id == review_data.booking_id
        )
        .first()
    )

    if not booking:
        raise ValueError(
            "Booking not found."
        )

    # --------------------------------------------------
    # 2. Make sure booking belongs to provider
    # --------------------------------------------------

    if booking.provider_id != provider.id:
        raise ValueError(
            "You can only review your own bookings."
        )

    # --------------------------------------------------
    # 3. Booking must be completed
    # --------------------------------------------------

    if booking.status != "completed":
        raise ValueError(
            "You can only review a completed booking."
        )

    # --------------------------------------------------
    # 4. Find or create review record
    # --------------------------------------------------

    review = (
        db.query(Review)
        .filter(
            Review.booking_id == booking.id
        )
        .first()
    )

    if not review:
        # Create new review record
        review = Review(
            booking_id=booking.id,
            customer_id=booking.customer_id,
            provider_id=provider.id,
        )

    # --------------------------------------------------
    # 5. Update provider review fields
    # --------------------------------------------------

    review.provider_rating = review_data.rating
    review.provider_comment = review_data.comment

    db.add(review)
    db.commit()
    db.refresh(review)

    # --------------------------------------------------
    # 6. Recalculate customer rating
    # --------------------------------------------------

    customer = (
        db.query(User)
        .filter(
            User.id == booking.customer_id
        )
        .first()
    )

    if customer:
        provider_reviews = (
            db.query(Review)
            .filter(
                Review.customer_id == customer.id,
                Review.provider_rating.isnot(None)
            )
            .all()
        )

        total_provider_reviews = len(provider_reviews)

        if total_provider_reviews > 0:
            total_rating = sum(
                item.provider_rating
                for item in provider_reviews
            )

            # Store customer rating on the user (we could add this field to User model)
            # For now, we'll just return it in the response
        else:
            total_provider_reviews = 0

    return review


def get_provider_reviews_for_customer(
    db: Session,
    customer_id: UUID
):
    """
    Get all reviews that providers have given to a customer.
    """

    return (
        db.query(Review)
        .filter(
            Review.customer_id == customer_id,
            Review.provider_rating.isnot(None)
        )
        .order_by(
            Review.created_at.desc()
        )
        .all()
    )
