import uuid

from sqlalchemy import (
    Column,
    String,
    Text,
    Date,
    Time,
    DateTime,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    customer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
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

    booking_date = Column(
        Date,
        nullable=False
    )

    booking_time = Column(
        Time,
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

    address = Column(
        String(500),
        nullable=True
    )

    description = Column(
        Text,
        nullable=True
    )

    status = Column(
        String(30),
        nullable=False,
        default="pending"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    customer = relationship(
        "User",
        foreign_keys=[customer_id]
    )

    provider = relationship(
        "Provider",
        foreign_keys=[provider_id]
    )

    category = relationship(
        "Category",
        foreign_keys=[category_id]
    )