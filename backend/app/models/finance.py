import uuid
from typing import Optional
from datetime import date
from sqlalchemy import String, Text, Boolean, Float, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin


class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    type: Mapped[str] = mapped_column(String(20), index=True, nullable=False)  # income, expense
    category: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # Food, Travel, Shopping, Bills, Subscriptions, Education, Entertainment, Health, Other
    date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(50), default="Card", nullable=False)  # Card, Cash, UPI, Bank Transfer, Other
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="transactions")


class Budget(Base, TimestampMixin):
    __tablename__ = "budgets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    category: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    monthly_limit: Mapped[float] = mapped_column(Float, nullable=False)
    month_year: Mapped[str] = mapped_column(String(7), index=True, nullable=False)  # YYYY-MM

    user: Mapped["User"] = relationship("User", back_populates="budgets")


class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    billing_frequency: Mapped[str] = mapped_column(String(20), default="monthly", nullable=False)  # monthly, quarterly, yearly
    next_billing_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="Subscriptions", nullable=False)
    payment_method: Mapped[str] = mapped_column(String(50), default="Card", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="subscriptions")
