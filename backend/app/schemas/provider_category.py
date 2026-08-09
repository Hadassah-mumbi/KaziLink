from uuid import UUID

from pydantic import BaseModel, Field


class ProviderCategoryAdd(BaseModel):
    category_id: UUID


class ProviderCategoryResponse(BaseModel):
    id: UUID
    category_id: UUID
    name: str
    description: str | None = None

    model_config = {
        "from_attributes": True
    }