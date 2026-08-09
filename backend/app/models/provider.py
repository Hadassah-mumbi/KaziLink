import uuid

from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    Boolean,
    ForeignKey,
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class Provider(Base):
    __tablename__ = "providers"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    bio = Column(
        String,
        nullable=False
    )

    county = Column(
        String(100),
        nullable=False
    )

    town = Column(
        String(100),
        nullable=False
    )

    latitude = Column(
        Float,
        nullable=True
    )

    longitude = Column(
        Float,
        nullable=True
    )

    service_radius_km = Column(
        Float,
        nullable=False,
        default=10.0
    )

    experience_years = Column(
        Integer,
        nullable=False
    )

    hourly_rate = Column(
        Float,
        nullable=False
    )

    daily_rate = Column(
        Float,
        nullable=False
    )

    approved = Column(
        Boolean,
        default=False,
        nullable=False
    )

    available = Column(
        Boolean,
        default=True,
        nullable=False
    )

    average_rating = Column(
        Float,
        default=0.0,
        nullable=False
    )

    total_reviews = Column(
        Integer,
        default=0,
        nullable=False
    )

    completed_jobs = Column(
        Integer,
        default=0,
        nullable=False
    )

    profile_picture = Column(
        String(500),
        nullable=True
    )

    national_id_document = Column(
        String(500),
        nullable=True
    )

    good_conduct_certificate = Column(
        String(500),
        nullable=True
    )

    user = relationship(
        "User",
        back_populates="provider_profile"
    )

    categories = relationship(
        "ProviderCategory",
        back_populates="provider",
        cascade="all, delete-orphan"
    )

    availability = relationship(
        "ProviderAvailability",
        back_populates="provider",
        cascade="all, delete-orphan"
    )