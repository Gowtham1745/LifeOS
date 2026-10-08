from pydantic import BaseModel, Field
from typing import List, Dict, Any


class AnalyticsResponse(BaseModel):
    timeframe: str = "monthly"  # weekly, monthly, yearly
    productivity_score: int = 0
    score_history: List[Dict[str, Any]] = Field(default_factory=list)
    score_formula_breakdown: Dict[str, Any] = Field(default_factory=dict)
    
    # Task metrics
    total_tasks_completed: int = 0
    task_completion_rate: float = 0.0
    tasks_by_priority: Dict[str, int] = Field(default_factory=dict)
    tasks_completion_trend: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Habit metrics
    habit_overall_completion_rate: float = 0.0
    habit_streaks_leaderboard: List[Dict[str, Any]] = Field(default_factory=list)
    habit_completion_trend: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Finance metrics
    total_income: float = 0.0
    total_expenses: float = 0.0
    savings: float = 0.0
    savings_rate: float = 0.0
    spending_by_category: List[Dict[str, Any]] = Field(default_factory=list)
    cashflow_trend: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Focus metrics
    total_focus_hours: float = 0.0
    focus_trend: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Goals metrics
    active_goals_count: int = 0
    completed_goals_count: int = 0
    average_goal_progress: float = 0.0
    
    # Journal / Mood metrics
    mood_distribution: Dict[str, int] = Field(default_factory=dict)
    mood_trend: List[Dict[str, Any]] = Field(default_factory=list)
