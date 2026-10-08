import uuid
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin


class FocusSession(Base, TimestampMixin):
    __tablename__ = "focus_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    task_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    
    duration_minutes: Mapped[int] = mapped_column(Integer, default=25, nullable=False)
    session_type: Mapped[str] = mapped_column(String(30), default="pomodoro", nullable=False)  # pomodoro, short_break, long_break
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="focus_sessions")
    task: Mapped[Optional["Task"]] = relationship("Task")
