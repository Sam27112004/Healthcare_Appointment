from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class Specialization(Base):
    __tablename__ = "specialization"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    
    # updated_at is in Base, but the schema doesn't explicitly require it for specialization.
    # It's inherited from Base, which is fine and often preferred.
