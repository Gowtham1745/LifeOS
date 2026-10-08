from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class HabitLogBase(BaseModel):
    log_date: date
    completed_value: float = 1.0
    is_completed: bool = True
    notes: Optional[str] = None


class HabitLogCreate(HabitLogBase):
    pass


class HabitLogResponse(HabitLogBase):
    id: str
    habit_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HabitBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    frequency: str = "daily"  # daily, weekly, custom
    target_value: float = 1.0
    unit: str = "times"
    reminder_time: Optional[str] = None
    color: str = "#6366f1"
    icon: str = "check-circle"
    start_date: date
    is_active: bool = True


class HabitCreate(HabitBase):
    pass


class HabitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    frequency: Optional[str] = None
    target_value: Optional[float] = None
    unit: Optional[str] = None
    reminder_time: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    start_date: Optional[date] = None
    is_active: Optional[bool] = None


class HabitResponse(HabitBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    current_streak: int = 0
    longest_streak: int = 0
    completion_rate: float = 0.0
    today_completed: bool = False
    logs: List[HabitLogResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True
