import uuid
from typing import Optional, List
from datetime import date
from sqlalchemy import String, Text, Boolean, Float, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin


class Habit(Base, TimestampMixin):
    __tablename__ = "habits"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    frequency: Mapped[str] = mapped_column(String(30), default="daily", nullable=False)  # daily, weekly, custom
    target_value: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), default="times", nullable=False)  # pages, minutes, km, liters, times
    reminder_time: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    color: Mapped[str] = mapped_column(String(30), default="#6366f1", nullable=False)
    icon: Mapped[str] = mapped_column(String(50), default="check-circle", nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="habits")
    logs: Mapped[List["HabitLog"]] = relationship("HabitLog", back_populates="habit", cascade="all, delete-orphan", order_by="desc(HabitLog.log_date)")


class HabitLog(Base, TimestampMixin):
    __tablename__ = "habit_logs"
    __table_args__ = (
        UniqueConstraint("habit_id", "log_date", name="uq_habit_log_date"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    habit_id: Mapped[str] = mapped_column(String(36), ForeignKey("habits.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    log_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    completed_value: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    habit: Mapped["Habit"] = relationship("Habit", back_populates="logs")
