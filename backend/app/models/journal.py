import uuid
from typing import Optional
from datetime import date
from sqlalchemy import String, Text, Integer, Date, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin


class JournalEntry(Base, TimestampMixin):
    __tablename__ = "journal_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    mood: Mapped[str] = mapped_column(String(20), default="Good", nullable=False)  # Great, Good, Neutral, Low, Bad
    energy: Mapped[int] = mapped_column(Integer, default=3, nullable=False)  # 1 to 5
    tags: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="journal_entries")
