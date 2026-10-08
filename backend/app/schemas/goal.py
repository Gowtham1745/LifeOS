from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class GoalMilestoneBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    is_completed: bool = False
    target_date: Optional[date] = None


class GoalMilestoneCreate(GoalMilestoneBase):
    pass


class GoalMilestoneUpdate(BaseModel):
    title: Optional[str] = None
    is_completed: Optional[bool] = None
    target_date: Optional[date] = None


class GoalMilestoneResponse(GoalMilestoneBase):
    id: str
    goal_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GoalBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: str = "Career"
    target_value: float = 100.0
    current_value: float = 0.0
    unit: str = "%"
    start_date: date
    target_date: date
    status: str = "active"  # active, completed, paused, cancelled


class GoalCreate(GoalBase):
    milestones: Optional[List[GoalMilestoneCreate]] = None


class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    unit: Optional[str] = None
    start_date: Optional[date] = None
    target_date: Optional[date] = None
    status: Optional[str] = None


class GoalResponse(GoalBase):
    id: str
    user_id: str
    progress_percentage: float = 0.0
    created_at: datetime
    updated_at: datetime
    milestones: List[GoalMilestoneResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True
