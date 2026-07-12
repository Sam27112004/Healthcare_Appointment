import uuid
from pydantic import BaseModel, Field

class SpecializationCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: str | None = None

class SpecializationUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100)
    description: str | None = None

# We can reuse the SpecializationResponse or define an Admin specific one
class SpecializationResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None

    class Config:
        from_attributes = True
