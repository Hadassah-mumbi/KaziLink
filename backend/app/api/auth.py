from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.auth import (
    CustomerRegister,
    TokenResponse,
)
from app.services.auth_service import (
    create_customer,
    authenticate_user,
)
from app.core.security import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register/customer")
def register_customer(
    customer: CustomerRegister,
    db: Session = Depends(get_db)
):
    try:
        user = create_customer(db, customer)

        return {
            "message": "Customer registered successfully.",
            "user_id": str(user.id)
        }

    except Exception as e:
        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = authenticate_user(
        db,
        form_data.username,
        form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    token = create_access_token(
        {
            "sub": str(user.id),
            "is_provider": user.is_provider,
            "is_admin": user.is_admin
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }