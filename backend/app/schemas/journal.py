from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class JournalEntryBase(BaseModel):
    date: date
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    mood: str = "Good"  # Great, Good, Neutral, Low, Bad
    energy: int = Field(default=3, ge=1, le=5)  # 1 to 5
    tags: List[str] = Field(default_factory=list)


class JournalEntryCreate(JournalEntryBase):
    pass


class JournalEntryUpdate(BaseModel):
    date: Optional[date] = None
    title: Optional[str] = None
    content: Optional[str] = None
    mood: Optional[str] = None
    energy: Optional[int] = Field(default=None, ge=1, le=5)
    tags: Optional[List[str]] = None


class JournalEntryResponse(JournalEntryBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
