from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User
from app.models.provider import Provider
from app.models.provider_category import ProviderCategory

from app.schemas.provider import (
    ProviderCreate,
    ProviderResponse,
    ProviderLocationUpdate,
    ServiceRadiusUpdate,
    ServiceLocationRequest,
    NearbyProviderResponse,
    ProviderCategoryAdd,
    ProviderCategoryResponse,
    PublicProviderResponse,
)

from app.services.provider_service import (
    create_provider_profile,
    find_nearby_providers,
    get_provider_categories,
    add_provider_category,
    remove_provider_category,
    search_providers,
)


router = APIRouter(
    prefix="/providers",
    tags=["Providers"]
)


# ============================================================
# APPLY AS PROVIDER
# ============================================================

@router.post(
    "/apply",
    response_model=ProviderResponse
)
def apply_as_provider(
    provider: ProviderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return create_provider_profile(
            db,
            current_user,
            provider
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ============================================================
# GET MY PROVIDER PROFILE
# ============================================================

@router.get(
    "/me",
    response_model=ProviderResponse
)
def get_my_provider_profile(
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

    categories = get_provider_categories(
        db,
        provider
    )

    return {
        "id": provider.id,
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
    }


# ============================================================
# SEARCH / FILTER PROVIDERS
# ============================================================

@router.get(
    "/search",
    response_model=list[PublicProviderResponse]
)
def search_public_providers(
    county: str | None = Query(
        default=None,
        min_length=2,
        max_length=100
    ),
    town: str | None = Query(
        default=None,
        min_length=2,
        max_length=100
    ),
    category_id: UUID | None = Query(
        default=None
    ),
    min_hourly_rate: float | None = Query(
        default=None,
        ge=0
    ),
    max_hourly_rate: float | None = Query(
        default=None,
        ge=0
    ),
    available: bool | None = Query(
        default=None
    ),
    min_experience_years: int | None = Query(
        default=None,
        ge=0
    ),
    max_experience_years: int | None = Query(
        default=None,
        ge=0
    ),
    db: Session = Depends(get_db)
):
    """
    Search and filter approved providers.

    Available filters:

    - county
    - town
    - category_id
    - min_hourly_rate
    - max_hourly_rate
    - available
    - min_experience_years
    - max_experience_years

    Results are sorted by average rating,
    from highest to lowest.
    """

    if (
        min_hourly_rate is not None
        and max_hourly_rate is not None
        and min_hourly_rate > max_hourly_rate
    ):
        raise HTTPException(
            status_code=400,
            detail="min_hourly_rate cannot be greater than max_hourly_rate."
        )

    if (
        min_experience_years is not None
        and max_experience_years is not None
        and min_experience_years > max_experience_years
    ):
        raise HTTPException(
            status_code=400,
            detail="min_experience_years cannot be greater than max_experience_years."
        )

    providers = search_providers(
        db=db,
        county=county,
        town=town,
        category_id=category_id,
        min_hourly_rate=min_hourly_rate,
        max_hourly_rate=max_hourly_rate,
        available=available,
        min_experience_years=min_experience_years,
        max_experience_years=max_experience_years,
    )

    results = []

    for provider in providers:

        categories = get_provider_categories(
            db,
            provider
        )

        results.append(
            {
                "id": provider.id,
                "bio": provider.bio,
                "county": provider.county,
                "town": provider.town,
                "latitude": provider.latitude,
                "longitude": provider.longitude,
                "experience_years": provider.experience_years,
                "hourly_rate": provider.hourly_rate,
                "daily_rate": provider.daily_rate,
                "available": provider.available,
                "average_rating": provider.average_rating,
                "total_reviews": provider.total_reviews,
                "completed_jobs": provider.completed_jobs,
                "profile_picture": provider.profile_picture,
                "services": [
                    {
                        "category_id": item.category.id,
                        "name": item.category.name,
                        "description": item.category.description,
                    }
                    for item in categories
                ],
            }
        )

    return results


# ============================================================
# GET PUBLIC PROVIDER PROFILE
# ============================================================

@router.get(
    "/{provider_id}",
    response_model=PublicProviderResponse
)
def get_public_provider_profile(
    provider_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a provider's public profile.

    Only approved providers can be viewed publicly.
    """

    provider = (
        db.query(Provider)
        .filter(
            Provider.id == provider_id,
            Provider.approved.is_(True)
        )
        .first()
    )

    if not provider:
        raise HTTPException(
            status_code=404,
            detail="Provider not found."
        )

    categories = get_provider_categories(
        db,
        provider
    )

    return {
        "id": provider.id,
        "bio": provider.bio,
        "county": provider.county,
        "town": provider.town,
        "latitude": provider.latitude,
        "longitude": provider.longitude,
        "experience_years": provider.experience_years,
        "hourly_rate": provider.hourly_rate,
        "daily_rate": provider.daily_rate,
        "available": provider.available,
        "average_rating": provider.average_rating,
        "total_reviews": provider.total_reviews,
        "completed_jobs": provider.completed_jobs,
        "profile_picture": provider.profile_picture,
        "services": [
            {
                "category_id": item.category.id,
                "name": item.category.name,
                "description": item.category.description,
            }
            for item in categories
        ],
    }


# ============================================================
# UPDATE MY LOCATION
# ============================================================

@router.put(
    "/me/location",
    response_model=ProviderResponse
)
def update_my_provider_location(
    location: ProviderLocationUpdate,
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

    provider.latitude = location.latitude
    provider.longitude = location.longitude

    db.commit()
    db.refresh(provider)

    categories = get_provider_categories(
        db,
        provider
    )

    return {
        "id": provider.id,
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
    }


# ============================================================
# UPDATE MY SERVICE RADIUS
# ============================================================

@router.put(
    "/me/service-radius",
    response_model=ProviderResponse
)
def update_my_service_radius(
    radius: ServiceRadiusUpdate,
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

    provider.service_radius_km = (
        radius.service_radius_km
    )

    db.commit()
    db.refresh(provider)

    categories = get_provider_categories(
        db,
        provider
    )

    return {
        "id": provider.id,
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
    }


# ============================================================
# ADD MY SERVICE
# ============================================================

@router.post(
    "/me/services",
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
            "category_id": provider_category.category.id,
            "name": provider_category.category.name,
            "description": provider_category.category.description,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ============================================================
# GET MY SERVICES
# ============================================================

@router.get(
    "/me/services",
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

    categories = get_provider_categories(
        db,
        provider
    )

    return [
        {
            "category_id": item.category.id,
            "name": item.category.name,
            "description": item.category.description,
        }
        for item in categories
    ]


# ============================================================
# REMOVE MY SERVICE
# ============================================================

@router.delete(
    "/me/services/{category_id}"
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


# ============================================================
# SEARCH NEARBY PROVIDERS
# ============================================================

@router.post(
    "/search/nearby",
    response_model=list[NearbyProviderResponse]
)
def search_nearby_providers(
    location: ServiceLocationRequest,
    db: Session = Depends(get_db)
):
    """
    Find approved and available providers who offer
    the requested service and are within their
    service radius of the customer's location.

    Results are sorted from nearest to farthest.
    """

    results = find_nearby_providers(
        db,
        location.category_id,
        location.latitude,
        location.longitude
    )

    return [
        {
            **result["provider"].__dict__,
            "distance_km": result["distance_km"]
        }
        for result in results
    ]