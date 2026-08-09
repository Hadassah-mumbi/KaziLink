from uuid import UUID

from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.provider import Provider
from app.models.category import Category
from app.models.provider_category import ProviderCategory
from app.models.user import User
from app.schemas.booking import BookingCreate


# ============================================================
# CREATE BOOKING
# ============================================================

def create_booking(
    db: Session,
    customer: User,
    booking_data: BookingCreate
):
    """
    Create a booking request from a customer
    to a provider for a specific service.
    """

    # --------------------------------------------------------
    # Find provider
    # --------------------------------------------------------

    provider = (
        db.query(Provider)
        .filter(
            Provider.id == booking_data.provider_id
        )
        .first()
    )

    if not provider:
        raise ValueError(
            "Provider not found."
        )

    # --------------------------------------------------------
    # Provider must be approved
    # --------------------------------------------------------

    if not provider.approved:
        raise ValueError(
            "This provider is not approved."
        )

    # --------------------------------------------------------
    # Provider must be available
    # --------------------------------------------------------

    if not provider.available:
        raise ValueError(
            "This provider is currently unavailable."
        )

    # --------------------------------------------------------
    # Check category
    # --------------------------------------------------------

    category = (
        db.query(Category)
        .filter(
            Category.id == booking_data.category_id
        )
        .first()
    )

    if not category:
        raise ValueError(
            "Service category not found."
        )

    # --------------------------------------------------------
    # Provider must offer category
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
        raise ValueError(
            "This provider does not offer the selected service."
        )

    # --------------------------------------------------------
    # Prevent customer booking own profile
    # --------------------------------------------------------

    if provider.user_id == customer.id:
        raise ValueError(
            "You cannot book your own provider profile."
        )

    # --------------------------------------------------------
    # Check for existing conflicting booking
    # --------------------------------------------------------

    existing_booking = (
        db.query(Booking)
        .filter(
            Booking.provider_id == provider.id,
            Booking.booking_date == booking_data.booking_date,
            Booking.booking_time == booking_data.booking_time,
            Booking.status.in_([
                "pending",
                "accepted"
            ])
        )
        .first()
    )

    if existing_booking:
        raise ValueError(
            "Provider already has a booking at this date and time."
        )

    # --------------------------------------------------------
    # Create booking
    # --------------------------------------------------------

    booking = Booking(
        customer_id=customer.id,
        provider_id=provider.id,
        category_id=category.id,
        booking_date=booking_data.booking_date,
        booking_time=booking_data.booking_time,
        county=booking_data.county,
        town=booking_data.town,
        address=booking_data.address,
        description=booking_data.description,
        status="pending"
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    return booking


# ============================================================
# GET SINGLE BOOKING
# ============================================================

def get_booking(
    db: Session,
    booking_id: UUID
):
    """
    Get a booking by ID.
    """

    return (
        db.query(Booking)
        .filter(
            Booking.id == booking_id
        )
        .first()
    )


# ============================================================
# GET CUSTOMER BOOKINGS
# ============================================================

def get_customer_bookings(
    db: Session,
    customer: User
):
    """
    Get all bookings created by a customer.
    """

    return (
        db.query(Booking)
        .filter(
            Booking.customer_id == customer.id
        )
        .order_by(
            Booking.created_at.desc()
        )
        .all()
    )


# ============================================================
# GET PROVIDER BOOKINGS
# ============================================================

def get_provider_bookings(
    db: Session,
    provider: Provider
):
    """
    Get all bookings received by a provider.
    """

    return (
        db.query(Booking)
        .filter(
            Booking.provider_id == provider.id
        )
        .order_by(
            Booking.created_at.desc()
        )
        .all()
    )


# ============================================================
# ACCEPT BOOKING
# ============================================================

def accept_booking(
    db: Session,
    booking: Booking,
    provider: Provider
):
    """
    Provider accepts a pending booking.
    """

    if booking.provider_id != provider.id:
        raise ValueError(
            "You are not the provider for this booking."
        )

    if booking.status != "pending":
        raise ValueError(
            f"Only pending bookings can be accepted. "
            f"Current status: {booking.status}."
        )

    booking.status = "accepted"

    db.commit()
    db.refresh(booking)

    return booking


# ============================================================
# REJECT BOOKING
# ============================================================

def reject_booking(
    db: Session,
    booking: Booking,
    provider: Provider
):
    """
    Provider rejects a pending booking.
    """

    if booking.provider_id != provider.id:
        raise ValueError(
            "You are not the provider for this booking."
        )

    if booking.status != "pending":
        raise ValueError(
            f"Only pending bookings can be rejected. "
            f"Current status: {booking.status}."
        )

    booking.status = "rejected"

    db.commit()
    db.refresh(booking)

    return booking


# ============================================================
# COMPLETE BOOKING
# ============================================================

def complete_booking(
    db: Session,
    booking: Booking,
    provider: Provider
):
    """
    Provider marks an accepted booking as completed.
    """

    if booking.provider_id != provider.id:
        raise ValueError(
            "You are not the provider for this booking."
        )

    if booking.status != "accepted":
        raise ValueError(
            f"Only accepted bookings can be completed. "
            f"Current status: {booking.status}."
        )

    booking.status = "completed"

    # Update provider completed jobs count
    provider.completed_jobs = (
        provider.completed_jobs + 1
    )

    db.commit()
    db.refresh(booking)

    return booking


# ============================================================
# CANCEL BOOKING
# ============================================================

def cancel_booking(
    db: Session,
    booking: Booking,
    customer: User
):
    """
    Customer cancels their own booking.
    """

    if booking.customer_id != customer.id:
        raise ValueError(
            "You are not the customer for this booking."
        )

    if booking.status == "completed":
        raise ValueError(
            "A completed booking cannot be cancelled."
        )

    if booking.status == "cancelled":
        raise ValueError(
            "Booking is already cancelled."
        )

    if booking.status == "rejected":
        raise ValueError(
            "A rejected booking cannot be cancelled."
        )

    booking.status = "cancelled"

    db.commit()
    db.refresh(booking)

    return booking


# ============================================================
# GENERIC STATUS UPDATE
# ============================================================

def update_booking_status(
    db: Session,
    booking: Booking,
    status: str
):
    """
    Generic status update.

    This function is kept for compatibility,
    but the preferred workflow is to use the
    dedicated accept/reject/complete/cancel functions.
    """

    allowed_statuses = {
        "pending",
        "accepted",
        "rejected",
        "cancelled",
        "completed",
    }

    status = status.lower()

    if status not in allowed_statuses:
        raise ValueError(
            "Invalid booking status."
        )

    # --------------------------------------------------------
    # Prevent changing completed bookings
    # --------------------------------------------------------

    if booking.status == "completed":
        raise ValueError(
            "A completed booking cannot be changed."
        )

    # --------------------------------------------------------
    # Prevent changing cancelled bookings
    # --------------------------------------------------------

    if booking.status == "cancelled":
        raise ValueError(
            "A cancelled booking cannot be changed."
        )

    # --------------------------------------------------------
    # Prevent changing rejected bookings
    # --------------------------------------------------------

    if booking.status == "rejected":
        raise ValueError(
            "A rejected booking cannot be changed."
        )

    # --------------------------------------------------------
    # Valid transitions
    # --------------------------------------------------------

    valid_transitions = {
        "pending": {
            "accepted",
            "rejected",
            "cancelled"
        },
        "accepted": {
            "completed",
            "cancelled"
        }
    }

    current_status = booking.status

    if (
        current_status not in valid_transitions
        or status not in valid_transitions[current_status]
    ):
        raise ValueError(
            f"Cannot change booking status from "
            f"{current_status} to {status}."
        )

    booking.status = status

    db.commit()
    db.refresh(booking)

    return booking