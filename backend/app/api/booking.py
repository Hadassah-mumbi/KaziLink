from datetime import date, time
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.dependencies import get_current_user

from app.models.booking import Booking
from app.models.user import User
from app.models.provider import Provider
from app.models.category import Category
from app.models.provider_category import ProviderCategory
from app.models.provider_availability import ProviderAvailability

from app.schemas.booking import (
    BookingCreate,
    BookingStatusUpdate,
)

from fastapi.responses import Response
from app.services import document_service


router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"]
)


# ============================================================
# CREATE BOOKING
# ============================================================

@router.post("")
def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new booking.

    The customer is automatically taken from the
    authenticated user instead of being supplied manually.

    The booking is validated against:

    - Customer authentication
    - Provider existence
    - Provider approval
    - Provider availability
    - Category existence
    - Provider/category relationship
    - Provider working day
    - Provider working hours
    - Existing booking conflicts
    """

    # --------------------------------------------------------
    # Customer
    # --------------------------------------------------------

    customer = current_user

    # A provider should not book themselves
    if customer.is_provider:
        provider_check = (
            db.query(Provider)
            .filter(
                Provider.user_id == customer.id
            )
            .first()
        )

        if provider_check:
            if provider_check.id == booking_data.provider_id:
                raise HTTPException(
                    status_code=400,
                    detail="You cannot book your own provider profile."
                )

    # --------------------------------------------------------
    # Check provider
    # --------------------------------------------------------

    provider = (
        db.query(Provider)
        .filter(
            Provider.id == booking_data.provider_id
        )
        .first()
    )

    if not provider:
        raise HTTPException(
            status_code=404,
            detail="Provider not found."
        )

    # --------------------------------------------------------
    # Prevent provider from booking themselves
    # --------------------------------------------------------

    if provider.user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot book your own provider profile."
        )

    # --------------------------------------------------------
    # Check provider approval
    # --------------------------------------------------------

    if not provider.approved:
        raise HTTPException(
            status_code=400,
            detail="Provider has not been approved yet."
        )

    # --------------------------------------------------------
    # Check provider availability
    # --------------------------------------------------------

    if not provider.available:
        raise HTTPException(
            status_code=400,
            detail="Provider is currently unavailable."
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
        raise HTTPException(
            status_code=404,
            detail="Category not found."
        )

    # --------------------------------------------------------
    # Check provider offers category
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
    # Determine day of week
    #
    # Monday = 0
    # Tuesday = 1
    # Wednesday = 2
    # Thursday = 3
    # Friday = 4
    # Saturday = 5
    # Sunday = 6
    # --------------------------------------------------------

    day_of_week = booking_data.booking_date.weekday()

    # --------------------------------------------------------
    # Check provider working day and service category availability
    # --------------------------------------------------------

    availability = (
        db.query(ProviderAvailability)
        .filter(
            ProviderAvailability.provider_id == provider.id,
            ProviderAvailability.category_id == category.id,
            ProviderAvailability.day_of_week == day_of_week,
            ProviderAvailability.is_available.is_(True),
            ProviderAvailability.start_time.isnot(None),
            ProviderAvailability.end_time.isnot(None),
            ProviderAvailability.start_time <= booking_data.booking_time,
            ProviderAvailability.end_time > booking_data.booking_time,
        )
        .first()
    )

    if not availability:
        raise HTTPException(
            status_code=400,
            detail=(
                "Provider is not available for the selected service category, day, "
                "or time."
            )
        )

    # --------------------------------------------------------
    # Check for conflicting booking
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
        raise HTTPException(
            status_code=400,
            detail="Provider already has a booking at this date and time."
        )

    # --------------------------------------------------------
    # Create booking
    # --------------------------------------------------------

    booking = Booking(
        customer_id=current_user.id,
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

    return {
        "message": "Booking created successfully.",
        "booking": {
            "id": booking.id,
            "customer_id": booking.customer_id,
            "provider_id": booking.provider_id,
            "provider_name": f"{provider.user.first_name} {provider.user.last_name}" if provider.user else None,
            "provider_phone": provider.user.phone if provider.user else None,
            "provider_profile_picture": provider.profile_picture,
            "category_id": booking.category_id,
            "category_name": category.name,
            "booking_date": booking.booking_date,
            "booking_time": booking.booking_time,
            "county": booking.county,
            "town": booking.town,
            "address": booking.address,
            "description": booking.description,
            "status": booking.status,
            "created_at": booking.created_at,
            "updated_at": booking.updated_at
        }
    }


# ============================================================
# GET SINGLE BOOKING
# ============================================================

@router.get("/{booking_id}")
def get_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a booking.

    Only the customer who created the booking,
    the provider receiving the booking, or an admin
    can view it.
    """

    booking = (
        db.query(Booking)
        .filter(
            Booking.id == booking_id
        )
        .first()
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found."
        )

    # --------------------------------------------------------
    # Authorization
    # --------------------------------------------------------

    provider = (
        db.query(Provider)
        .filter(
            Provider.id == booking.provider_id
        )
        .first()
    )

    is_customer = (
        booking.customer_id == current_user.id
    )

    is_provider = (
        provider is not None
        and provider.user_id == current_user.id
    )

    if not (
        is_customer
        or is_provider
        or current_user.is_admin
    ):
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to view this booking."
        )

    return {
        "id": booking.id,
        "customer_id": booking.customer_id,
        "provider_id": booking.provider_id,
        "provider_name": f"{provider.user.first_name} {provider.user.last_name}" if provider.user else None,
        "provider_phone": provider.user.phone if provider.user else None,
        "provider_profile_picture": provider.profile_picture,
        "customer_name": f"{booking.customer.first_name} {booking.customer.last_name}" if booking.customer else None,
        "customer_phone": booking.customer.phone if booking.customer else None,
        "customer_profile_picture": booking.customer.profile_picture if booking.customer else None,
        "category_id": booking.category_id,
        "category_name": booking.category.name if booking.category else None,
        "booking_date": booking.booking_date,
        "booking_time": booking.booking_time,
        "county": booking.county,
        "town": booking.town,
        "address": booking.address,
        "description": booking.description,
        "status": booking.status,
        "created_at": booking.created_at,
        "updated_at": booking.updated_at
    }


# ============================================================
# GET MY CUSTOMER BOOKINGS
# ============================================================

@router.get("/customer/me")
def get_my_customer_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all bookings created by the authenticated customer.
    """

    bookings = (
        db.query(Booking)
        .filter(
            Booking.customer_id == current_user.id
        )
        .order_by(
            Booking.created_at.desc()
        )
        .all()
    )

    return [
        {
            "id": booking.id,
            "customer_id": booking.customer_id,
            "provider_id": booking.provider_id,
            "provider_name": f"{booking.provider.user.first_name} {booking.provider.user.last_name}" if booking.provider and booking.provider.user else None,
            "provider_phone": booking.provider.user.phone if booking.provider and booking.provider.user else None,
            "provider_profile_picture": booking.provider.profile_picture if booking.provider else None,
            "category_id": booking.category_id,
            "booking_date": booking.booking_date,
            "booking_time": booking.booking_time,
            "county": booking.county,
            "town": booking.town,
            "address": booking.address,
            "description": booking.description,
            "status": booking.status,
            "created_at": booking.created_at,
            "updated_at": booking.updated_at
        }
        for booking in bookings
    ]


# ============================================================
# GET CUSTOMER BOOKINGS BY ID
# ============================================================

@router.get("/customer/{customer_id}")
def get_customer_bookings(
    customer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get customer bookings.

    A customer can only view their own bookings.
    Admins can view any customer's bookings.
    """

    if (
        current_user.id != customer_id
        and not current_user.is_admin
    ):
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to view these bookings."
        )

    customer = (
        db.query(User)
        .filter(
            User.id == customer_id
        )
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found."
        )

    bookings = (
        db.query(Booking)
        .filter(
            Booking.customer_id == customer_id
        )
        .order_by(
            Booking.created_at.desc()
        )
        .all()
    )

    return [
        {
            "id": booking.id,
            "customer_id": booking.customer_id,
            "provider_id": booking.provider_id,
            "category_id": booking.category_id,
            "booking_date": booking.booking_date,
            "booking_time": booking.booking_time,
            "county": booking.county,
            "town": booking.town,
            "address": booking.address,
            "description": booking.description,
            "status": booking.status,
            "created_at": booking.created_at,
            "updated_at": booking.updated_at
        }
        for booking in bookings
    ]


# ============================================================
# GET MY PROVIDER BOOKINGS
# ============================================================

@router.get("/provider/me")
def get_my_provider_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all bookings received by the authenticated provider.
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

    bookings = (
        db.query(Booking)
        .filter(
            Booking.provider_id == provider.id
        )
        .order_by(
            Booking.created_at.desc()
        )
        .all()
    )

    return [
        {
            "id": booking.id,
            "customer_id": booking.customer_id,
            "provider_id": booking.provider_id,
            "customer_name": f"{booking.customer.first_name} {booking.customer.last_name}" if booking.customer else None,
            "customer_phone": booking.customer.phone if booking.customer else None,
            "customer_profile_picture": booking.customer.profile_picture if booking.customer else None,
            "category_id": booking.category_id,
            "booking_date": booking.booking_date,
            "booking_time": booking.booking_time,
            "county": booking.county,
            "town": booking.town,
            "address": booking.address,
            "description": booking.description,
            "status": booking.status,
            "created_at": booking.created_at,
            "updated_at": booking.updated_at
        }
        for booking in bookings
    ]


# ============================================================
# GET PROVIDER BOOKINGS BY ID
# ============================================================

@router.get("/provider/{provider_id}")
def get_provider_bookings(
    provider_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get provider bookings.

    Only the provider themselves or an admin
    can access these bookings.
    """

    provider = (
        db.query(Provider)
        .filter(
            Provider.id == provider_id
        )
        .first()
    )

    if not provider:
        raise HTTPException(
            status_code=404,
            detail="Provider not found."
        )

    if (
        provider.user_id != current_user.id
        and not current_user.is_admin
    ):
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to view these bookings."
        )

    bookings = (
        db.query(Booking)
        .filter(
            Booking.provider_id == provider_id
        )
        .order_by(
            Booking.created_at.desc()
        )
        .all()
    )

    return [
        {
            "id": booking.id,
            "customer_id": booking.customer_id,
            "provider_id": booking.provider_id,
            "category_id": booking.category_id,
            "booking_date": booking.booking_date,
            "booking_time": booking.booking_time,
            "county": booking.county,
            "town": booking.town,
            "address": booking.address,
            "description": booking.description,
            "status": booking.status,
            "created_at": booking.created_at,
            "updated_at": booking.updated_at
        }
        for booking in bookings
    ]


# ============================================================
# ACCEPT BOOKING
# ============================================================

@router.put("/{booking_id}/accept")
def accept_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Accept a pending booking.

    Only the provider receiving the booking can accept it.
    """

    booking = (
        db.query(Booking)
        .filter(
            Booking.id == booking_id
        )
        .first()
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found."
        )

    provider = (
        db.query(Provider)
        .filter(
            Provider.id == booking.provider_id
        )
        .first()
    )

    if not provider:
        raise HTTPException(
            status_code=404,
            detail="Provider not found."
        )

    if provider.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the assigned provider can accept this booking."
        )

    if booking.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=(
                f"Only pending bookings can be accepted. "
                f"Current status: {booking.status}."
            )
        )

    booking.status = "accepted"

    db.commit()
    db.refresh(booking)
    # Generate acceptance document and attempt to email customer
    try:
        customer = (
            db.query(User)
            .filter(User.id == booking.customer_id)
            .first()
        )

        category_name = booking.category.name if booking.category else ""
        provider = (
            db.query(Provider)
            .filter(Provider.id == booking.provider_id)
            .first()
        )

        if customer and provider:
            pdf_bytes = document_service.generate_booking_acceptance_pdf(booking, provider, customer, category_name)
            email_error = None
        else:
            pdf_bytes = None
            email_error = "customer or provider not available"
    except Exception:
        pdf_bytes = None
        email_error = "error generating acceptance document"

    return {
        "message": "Booking accepted successfully.",
        "booking": {
            "id": booking.id,
            "status": booking.status
        },
        "acceptance_document_email": None,
        "acceptance_document_url": f"/bookings/{booking.id}/acceptance_document"
    }


@router.get("/{booking_id}/acceptance_document")
def get_acceptance_document(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return the booking acceptance document as an attachment.

    Only the customer, the provider, or an admin can download it.
    """
    booking = (
        db.query(Booking)
        .filter(
            Booking.id == booking_id
        )
        .first()
    )

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")

    provider = (
        db.query(Provider)
        .filter(Provider.id == booking.provider_id)
        .first()
    )

    is_customer = booking.customer_id == current_user.id
    is_provider = provider is not None and provider.user_id == current_user.id

    if not (is_customer or is_provider or current_user.is_admin):
        raise HTTPException(status_code=403, detail="You do not have permission to view this document.")

    customer = (
        db.query(User)
        .filter(User.id == booking.customer_id)
        .first()
    )

    category_name = booking.category.name if booking.category else ""

    if not customer or not provider:
        raise HTTPException(status_code=500, detail="Unable to build acceptance document.")

    pdf_bytes = document_service.generate_booking_acceptance_pdf(booking, provider, customer, category_name)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=booking_{booking.id}.pdf"}
    )


# ============================================================
# REJECT BOOKING
# ============================================================

@router.put("/{booking_id}/reject")
def reject_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Reject a pending booking.

    Only the provider receiving the booking can reject it.
    """

    booking = (
        db.query(Booking)
        .filter(
            Booking.id == booking_id
        )
        .first()
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found."
        )

    provider = (
        db.query(Provider)
        .filter(
            Provider.id == booking.provider_id
        )
        .first()
    )

    if not provider:
        raise HTTPException(
            status_code=404,
            detail="Provider not found."
        )

    if provider.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the assigned provider can reject this booking."
        )

    if booking.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=(
                f"Only pending bookings can be rejected. "
                f"Current status: {booking.status}."
            )
        )

    booking.status = "rejected"

    db.commit()
    db.refresh(booking)

    return {
        "message": "Booking rejected successfully.",
        "booking": {
            "id": booking.id,
            "status": booking.status
        }
    }


# ============================================================
# COMPLETE BOOKING
# ============================================================

@router.put("/{booking_id}/complete")
def complete_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark an accepted booking as completed.

    Only the assigned provider can complete it.
    """

    booking = (
        db.query(Booking)
        .filter(
            Booking.id == booking_id
        )
        .first()
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found."
        )

    provider = (
        db.query(Provider)
        .filter(
            Provider.id == booking.provider_id
        )
        .first()
    )

    if not provider:
        raise HTTPException(
            status_code=404,
            detail="Provider not found."
        )

    if provider.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the assigned provider can complete this booking."
        )

    if booking.status != "accepted":
        raise HTTPException(
            status_code=400,
            detail=(
                f"Only accepted bookings can be completed. "
                f"Current status: {booking.status}."
            )
        )

    booking.status = "completed"

    # Update provider completed jobs count
    provider.completed_jobs = (
        provider.completed_jobs + 1
    )

    db.commit()
    db.refresh(booking)
    db.refresh(provider)

    return {
        "message": "Booking completed successfully.",
        "booking": {
            "id": booking.id,
            "status": booking.status
        },
        "provider": {
            "id": provider.id,
            "completed_jobs": provider.completed_jobs
        }
    }


# ============================================================
# UPDATE BOOKING STATUS
# ============================================================

@router.put("/{booking_id}/status")
def update_booking_status(
    booking_id: UUID,
    status_update: BookingStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    General booking status update.

    This endpoint is restricted so customers cannot
    arbitrarily change booking statuses.

    Providers can change:
    pending -> accepted/rejected
    accepted -> completed

    Customers can change:
    pending/accepted -> cancelled

    Admins can update any valid status.
    """

    allowed_statuses = {
        "pending",
        "accepted",
        "rejected",
        "cancelled",
        "completed"
    }

    status = status_update.status.lower()

    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid booking status. "
                "Allowed values: pending, accepted, "
                "rejected, cancelled, completed."
            )
        )

    booking = (
        db.query(Booking)
        .filter(
            Booking.id == booking_id
        )
        .first()
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found."
        )

    provider = (
        db.query(Provider)
        .filter(
            Provider.id == booking.provider_id
        )
        .first()
    )

    is_customer = (
        booking.customer_id == current_user.id
    )

    is_provider = (
        provider is not None
        and provider.user_id == current_user.id
    )

    # --------------------------------------------------------
    # Admin
    # --------------------------------------------------------

    if current_user.is_admin:
        booking.status = status

    # --------------------------------------------------------
    # Customer
    # --------------------------------------------------------

    elif is_customer:

        if status != "cancelled":
            raise HTTPException(
                status_code=403,
                detail="Customers can only cancel their bookings."
            )

        if booking.status in {
            "completed",
            "rejected",
            "cancelled"
        }:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"A booking with status "
                    f"'{booking.status}' cannot be cancelled."
                )
            )

        booking.status = "cancelled"

    # --------------------------------------------------------
    # Provider
    # --------------------------------------------------------

    elif is_provider:

        valid_provider_transitions = {
            "pending": {"accepted", "rejected"},
            "accepted": {"completed"},
        }

        allowed_transitions = valid_provider_transitions.get(
            booking.status,
            set()
        )

        if status not in allowed_transitions:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Provider cannot change booking from "
                    f"'{booking.status}' to '{status}'."
                )
            )

        booking.status = status

        if status == "completed":
            provider.completed_jobs += 1

    # --------------------------------------------------------
    # No permission
    # --------------------------------------------------------

    else:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to update this booking."
        )

    db.commit()
    db.refresh(booking)

    return {
        "message": "Booking status updated successfully.",
        "booking": {
            "id": booking.id,
            "customer_id": booking.customer_id,
            "provider_id": booking.provider_id,
            "category_id": booking.category_id,
            "booking_date": booking.booking_date,
            "booking_time": booking.booking_time,
            "status": booking.status
        }
    }


# ============================================================
# CANCEL BOOKING
# ============================================================

@router.delete("/{booking_id}")
def cancel_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel a booking.

    Only:
    - The customer who created it
    - The assigned provider
    - An admin

    can cancel the booking.

    The booking remains in the database.
    Only its status changes to 'cancelled'.
    """

    booking = (
        db.query(Booking)
        .filter(
            Booking.id == booking_id
        )
        .first()
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found."
        )

    provider = (
        db.query(Provider)
        .filter(
            Provider.id == booking.provider_id
        )
        .first()
    )

    is_customer = (
        booking.customer_id == current_user.id
    )

    is_provider = (
        provider is not None
        and provider.user_id == current_user.id
    )

    is_admin = current_user.is_admin

    if not (
        is_customer
        or is_provider
        or is_admin
    ):
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to cancel this booking."
        )

    if booking.status == "completed":
        raise HTTPException(
            status_code=400,
            detail="A completed booking cannot be cancelled."
        )

    if booking.status == "cancelled":
        raise HTTPException(
            status_code=400,
            detail="Booking is already cancelled."
        )

    if booking.status == "rejected":
        raise HTTPException(
            status_code=400,
            detail="A rejected booking cannot be cancelled."
        )

    booking.status = "cancelled"

    db.commit()
    db.refresh(booking)

    return {
        "message": "Booking cancelled successfully.",
        "booking": {
            "id": booking.id,
            "status": booking.status
        }
    }