import uuid

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Time,
    Boolean,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class ProviderAvailability(Base):
    __tablename__ = "provider_availability"

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