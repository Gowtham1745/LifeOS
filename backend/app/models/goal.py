import uuid
from typing import Optional, List
from datetime import date
from sqlalchemy import String, Text, Boolean, Float, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin


class Goal(Base, TimestampMixin):
    __tablename__ = "goals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), default="Career", index=True, nullable=False)
    target_value: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    current_value: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), default="%", nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    target_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="active", index=True, nullable=False)  # active, completed, paused, cancelled

    user: Mapped["User"] = relationship("User", back_populates="goals")
    milestones: Mapped[List["GoalMilestone"]] = relationship("GoalMilestone", back_populates="goal", cascade="all, delete-orphan")


class GoalMilestone(Base, TimestampMixin):
    __tablename__ = "goal_milestones"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    goal_id: Mapped[str] = mapped_column(String(36), ForeignKey("goals.id", ondelete="CASCADE"), index=True, nullable=False)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    target_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    goal: Mapped["Goal"] = relationship("Goal", back_populates="milestones")
