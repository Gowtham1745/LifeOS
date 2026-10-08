from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class SubtaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    is_completed: bool = False
    position: int = 0


class SubtaskCreate(SubtaskBase):
    pass


class SubtaskUpdate(BaseModel):
    title: Optional[str] = None
    is_completed: Optional[bool] = None
    position: Optional[int] = None


class SubtaskResponse(SubtaskBase):
    id: str
    task_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: str = "todo"  # todo, in_progress, completed, archived
    priority: str = "medium"  # low, medium, high, urgent
    due_date: Optional[date] = None
    due_time: Optional[str] = None
    category: Optional[str] = "General"
    tags: List[str] = Field(default_factory=list)
    estimated_duration: Optional[int] = None
    recurrence: str = "none"


class TaskCreate(TaskBase):
    subtasks: Optional[List[SubtaskCreate]] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None
    due_time: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    estimated_duration: Optional[int] = None
    recurrence: Optional[str] = None


class TaskResponse(TaskBase):
    id: str
    user_id: str
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    subtasks: List[SubtaskResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True
