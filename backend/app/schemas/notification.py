from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class NotificationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    type: str = "system"  # task_due, habit_reminder, goal_deadline, budget_warning, subscription_renewal, calendar_event, system
    link: Optional[str] = None


class NotificationCreate(NotificationBase):
    pass


class NotificationResponse(NotificationBase):
    id: str
    user_id: str
    is_read: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationBulkRead(BaseModel):
    notification_ids: Optional[List[str]] = None
    all: bool = False
