import uuid
from typing import Optional, List
from sqlalchemy import String, Boolean, ForeignKey, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    settings: Mapped[Optional["UserSettings"]] = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    habits: Mapped[List["Habit"]] = relationship("Habit", back_populates="user", cascade="all, delete-orphan")
    goals: Mapped[List["Goal"]] = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    budgets: Mapped[List["Budget"]] = relationship("Budget", back_populates="user", cascade="all, delete-orphan")
    subscriptions: Mapped[List["Subscription"]] = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    calendar_events: Mapped[List["CalendarEvent"]] = relationship("CalendarEvent", back_populates="user", cascade="all, delete-orphan")
    notes: Mapped[List["Note"]] = relationship("Note", back_populates="user", cascade="all, delete-orphan")
    journal_entries: Mapped[List["JournalEntry"]] = relationship("JournalEntry", back_populates="user", cascade="all, delete-orphan")
    focus_sessions: Mapped[List["FocusSession"]] = relationship("FocusSession", back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[List["Notification"]] = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    state: Mapped[Optional["UserState"]] = relationship("UserState", back_populates="user", uselist=False, cascade="all, delete-orphan")


class UserSettings(Base, TimestampMixin):
    __tablename__ = "user_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    
    theme: Mapped[str] = mapped_column(String(20), default="system", nullable=False)  # light, dark, system
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)  # USD, INR, EUR, GBP, etc.
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    working_hours_start: Mapped[str] = mapped_column(String(10), default="09:00", nullable=False)
    working_hours_end: Mapped[str] = mapped_column(String(10), default="18:00", nullable=False)
    notification_preferences: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="settings")
