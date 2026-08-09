from uuid import UUID

from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def create_category(
    db: Session,
    category: CategoryCreate
):
    existing = (
        db.query(Category)
        .filter(Category.name == category.name)
        .first()
    )

    if existing:
        raise Exception("Category already exists.")

    new_category = Category(
        name=category.name,
        description=category.description
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


def get_categories(db: Session):
    return (
        db.query(Category)
        .order_by(Category.name)
        .all()
    )


def get_category(
    db: Session,
    category_id: UUID
):
    return (
        db.query(Category)
        .filter(Category.id == category_id)
        .first()
    )


def update_category(
    db: Session,
    category_id: UUID,
    data: CategoryUpdate
):
    category = get_category(db, category_id)

    if not category:
        return None

    if data.name is not None:
        category.name = data.name

    if data.description is not None:
        category.description = data.description

    db.commit()
    db.refresh(category)

    return category


def delete_category(
    db: Session,
    category_id: UUID
):
    category = get_category(db, category_id)

    if not category:
        return False

    db.delete(category)
    db.commit()

    return True