from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import date
from app.schemas.task import TaskResponse
from app.schemas.habit import HabitResponse
from app.schemas.goal import GoalResponse
from app.schemas.calendar import CalendarEventResponse


class TasksSummary(BaseModel):
    total_today: int = 0
    completed_today: int = 0
    remaining_today: int = 0
    high_priority_remaining: int = 0
    completion_rate: float = 0.0
    tasks: List[TaskResponse] = Field(default_factory=list)


class HabitsSummary(BaseModel):
    total: int = 0
    completed_today: int = 0
    completion_rate: float = 0.0
    habits: List[HabitResponse] = Field(default_factory=list)


class FinanceMiniSummary(BaseModel):
    month_income: float = 0.0
    month_expenses: float = 0.0
    savings: float = 0.0
    savings_rate: float = 0.0
    currency: str = "USD"


class ProductivityScoreSummary(BaseModel):
    score: int = 0  # 0 to 100
    focus_minutes_today: int = 0
    tasks_completed_today: int = 0
    habits_completed_today: int = 0
    explanation: str = ""


class DashboardSummary(BaseModel):
    user_name: str
    greeting: str
    current_date: date
    tasks_summary: TasksSummary
    habits_summary: HabitsSummary
    active_goals: List[GoalResponse]
    finance_summary: FinanceMiniSummary
    upcoming_events: List[CalendarEventResponse]
    productivity: ProductivityScoreSummary
