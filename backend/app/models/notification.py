import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, Text, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime
from app.models.base import Base

class Notification(Base):
    __tablename__ = "notification"

    appointment_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("appointment.id"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    
    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(20), default="email", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)
    
    subject: Mapped[str | None] = mapped_column(String(255))
    body: Mapped[str | None] = mapped_column(Text)
    
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text)
    
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
