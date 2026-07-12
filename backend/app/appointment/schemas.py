import uuid
from pydantic import BaseModel
from datetime import datetime

class SlotHoldRequest(BaseModel):
    slot_id: uuid.UUID

class SlotHoldResponse(BaseModel):
    slot_id: uuid.UUID
    status: str
    held_until: datetime
    ttl_seconds: int

    class Config:
        from_attributes = True
