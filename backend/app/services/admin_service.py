from sqlalchemy.orm import Session

from app.models.provider import Provider
from app.models.user import User


def get_pending_provider_applications(db: Session):
    providers = (
        db.query(Provider)
        .filter(Provider.approved == False)
        .all()
    )

    results = []

    for provider in providers:
        user = provider.user

        results.append({
            "id": str(provider.id),
            "user_id": str(user.id),

            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone,

            "bio": provider.bio,
            "county": provider.county,
            "town": provider.town,

            "experience_years": provider.experience_years,
            "hourly_rate": provider.hourly_rate,
            "daily_rate": provider.daily_rate,

            "approved": provider.approved
        })

    return results


def approve_provider(
    db: Session,
    provider_id: str
):

    provider = (
        db.query(Provider)
        .filter(Provider.id == provider_id)
        .first()
    )

    if not provider:
        raise ValueError("Provider application not found.")

    provider.approved = True

    if provider.user:
        provider.user.is_provider = True
        db.add(provider.user)

    db.commit()

    db.refresh(provider)
    if provider.user:
        db.refresh(provider.user)

    return provider