import uuid
from typing import Optional
from sqlalchemy import String, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin


class Note(Base, TimestampMixin):
    __tablename__ = "notes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, default="", nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="Personal", index=True, nullable=False)  # Personal, Work, Learning, Projects, Ideas
    tags: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="notes")
