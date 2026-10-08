from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class FocusSessionBase(BaseModel):
    task_id: Optional[str] = None
    duration_minutes: int = Field(default=25, ge=1)
    session_type: str = "pomodoro"  # pomodoro, short_break, long_break
    completed_at: datetime
    notes: Optional[str] = None


class FocusSessionCreate(FocusSessionBase):
    pass


class FocusSessionResponse(FocusSessionBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FocusStatsResponse(BaseModel):
    total_focus_minutes_today: int = 0
    total_sessions_today: int = 0
    total_focus_minutes_week: int = 0
    daily_focus_trend: List[Dict[str, Any]] = Field(default_factory=list)
