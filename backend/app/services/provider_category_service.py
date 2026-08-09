from uuid import UUID

from sqlalchemy.orm import Session

from app.models.provider import Provider
from app.models.provider_category import ProviderCategory
from app.models.category import Category


def get_provider_for_user(
    db: Session,
    user_id: UUID
):
    return (
        db.query(Provider)
        .filter(Provider.user_id == user_id)
        .first()
    )


def add_category_to_provider(
    db: Session,
    provider: Provider,
    category_id: UUID
):
    category = (
        db.query(Category)
        .filter(Category.id == category_id)
        .first()
    )

    if not category:
        raise ValueError("Category not found.")

    existing = (
        db.query(ProviderCategory)
        .filter(
            ProviderCategory.provider_id == provider.id,
            ProviderCategory.category_id == category_id
        )
        .first()
    )

    if existing:
        raise ValueError(
            "This category is already assigned to your provider profile."
        )

    provider_category = ProviderCategory(
        provider_id=provider.id,
        category_id=category.id
    )

    db.add(provider_category)
    db.commit()
    db.refresh(provider_category)

    return provider_category


def get_provider_categories(
    db: Session,
    provider: Provider
):
    return (
        db.query(
            ProviderCategory,
            Category
        )
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


def remove_category_from_provider(
    db: Session,
    provider: Provider,
    category_id: UUID
):
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