from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import hash_password


def create_default_admin(db: Session):
    """
    Creates the default administrator account if one doesn't exist.
    """

    existing_admin = (
        db.query(User)
        .filter(User.is_admin == True)
        .first()
    )

    if existing_admin:
        return

    admin = User(
        first_name="System",
        last_name="Administrator",
        email="admin@kazilink.com",
        phone="0700000000",
        password_hash=hash_password("Admin123!"),
        is_admin=True,
        is_provider=False,
        is_active=True,
    )

    db.add(admin)
    db.commit()

    print("✅ Default admin account created.")