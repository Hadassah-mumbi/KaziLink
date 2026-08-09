import uuid

from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class ProviderCategory(Base):
    __tablename__ = "provider_categories"

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

    provider = relationship(
        "Provider",
        back_populates="categories"
    )

    category = relationship(
        "Category",
        back_populates="providers"
    )

    __table_args__ = (
        UniqueConstraint(
            "provider_id",
            "category_id",
            name="uq_provider_category"
        ),
    )