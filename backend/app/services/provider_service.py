import math
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.provider import Provider
from app.models.user import User
from app.models.category import Category
from app.models.provider_category import ProviderCategory

from app.schemas.provider import ProviderCreate


# ============================================================
# CALCULATE DISTANCE
# ============================================================

def calculate_distance_km(
    latitude1: float,
    longitude1: float,
    latitude2: float,
    longitude2: float
) -> float:
    """
    Calculate the distance between two geographic coordinates
    using the Haversine formula.

    Returns the distance in kilometres.
    """

    earth_radius_km = 6371.0

    lat1 = math.radians(latitude1)
    lon1 = math.radians(longitude1)

    lat2 = math.radians(latitude2)
    lon2 = math.radians(longitude2)

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return earth_radius_km * c


# ============================================================
# CREATE PROVIDER PROFILE
# ============================================================

def create_provider_profile(
    db: Session,
    user: User,
    provider_data: ProviderCreate
):
    """
    Create a provider profile for a user.

    Prevents the same user from creating
    multiple provider profiles.
    """

    existing = (
        db.query(Provider)
        .filter(
            Provider.user_id == user.id
        )
        .first()
    )

    if existing:
        raise ValueError(
            "You have already applied to become a provider."
        )

    provider = Provider(
        user_id=user.id,
        bio=provider_data.bio,
        county=provider_data.county,
        town=provider_data.town,
        latitude=provider_data.latitude,
        longitude=provider_data.longitude,
        experience_years=provider_data.experience_years,
        hourly_rate=provider_data.hourly_rate,
        daily_rate=provider_data.daily_rate,
    )

    db.add(provider)
    db.commit()
    db.refresh(provider)

    return provider


# ============================================================
# ADD PROVIDER CATEGORY
# ============================================================

def add_provider_category(
    db: Session,
    provider: Provider,
    category_id: UUID
):
    """
    Add a service/category to a provider.
    """

    category = (
        db.query(Category)
        .filter(
            Category.id == category_id
        )
        .first()
    )

    if not category:
        raise ValueError(
            "Category not found."
        )

    existing = (
        db.query(ProviderCategory)
        .filter(
            ProviderCategory.provider_id == provider.id,
            ProviderCategory.category_id == category.id
        )
        .first()
    )

    if existing:
        raise ValueError(
            "Provider is already registered for this service."
        )

    provider_category = ProviderCategory(
        provider_id=provider.id,
        category_id=category.id
    )

    db.add(provider_category)
    db.commit()
    db.refresh(provider_category)

    return provider_category


# ============================================================
# GET PROVIDER CATEGORIES
# ============================================================

def get_provider_categories(
    db: Session,
    provider: Provider
):
    """
    Get all services/categories belonging to a provider.
    """

    return (
        db.query(ProviderCategory)
        .join(
            Category,
            ProviderCategory.category_id == Category.id
        )
        .filter(
            ProviderCategory.provider_id == provider.id
        )
        .order_by(Category.name)
        .all()
    )


# ============================================================
# REMOVE PROVIDER CATEGORY
# ============================================================

def remove_provider_category(
    db: Session,
    provider: Provider,
    category_id: UUID
):
    """
    Remove a service/category from a provider.
    """

    provider_category = (
        db.query(ProviderCategory)
        .filter(
            ProviderCategory.provider_id == provider.id,
            ProviderCategory.category_id == category_id
        )
        .first()
    )

    if not provider_category:
        return False

    db.delete(provider_category)
    db.commit()

    return True


# ============================================================
# SEARCH / FILTER PROVIDERS
# ============================================================

def search_providers(
    db: Session,
    county: str | None = None,
    town: str | None = None,
    category_id: UUID | None = None,
    min_hourly_rate: float | None = None,
    max_hourly_rate: float | None = None,
    available: bool | None = None,
    min_experience_years: int | None = None,
    max_experience_years: int | None = None,
):
    """
    Search for approved providers using optional filters.

    Only approved providers are returned.

    Supported filters:

    - county
    - town
    - category_id
    - min_hourly_rate
    - max_hourly_rate
    - available
    - min_experience_years
    - max_experience_years

    Results are sorted by average rating,
    highest first.
    """

    query = (
        db.query(Provider)
        .filter(
            Provider.approved.is_(True)
        )
    )

    # --------------------------------------------------------
    # COUNTY
    # --------------------------------------------------------

    if county:
        query = query.filter(
            Provider.county.ilike(f"%{county}%")
        )

    # --------------------------------------------------------
    # TOWN
    # --------------------------------------------------------

    if town:
        query = query.filter(
            Provider.town.ilike(f"%{town}%")
        )

    # --------------------------------------------------------
    # CATEGORY
    # --------------------------------------------------------

    if category_id:
        query = (
            query
            .join(
                ProviderCategory,
                ProviderCategory.provider_id == Provider.id
            )
            .filter(
                ProviderCategory.category_id == category_id
            )
        )

    # --------------------------------------------------------
    # MINIMUM HOURLY RATE
    # --------------------------------------------------------

    if min_hourly_rate is not None:
        query = query.filter(
            Provider.hourly_rate >= min_hourly_rate
        )

    # --------------------------------------------------------
    # MAXIMUM HOURLY RATE
    # --------------------------------------------------------

    if max_hourly_rate is not None:
        query = query.filter(
            Provider.hourly_rate <= max_hourly_rate
        )

    # --------------------------------------------------------
    # AVAILABILITY
    # --------------------------------------------------------

    if available is not None:
        query = query.filter(
            Provider.available == available
        )

    # --------------------------------------------------------
    # MINIMUM EXPERIENCE
    # --------------------------------------------------------

    if min_experience_years is not None:
        query = query.filter(
            Provider.experience_years >= min_experience_years
        )

    # --------------------------------------------------------
    # MAXIMUM EXPERIENCE
    # --------------------------------------------------------

    if max_experience_years is not None:
        query = query.filter(
            Provider.experience_years <= max_experience_years
        )

    # --------------------------------------------------------
    # SORTING
    # --------------------------------------------------------

    query = query.order_by(
        Provider.average_rating.desc(),
        Provider.total_reviews.desc()
    )

    return query.all()


# ============================================================
# FIND NEARBY PROVIDERS
# ============================================================

def find_nearby_providers(
    db: Session,
    category_id: UUID,
    customer_latitude: float,
    customer_longitude: float
):
    """
    Find approved and available providers who:

    1. Offer the requested category.
    2. Have a valid location.
    3. Are within their service radius.
    4. Are sorted from nearest to farthest.
    """

    providers = (
        db.query(Provider)
        .join(
            ProviderCategory,
            ProviderCategory.provider_id == Provider.id
        )
        .filter(
            ProviderCategory.category_id == category_id,
            Provider.approved.is_(True),
            Provider.available.is_(True),
            Provider.latitude.isnot(None),
            Provider.longitude.isnot(None),
        )
        .all()
    )

    nearby_providers = []

    for provider in providers:

        distance_km = calculate_distance_km(
            customer_latitude,
            customer_longitude,
            provider.latitude,
            provider.longitude,
        )

        if distance_km <= provider.service_radius_km:

            nearby_providers.append(
                {
                    "provider": provider,
                    "distance_km": round(
                        distance_km,
                        2
                    ),
                }
            )

    nearby_providers.sort(
        key=lambda result: result["distance_km"]
    )

    return nearby_providers