from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CalendarEventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    reminder_minutes: Optional[int] = 15
    color: str = "#6366f1"


class CalendarEventCreate(CalendarEventBase):
    pass


class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    reminder_minutes: Optional[int] = None
    color: Optional[str] = None


class CalendarEventResponse(CalendarEventBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
