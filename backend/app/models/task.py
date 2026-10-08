import uuid
from typing import Optional, List
from datetime import datetime, date
from sqlalchemy import String, Text, Boolean, Integer, Date, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="todo", index=True, nullable=False)  # todo, in_progress, completed, archived
    priority: Mapped[str] = mapped_column(String(20), default="medium", index=True, nullable=False)  # low, medium, high, urgent
    
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    due_time: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(50), default="General", index=True, nullable=True)
    tags: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    estimated_duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # in minutes
    recurrence: Mapped[str] = mapped_column(String(30), default="none", nullable=False)  # none, daily, weekly, monthly
    
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="tasks")
    subtasks: Mapped[List["Subtask"]] = relationship("Subtask", back_populates="task", cascade="all, delete-orphan", order_by="Subtask.position")


class Subtask(Base, TimestampMixin):
    __tablename__ = "subtasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    task: Mapped["Task"] = relationship("Task", back_populates="subtasks")
