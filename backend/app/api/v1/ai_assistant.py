from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import date, timedelta

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.task import Task
from app.models.habit import Habit
from app.models.goal import Goal
from app.models.finance import Transaction
from app.models.focus import FocusSession
from app.models.journal import JournalEntry
from app.api.v1.habits import compute_habit_stats
from app.api.v1.goals import compute_goal_progress

router = APIRouter()


class AIChatRequest(BaseModel):
    message: str


class AIChatResponse(BaseModel):
    response: str
    insights: List[str]
    suggested_actions: List[str]


@router.post("/query", response_model=AIChatResponse)
async def query_ai_assistant(
    req: AIChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = req.message.lower().strip()
    today = date.today()
    week_ago = today - timedelta(days=7)

    # Fetch user's data safely (only user's records)
    stmt_tasks = select(Task).where(Task.user_id == current_user.id)
    tasks = (await db.execute(stmt_tasks)).scalars().all()

    stmt_habits = select(Habit).where(Habit.user_id == current_user.id).options(selectinload(Habit.logs))
    habits = (await db.execute(stmt_habits)).scalars().all()

    stmt_goals = select(Goal).where(Goal.user_id == current_user.id).options(selectinload(Goal.milestones))
    goals = (await db.execute(stmt_goals)).scalars().all()

    stmt_tx = select(Transaction).where(and_(Transaction.user_id == current_user.id, Transaction.date >= week_ago))
    week_txs = (await db.execute(stmt_tx)).scalars().all()

    stmt_focus = select(FocusSession).where(and_(FocusSession.user_id == current_user.id, FocusSession.completed_at >= week_ago))
    focus_sessions = (await db.execute(stmt_focus)).scalars().all()

    stmt_journal = select(JournalEntry).where(and_(JournalEntry.user_id == current_user.id, JournalEntry.date >= week_ago))
    journal_entries = (await db.execute(stmt_journal)).scalars().all()

    # Calculations
    tasks_completed_week = sum(1 for t in tasks if t.completed_at and t.completed_at.date() >= week_ago)
    tasks_due_week = sum(1 for t in tasks if t.due_date and t.due_date >= week_ago)
    completion_rate = round((tasks_completed_week / max(1, tasks_due_week)) * 100, 1)

    focus_minutes_week = sum(s.duration_minutes for s in focus_sessions)
    focus_hours_week = round(focus_minutes_week / 60.0, 1)

    week_expenses = sum(t.amount for t in week_txs if t.type == "expense")
    week_income = sum(t.amount for t in week_txs if t.type == "income")

    # Habits analysis
    best_habit = None
    best_streak = -1
    for h in habits:
        stats = compute_habit_stats(h, today)
        if stats["current_streak"] > best_streak:
            best_streak = stats["current_streak"]
            best_habit = h.name

    insights = []
    actions = []

    if "week" in query or "how is my life" in query or "summary" in query:
        response_text = (
            f"Here is your week in review, {current_user.full_name}:\n\n"
            f"• You completed {tasks_completed_week} tasks this week ({completion_rate}% completion rate).\n"
            f"• Your strongest habit is '{best_habit or 'None yet'}' with a {max(0, best_streak)}-day streak.\n"
            f"• You logged {focus_hours_week} hours of deep focus across {len(focus_sessions)} Pomodoro sessions.\n"
            f"• Total expenses this week: ${round(week_expenses, 2)} against ${round(week_income, 2)} income."
        )
        insights.append(f"Task momentum is at {completion_rate}%. High-priority tasks are moving forward.")
        insights.append(f"Deep work logged: {focus_hours_week} hours this week.")
        actions.append("Review pending high-priority tasks in your Tasks view.")
        actions.append("Check budget threshold for your primary expense categories.")

    elif "finance" in query or "spend" in query or "money" in query or "budget" in query:
        response_text = (
            f"Financial Overview for the past 7 days:\n"
            f"• Total spending: ${round(week_expenses, 2)}\n"
            f"• Total income: ${round(week_income, 2)}\n"
            f"• Net cashflow: ${round(week_income - week_expenses, 2)}"
        )
        insights.append(f"Logged {len(week_txs)} transactions in the past week.")
        actions.append("Add any missing receipts or cash transactions.")

    elif "habit" in query:
        response_text = (
            f"Habit Performance:\n"
            f"• Active habits: {len(habits)}\n"
            f"• Top performer: {best_habit or 'No active habit'} ({max(0, best_streak)} day streak)"
        )
        insights.append("Consistent morning habits correlate with higher daily productivity scores.")
        actions.append("Mark today's habits on your Habit Tracker.")

    else:
        response_text = (
            f"Hello {current_user.full_name}! I analyzed your personal OS telemetry. "
            f"You have {sum(1 for t in tasks if t.status != 'completed')} pending tasks, "
            f"{len(habits)} active habits, and {len(goals)} long-term goals. "
            f"What area would you like to plan or optimize today?"
        )
        insights.append("Your personal workspace is organized and syncing in real-time.")
        actions.append("Plan your Top 3 daily priorities in Tasks.")
        actions.append("Start a 25-minute Focus timer for deep work.")

    return AIChatResponse(
        response=response_text,
        insights=insights,
        suggested_actions=actions,
    )
