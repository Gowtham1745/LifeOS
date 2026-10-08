import uuid
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin


class CalendarEvent(Base, TimestampMixin):
    __tablename__ = "calendar_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reminder_minutes: Mapped[Optional[int]] = mapped_column(Integer, default=15, nullable=True)
    color: Mapped[str] = mapped_column(String(30), default="#6366f1", nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="calendar_events")
