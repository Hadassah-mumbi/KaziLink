import uuid

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Time,
    Boolean,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class ProviderAvailability(Base):
    __tablename__ = "provider_availability"
    __table_args__ = (
        UniqueConstraint(
            "provider_id",
            "category_id",
            "day_of_week",
            "start_time",
            "end_time",
            name="uq_provider_category_availability"
        ),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    provider_id = Column(
        UUID(as_uuid=True),
        ForeignKey("providers.id"),
        nullable=False
    )

    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id"),
        nullable=False
    )

    # 0 = Monday
    # 1 = Tuesday
    # 2 = Wednesday
    # 3 = Thursday
    # 4 = Friday
    # 5 = Saturday
    # 6 = Sunday

    day_of_week = Column(
        Integer,
        nullable=False
    )

    start_time = Column(
        Time,
        nullable=True
    )

    end_time = Column(
        Time,
        nullable=True
    )

    is_available = Column(
        Boolean,
        default=True,
        nullable=False
    )

    provider = relationship(
        "Provider",
        back_populates="availability"
    )

    category = relationship(
        "Category"
    )