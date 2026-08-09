from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse
)
from app.services.category_service import (
    create_category,
    get_categories,
    get_category,
    update_category,
    delete_category
)

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.post(
    "",
    response_model=CategoryResponse
)
def create(
    category: CategoryCreate,
    db: Session = Depends(get_db)
):
    try:
        return create_category(db, category)

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get(
    "",
    response_model=list[CategoryResponse]
)
def get_all(
    db: Session = Depends(get_db)
):
    return get_categories(db)


@router.get(
    "/{category_id}",
    response_model=CategoryResponse
)
def get_one(
    category_id: UUID,
    db: Session = Depends(get_db)
):
    category = get_category(db, category_id)

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found."
        )

    return category


@router.put(
    "/{category_id}",
    response_model=CategoryResponse
)
def update(
    category_id: UUID,
    data: CategoryUpdate,
    db: Session = Depends(get_db)
):
    category = update_category(
        db,
        category_id,
        data
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found."
        )

    return category


@router.delete(
    "/{category_id}"
)
def delete(
    category_id: UUID,
    db: Session = Depends(get_db)
):
    deleted = delete_category(
        db,
        category_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Category not found."
        )

    return {
        "message": "Category deleted successfully."
    }