from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = ""
    category: str = "Personal"  # Personal, Work, Learning, Projects, Ideas
    tags: List[str] = Field(default_factory=list)
    is_pinned: bool = False
    is_archived: bool = False


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_pinned: Optional[bool] = None
    is_archived: Optional[bool] = None


class NoteResponse(NoteBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
