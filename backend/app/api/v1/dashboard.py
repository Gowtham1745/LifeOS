from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from datetime import date, datetime, timedelta, timezone

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.task import Task
from app.models.habit import Habit, HabitLog
from app.models.goal import Goal
from app.models.finance import Transaction
from app.models.calendar import CalendarEvent
from app.models.focus import FocusSession
from app.schemas.dashboard import (
    DashboardSummary, TasksSummary, HabitsSummary, FinanceMiniSummary, ProductivityScoreSummary
)
from app.schemas.task import TaskResponse
from app.schemas.habit import HabitResponse
from app.schemas.goal import GoalResponse
from app.schemas.calendar import CalendarEventResponse
from app.api.v1.habits import compute_habit_stats, habit_to_response
from app.api.v1.goals import compute_goal_progress, goal_to_response

router = APIRouter()


@router.get("/", response_model=DashboardSummary)
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    today = date.today()
    now_utc = datetime.now(timezone.utc)

    # 1. Greeting based on current hour
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = f"Good morning, {current_user.full_name} 👋"
    elif current_hour < 17:
        greeting = f"Good afternoon, {current_user.full_name} 👋"
    else:
        greeting = f"Good evening, {current_user.full_name} 👋"

    # 2. Tasks Summary for today
    stmt_tasks = (
        select(Task)
        .where(
            and_(
                Task.user_id == current_user.id,
                or_(
                    Task.due_date == today,
                    and_(Task.status.in_(["todo", "in_progress"]), Task.due_date <= today),
                    and_(Task.due_date == None, Task.status.in_(["todo", "in_progress"]))
                )
            )
        )
        .options(selectinload(Task.subtasks))
        .order_by(Task.priority.desc(), Task.created_at.desc())
    )
    today_tasks_raw = (await db.execute(stmt_tasks)).scalars().all()
    
    total_today = len(today_tasks_raw)
    completed_today = sum(1 for t in today_tasks_raw if t.status == "completed")
    remaining_today = total_today - completed_today
    high_priority_remaining = sum(1 for t in today_tasks_raw if t.priority in ["high", "urgent"] and t.status != "completed")
    task_completion_rate = round((completed_today / total_today * 100), 1) if total_today > 0 else 0.0

    tasks_summary = TasksSummary(
        total_today=total_today,
        completed_today=completed_today,
        remaining_today=remaining_today,
        high_priority_remaining=high_priority_remaining,
        completion_rate=task_completion_rate,
        tasks=today_tasks_raw[:8],
    )

    # 3. Habits Summary
    stmt_habits = (
        select(Habit)
        .where(and_(Habit.user_id == current_user.id, Habit.is_active == True))
        .options(selectinload(Habit.logs))
    )
    habits_raw = (await db.execute(stmt_habits)).scalars().all()
    
    habits_list = [habit_to_response(h, today) for h in habits_raw]
    habits_completed_today_count = sum(1 for h in habits_list if h.today_completed)
    total_habits = len(habits_list)
    habits_completion_rate = round((habits_completed_today_count / total_habits * 100), 1) if total_habits > 0 else 0.0

    habits_summary = HabitsSummary(
        total=total_habits,
        completed_today=habits_completed_today_count,
        completion_rate=habits_completion_rate,
        habits=habits_list[:6],
    )

    # 4. Active Goals
    stmt_goals = (
        select(Goal)
        .where(and_(Goal.user_id == current_user.id, Goal.status == "active"))
        .options(selectinload(Goal.milestones))
        .order_by(Goal.target_date.asc())
        .limit(4)
    )
    goals_raw = (await db.execute(stmt_goals)).scalars().all()
    active_goals = [goal_to_response(g) for g in goals_raw]

    # 5. Finance Mini Summary
    current_month_str = today.strftime("%Y-%m")
    stmt_tx = select(Transaction).where(Transaction.user_id == current_user.id)
    all_txs = (await db.execute(stmt_tx)).scalars().all()
    
    month_income = 0.0
    month_expenses = 0.0
    for tx in all_txs:
        if tx.date.strftime("%Y-%m") == current_month_str:
            if tx.type == "income":
                month_income += tx.amount
            elif tx.type == "expense":
                month_expenses += tx.amount

    savings = round(month_income - month_expenses, 2)
    savings_rate = round((savings / month_income * 100), 1) if month_income > 0 else 0.0
    currency = current_user.settings.currency if current_user.settings else "USD"

    finance_summary = FinanceMiniSummary(
        month_income=round(month_income, 2),
        month_expenses=round(month_expenses, 2),
        savings=savings,
        savings_rate=savings_rate,
        currency=currency,
    )

    # 6. Upcoming Events (from today up to next 7 days)
    stmt_events = (
        select(CalendarEvent)
        .where(
            and_(
                CalendarEvent.user_id == current_user.id,
                CalendarEvent.start_time >= datetime.combine(today, datetime.min.time())
            )
        )
        .order_by(CalendarEvent.start_time.asc())
        .limit(5)
    )
    events_raw = (await db.execute(stmt_events)).scalars().all()
    upcoming_events = [CalendarEventResponse.model_validate(e) for e in events_raw]

    # 7. Focus sessions today
    stmt_focus = (
        select(FocusSession)
        .where(
            and_(
                FocusSession.user_id == current_user.id,
                func.date(FocusSession.completed_at) == today
            )
        )
    )
    focus_raw = (await db.execute(stmt_focus)).scalars().all()
    focus_minutes_today = sum(f.duration_minutes for f in focus_raw)

    # 8. Productivity Score (Section 22: simple transparent configurable formula)
    # Formula:
    # 35% Tasks completion (capped at 100%)
    # 35% Habits consistency (capped at 100%)
    # 20% Focus time (target 60 mins focus = 100%)
    # 10% Goal activity bonus
    task_pts = (task_completion_rate / 100.0) * 35.0 if total_today > 0 else 25.0
    habit_pts = (habits_completion_rate / 100.0) * 35.0 if total_habits > 0 else 25.0
    focus_pts = min(20.0, (focus_minutes_today / 60.0) * 20.0)
    goal_pts = 10.0 if len(active_goals) > 0 else 5.0
    productivity_score = min(100, int(round(task_pts + habit_pts + focus_pts + goal_pts)))

    explanation = (
        f"Calculated from {round(task_pts, 1)}/35 task pts, "
        f"{round(habit_pts, 1)}/35 habit pts, "
        f"{round(focus_pts, 1)}/20 focus pts ({focus_minutes_today}m), "
        f"and {round(goal_pts, 1)}/10 goal pts."
    )

    productivity_summary = ProductivityScoreSummary(
        score=productivity_score,
        focus_minutes_today=focus_minutes_today,
        tasks_completed_today=completed_today,
        habits_completed_today=habits_completed_today_count,
        explanation=explanation,
    )

    return DashboardSummary(
        user_name=current_user.full_name,
        greeting=greeting,
        current_date=today,
        tasks_summary=tasks_summary,
        habits_summary=habits_summary,
        active_goals=active_goals,
        finance_summary=finance_summary,
        upcoming_events=upcoming_events,
        productivity=productivity_summary,
    )
