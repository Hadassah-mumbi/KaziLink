from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import CustomerRegister
from app.core.security import hash_password, verify_password


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_phone(db: Session, phone: str):
    return db.query(User).filter(User.phone == phone).first()


def create_customer(db: Session, customer: CustomerRegister):

    existing_email = get_user_by_email(db, customer.email)

    if existing_email:
        raise ValueError("Email already exists.")

    existing_phone = get_user_by_phone(db, customer.phone)

    if existing_phone:
        raise ValueError("Phone number already exists.")

    new_user = User(
        first_name=customer.first_name,
        last_name=customer.last_name,
        email=customer.email,
        phone=customer.phone,
        password_hash=hash_password(customer.password),

        # Every new user starts as a customer
        is_provider=False,
        is_admin=False,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def authenticate_user(db: Session, email: str, password: str):

    user = get_user_by_email(db, email)

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user