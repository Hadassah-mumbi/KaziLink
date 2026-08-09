from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.dependencies import get_current_admin_user

from app.models.user import User
from app.models.provider import Provider

from app.services.provider_service import get_provider_categories


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# ============================================================
# GET ALL PROVIDERS
# ============================================================

@router.get("/providers")
def get_all_providers(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """
    Get all provider profiles.

    Admin only.
    """

    providers = (
        db.query(Provider)
        .order_by(
            Provider.approved,
            Provider.id
        )
        .all()
    )

    results = []

    for provider in providers:

        categories = get_provider_categories(
            db,
            provider
        )

        results.append({
            "id": provider.id,
            "user_id": provider.user_id,
            "bio": provider.bio,
            "county": provider.county,
            "town": provider.town,
            "latitude": provider.latitude,
            "longitude": provider.longitude,
            "service_radius_km": provider.service_radius_km,
            "experience_years": provider.experience_years,
            "hourly_rate": provider.hourly_rate,
            "daily_rate": provider.daily_rate,
            "approved": provider.approved,
            "available": provider.available,
            "average_rating": provider.average_rating,
            "total_reviews": provider.total_reviews,
            "completed_jobs": provider.completed_jobs,
            "profile_picture": provider.profile_picture,
            "national_id_document": provider.national_id_document,
            "good_conduct_certificate": provider.good_conduct_certificate,
            "services": [
                {
                    "category_id": item.category.id,
                    "name": item.category.name,
                    "description": item.category.description,
                }
                for item in categories
            ],
        })

    return results


# ============================================================
# GET PENDING PROVIDERS
# ============================================================

@router.get("/providers/pending")
def get_pending_providers(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """
    Get all provider applications that have not been approved.

    Admin only.
    """

    providers = (
        db.query(Provider)
        .filter(
            Provider.approved.is_(False)
        )
        .order_by(
            Provider.id
        )
        .all()
    )

    results = []

    for provider in providers:

        categories = get_provider_categories(
            db,
            provider
        )

        results.append({
            "id": provider.id,
            "user_id": provider.user_id,
            "bio": provider.bio,
            "county": provider.county,
            "town": provider.town,
            "latitude": provider.latitude,
            "longitude": provider.longitude,
            "service_radius_km": provider.service_radius_km,
            "experience_years": provider.experience_years,
            "hourly_rate": provider.hourly_rate,
            "daily_rate": provider.daily_rate,
            "approved": provider.approved,
            "available": provider.available,
            "average_rating": provider.average_rating,
            "total_reviews": provider.total_reviews,
            "completed_jobs": provider.completed_jobs,
            "profile_picture": provider.profile_picture,
            "national_id_document": provider.national_id_document,
            "good_conduct_certificate": provider.good_conduct_certificate,
            "services": [
                {
                    "category_id": item.category.id,
                    "name": item.category.name,
                    "description": item.category.description,
                }
                for item in categories
            ],
        })

    return results


# ============================================================
# GET SINGLE PROVIDER
# ============================================================

@router.get("/providers/{provider_id}")
def get_provider_for_admin(
    provider_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """
    Get complete provider information for admin review.

    Admin only.
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

    user = (
        db.query(User)
        .filter(
            User.id == provider.user_id
        )
        .first()
    )

    categories = get_provider_categories(
        db,
        provider
    )

    return {
        "provider": {
            "id": provider.id,
            "user_id": provider.user_id,
            "bio": provider.bio,
            "county": provider.county,
            "town": provider.town,
            "latitude": provider.latitude,
            "longitude": provider.longitude,
            "service_radius_km": provider.service_radius_km,
            "experience_years": provider.experience_years,
            "hourly_rate": provider.hourly_rate,
            "daily_rate": provider.daily_rate,
            "approved": provider.approved,
            "available": provider.available,
            "average_rating": provider.average_rating,
            "total_reviews": provider.total_reviews,
            "completed_jobs": provider.completed_jobs,
            "profile_picture": provider.profile_picture,
            "national_id_document": provider.national_id_document,
            "good_conduct_certificate": provider.good_conduct_certificate,
            "services": [
                {
                    "category_id": item.category.id,
                    "name": item.category.name,
                    "description": item.category.description,
                }
                for item in categories
            ],
        },

        "user": {
            "id": user.id if user else None,
            "first_name": user.first_name if user else None,
            "last_name": user.last_name if user else None,
            "email": user.email if user else None,
            "phone": user.phone if user else None,
            "is_provider": user.is_provider if user else None,
            "is_active": user.is_active if user else None,
        }
    }


# ============================================================
# APPROVE PROVIDER
# ============================================================

@router.put("/providers/{provider_id}/approve")
def approve_provider(
    provider_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """
    Approve a provider application.

    Admin only.
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

    if provider.approved:
        raise HTTPException(
            status_code=400,
            detail="Provider is already approved."
        )

    provider.approved = True

    db.commit()
    db.refresh(provider)

    return {
        "message": "Provider approved successfully.",
        "provider": {
            "id": provider.id,
            "user_id": provider.user_id,
            "approved": provider.approved
        }
    }


# ============================================================
# REJECT PROVIDER
# ============================================================

@router.put("/providers/{provider_id}/reject")
def reject_provider(
    provider_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """
    Reject a provider application.

    Admin only.

    Rejection is represented by approved=False.
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

    if not provider.approved:
        raise HTTPException(
            status_code=400,
            detail="Provider is already unapproved."
        )

    provider.approved = False

    db.commit()
    db.refresh(provider)

    return {
        "message": "Provider rejected successfully.",
        "provider": {
            "id": provider.id,
            "user_id": provider.user_id,
            "approved": provider.approved
        }
    }


# ============================================================
# GET ALL USERS
# ============================================================

@router.get("/users")
def get_all_users(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """
    Get all registered users.

    Admin only.
    """

    users = (
        db.query(User)
        .order_by(
            User.created_at.desc()
        )
        .all()
    )

    return [
        {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone,
            "is_provider": user.is_provider,
            "is_admin": user.is_admin,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }
        for user in users
    ]


# ============================================================
# GET SINGLE USER
# ============================================================

@router.get("/users/{user_id}")
def get_user_for_admin(
    user_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """
    Get a single user's information.

    Admin only.
    """

    user = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone": user.phone,
        "is_provider": user.is_provider,
        "is_admin": user.is_admin,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }


# ============================================================
# DEACTIVATE USER
# ============================================================

@router.put("/users/{user_id}/deactivate")
def deactivate_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """
    Deactivate a user account.

    Admin only.
    """

    user = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    if user.id == admin.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot deactivate your own admin account."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="User is already inactive."
        )

    user.is_active = False

    db.commit()
    db.refresh(user)

    return {
        "message": "User deactivated successfully.",
        "user": {
            "id": user.id,
            "email": user.email,
            "is_active": user.is_active
        }
    }


# ============================================================
# ACTIVATE USER
# ============================================================

@router.put("/users/{user_id}/activate")
def activate_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """
    Activate a user account.

    Admin only.
    """

    user = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    if user.is_active:
        raise HTTPException(
            status_code=400,
            detail="User is already active."
        )

    user.is_active = True

    db.commit()
    db.refresh(user)

    return {
        "message": "User activated successfully.",
        "user": {
            "id": user.id,
            "email": user.email,
            "is_active": user.is_active
        }
    }