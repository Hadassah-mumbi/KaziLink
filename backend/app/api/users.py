import os
import uuid

from fastapi import APIRouter, Depends, Request, File, UploadFile, Form, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": str(current_user.id),
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "phone": current_user.phone,
        "profile_picture": current_user.profile_picture,

        "is_provider": current_user.is_provider,
        "is_admin": current_user.is_admin
    }



@router.put("/me")
async def update_me(
    request: Request,
    first_name: str | None = Form(None),
    last_name: str | None = Form(None),
    phone: str | None = Form(None),
    profile_picture: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Update simple fields
    changed = False
    if first_name is not None:
        current_user.first_name = first_name
        changed = True
    if last_name is not None:
        current_user.last_name = last_name
        changed = True
    if phone is not None:
        current_user.phone = phone
        changed = True

    # Handle profile picture upload
    if profile_picture is not None:
        uploads_dir = os.path.join(os.getcwd(), "uploads")
        os.makedirs(uploads_dir, exist_ok=True)

        filename = f"{uuid.uuid4().hex}{os.path.splitext(profile_picture.filename)[1]}"
        file_path = os.path.join(uploads_dir, filename)

        contents = await profile_picture.read()
        try:
            with open(file_path, "wb") as f:
                f.write(contents)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to save uploaded file.")

        # Build a URL to the uploaded file using the request base URL
        base = str(request.base_url).rstrip("/")
        current_user.profile_picture = f"{base}/uploads/{filename}"
        changed = True

    if changed:
        db.add(current_user)
        db.commit()
        db.refresh(current_user)

    return {
        "id": str(current_user.id),
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "phone": current_user.phone,
        "is_provider": current_user.is_provider,
        "is_admin": current_user.is_admin,
        "profile_picture": current_user.profile_picture,
    }