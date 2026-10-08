from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from typing import Dict, Any, List
from datetime import date, timedelta, datetime

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.task import Task
from app.models.habit import Habit, HabitLog
from app.models.goal import Goal
from app.models.finance import Transaction
from app.models.journal import JournalEntry
from app.models.focus import FocusSession
from app.schemas.analytics import AnalyticsResponse
from app.api.v1.habits import compute_habit_stats
from app.api.v1.goals import compute_goal_progress

router = APIRouter()


@router.get("/", response_model=AnalyticsResponse)
async def get_analytics(
    timeframe: str = Query("monthly", description="weekly, monthly, yearly"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    today = date.today()
    if timeframe == "weekly":
        days_window = 7
    elif timeframe == "yearly":
        days_window = 365
    else:
        days_window = 30  # default monthly

    start_date = today - timedelta(days=days_window - 1)

    # 1. Tasks
    stmt_tasks = select(Task).where(Task.user_id == current_user.id)
    all_tasks = (await db.execute(stmt_tasks)).scalars().all()

    tasks_in_window = [
        t for t in all_tasks
        if t.completed_at and t.completed_at.date() >= start_date
    ]
    total_completed = len(tasks_in_window)
    all_in_window_tasks = [t for t in all_tasks if (t.due_date and t.due_date >= start_date) or (t.completed_at and t.completed_at.date() >= start_date)]
    completion_rate = round((total_completed / max(1, len(all_in_window_tasks))) * 100, 1)

    priority_counts = {"low": 0, "medium": 0, "high": 0, "urgent": 0}
    for t in tasks_in_window:
        if t.priority in priority_counts:
            priority_counts[t.priority] += 1

    # Task completion trend
    task_trend_map = {}
    for i in range(min(days_window, 14)):
        d = today - timedelta(days=i)
        task_trend_map[d.strftime("%Y-%m-%d")] = 0
    for t in tasks_in_window:
        d_str = t.completed_at.date().strftime("%Y-%m-%d")
        if d_str in task_trend_map:
            task_trend_map[d_str] += 1
    tasks_completion_trend = [
        {"date": d_str, "completed": count}
        for d_str, count in sorted(task_trend_map.items())
    ]

    # 2. Habits
    stmt_habits = select(Habit).where(Habit.user_id == current_user.id).options(selectinload(Habit.logs))
    habits = (await db.execute(stmt_habits)).scalars().all()

    leaderboard = []
    total_habit_checks = 0
    total_possible_checks = max(1, len(habits) * days_window)
    for h in habits:
        stats = compute_habit_stats(h, today)
        leaderboard.append({
            "name": h.name,
            "current_streak": stats["current_streak"],
            "longest_streak": stats["longest_streak"],
            "completion_rate": stats["completion_rate"],
            "color": h.color,
        })
        for log in h.logs:
            if log.is_completed and log.log_date >= start_date:
                total_habit_checks += 1

    leaderboard = sorted(leaderboard, key=lambda x: x["current_streak"], reverse=True)
    habit_overall_rate = round((total_habit_checks / total_possible_checks) * 100, 1) if habits else 0.0

    habit_trend_map = {}
    for i in range(min(days_window, 14)):
        d = today - timedelta(days=i)
        habit_trend_map[d.strftime("%Y-%m-%d")] = 0
    for h in habits:
        for log in h.logs:
            if log.is_completed:
                d_str = log.log_date.strftime("%Y-%m-%d")
                if d_str in habit_trend_map:
                    habit_trend_map[d_str] += 1
    habit_completion_trend = [
        {"date": d_str, "completed": count}
        for d_str, count in sorted(habit_trend_map.items())
    ]

    # 3. Finance
    stmt_tx = select(Transaction).where(
        and_(Transaction.user_id == current_user.id, Transaction.date >= start_date)
    )
    window_txs = (await db.execute(stmt_tx)).scalars().all()

    total_income = sum(tx.amount for tx in window_txs if tx.type == "income")
    total_expenses = sum(tx.amount for tx in window_txs if tx.type == "expense")
    savings = round(total_income - total_expenses, 2)
    savings_rate = round((savings / total_income) * 100, 1) if total_income > 0 else 0.0

    category_spending_map = {}
    for tx in window_txs:
        if tx.type == "expense":
            category_spending_map[tx.category] = category_spending_map.get(tx.category, 0.0) + tx.amount
    spending_by_category = [
        {"category": cat, "amount": round(amt, 2)}
        for cat, amt in sorted(category_spending_map.items(), key=lambda x: x[1], reverse=True)
    ]

    # Cashflow trend
    cashflow_map = {}
    for tx in window_txs:
        m_str = tx.date.strftime("%b %d") if timeframe == "weekly" else tx.date.strftime("%Y-%m")
        if m_str not in cashflow_map:
            cashflow_map[m_str] = {"income": 0.0, "expenses": 0.0}
        if tx.type == "income":
            cashflow_map[m_str]["income"] += tx.amount
        else:
            cashflow_map[m_str]["expenses"] += tx.amount
    cashflow_trend = [
        {"period": p, "income": round(data["income"], 2), "expenses": round(data["expenses"], 2)}
        for p, data in cashflow_map.items()
    ]

    # 4. Focus
    stmt_focus = select(FocusSession).where(
        and_(
            FocusSession.user_id == current_user.id,
            func.date(FocusSession.completed_at) >= start_date
        )
    )
    focus_sessions = (await db.execute(stmt_focus)).scalars().all()
    total_focus_hours = round(sum(s.duration_minutes for s in focus_sessions) / 60.0, 1)

    focus_map = {}
    for i in range(min(days_window, 14)):
        d = today - timedelta(days=i)
        focus_map[d.strftime("%Y-%m-%d")] = 0
    for s in focus_sessions:
        d_str = s.completed_at.date().strftime("%Y-%m-%d")
        if d_str in focus_map:
            focus_map[d_str] += s.duration_minutes
    focus_trend = [
        {"date": d_str, "minutes": mins}
        for d_str, mins in sorted(focus_map.items())
    ]

    # 5. Goals
    stmt_goals = select(Goal).where(Goal.user_id == current_user.id).options(selectinload(Goal.milestones))
    all_goals = (await db.execute(stmt_goals)).scalars().all()
    active_goals_count = sum(1 for g in all_goals if g.status == "active")
    completed_goals_count = sum(1 for g in all_goals if g.status == "completed")
    avg_progress = (
        round(sum(compute_goal_progress(g) for g in all_goals) / len(all_goals), 1)
        if all_goals else 0.0
    )

    # 6. Mood distribution
    stmt_journal = select(JournalEntry).where(
        and_(JournalEntry.user_id == current_user.id, JournalEntry.date >= start_date)
    )
    journal_entries = (await db.execute(stmt_journal)).scalars().all()
    mood_distribution = {"Great": 0, "Good": 0, "Neutral": 0, "Low": 0, "Bad": 0}
    for j in journal_entries:
        if j.mood in mood_distribution:
            mood_distribution[j.mood] += 1

    mood_trend = [
        {"date": j.date.strftime("%Y-%m-%d"), "mood": j.mood, "energy": j.energy}
        for j in sorted(journal_entries, key=lambda x: x.date)
    ]

    # 7. Productivity Score
    task_pts = min(35.0, (completion_rate / 100.0) * 35.0) if all_in_window_tasks else 25.0
    habit_pts = min(35.0, (habit_overall_rate / 100.0) * 35.0) if habits else 25.0
    focus_pts = min(20.0, (total_focus_hours / (days_window * 1.0)) * 20.0)
    goal_pts = min(10.0, (avg_progress / 100.0) * 10.0)
    productivity_score = min(100, int(round(task_pts + habit_pts + focus_pts + goal_pts)))

    score_history = [
        {"period": "Past 30 Days", "score": productivity_score},
        {"period": "Target", "score": 85},
    ]

    return AnalyticsResponse(
        timeframe=timeframe,
        productivity_score=productivity_score,
        score_history=score_history,
        score_formula_breakdown={
            "task_pts": round(task_pts, 1),
            "habit_pts": round(habit_pts, 1),
            "focus_pts": round(focus_pts, 1),
            "goal_pts": round(goal_pts, 1),
            "total_score": productivity_score,
            "formula": "35% Tasks + 35% Habits + 20% Focus + 10% Goals"
        },
        total_tasks_completed=total_completed,
        task_completion_rate=completion_rate,
        tasks_by_priority=priority_counts,
        tasks_completion_trend=tasks_completion_trend,
        habit_overall_completion_rate=habit_overall_rate,
        habit_streaks_leaderboard=leaderboard[:5],
        habit_completion_trend=habit_completion_trend,
        total_income=round(total_income, 2),
        total_expenses=round(total_expenses, 2),
        savings=savings,
        savings_rate=savings_rate,
        spending_by_category=spending_by_category,
        cashflow_trend=cashflow_trend,
        total_focus_hours=total_focus_hours,
        focus_trend=focus_trend,
        active_goals_count=active_goals_count,
        completed_goals_count=completed_goals_count,
        average_goal_progress=avg_progress,
        mood_distribution=mood_distribution,
        mood_trend=mood_trend,
    )
