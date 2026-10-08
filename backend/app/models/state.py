import uuid
from typing import Any
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin


class UserState(Base, TimestampMixin):
    """Cloud-synced application state for the lightweight LifeOS client.

    The frontend can keep working offline, while this record makes the same
    LifeOS account available across phones, tablets, laptops and browsers.
    """
    __tablename__ = "user_states"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"),
        unique=True, index=True, nullable=False
    )
    data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="state")
