from app.db.database import Base

# Import all models so SQLAlchemy registers them
from app.models.user import User
from app.models.provider import Provider
from app.models.category import Category
from app.models.provider_category import ProviderCategory
from app.models.provider_availability import ProviderAvailability
from app.models.booking import Booking

__all__ = [
    "Base",
    "User",
    "Provider",
    "Category",
    "ProviderCategory",
    "ProviderAvailability",
    "Booking",
]