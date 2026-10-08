from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import date, timedelta

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.habit import Habit, HabitLog
from app.schemas.habit import HabitCreate, HabitUpdate, HabitResponse, HabitLogCreate, HabitLogResponse

router = APIRouter()


def compute_habit_stats(habit: Habit, today: date):
    """Calculate current streak, longest streak, and completion rate for a habit"""
    logs_dict = {log.log_date: log for log in (habit.logs or []) if log.is_completed}
    
    # Check today completion
    today_completed = today in logs_dict

    # Current streak calculation
    current_streak = 0
    check_date = today
    
    # If not completed today, check if yesterday was completed to keep streak alive
    if not today_completed:
        check_date = today - timedelta(days=1)
    
    while check_date in logs_dict:
        current_streak += 1
        check_date -= timedelta(days=1)

    # Longest streak calculation
    longest_streak = 0
    temp_streak = 0
    all_dates = sorted(list(logs_dict.keys()))
    
    if all_dates:
        temp_streak = 1
        longest_streak = 1
        for i in range(1, len(all_dates)):
            if all_dates[i] == all_dates[i - 1] + timedelta(days=1):
                temp_streak += 1
            else:
                temp_streak = 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak
    
    longest_streak = max(longest_streak, current_streak)

    # Completion rate in last 30 days or since start date
    days_active = max(1, (today - habit.start_date).days + 1)
    days_to_check = min(days_active, 30)
    completed_in_window = sum(
        1 for d in range(days_to_check)
        if (today - timedelta(days=d)) in logs_dict
    )
    completion_rate = round((completed_in_window / days_to_check) * 100, 1)

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "completion_rate": completion_rate,
        "today_completed": today_completed,
    }


def habit_to_response(h: Habit, today: date) -> HabitResponse:
    stats = compute_habit_stats(h, today)
    return HabitResponse(
        id=h.id,
        user_id=h.user_id,
        name=h.name,
        description=h.description,
        frequency=h.frequency,
        target_value=h.target_value,
        unit=h.unit,
        reminder_time=h.reminder_time,
        color=h.color,
        icon=h.icon,
        start_date=h.start_date,
        is_active=h.is_active,
        created_at=h.created_at,
        updated_at=h.updated_at,
        current_streak=stats["current_streak"],
        longest_streak=stats["longest_streak"],
        completion_rate=stats["completion_rate"],
        today_completed=stats["today_completed"],
        logs=[HabitLogResponse.model_validate(l) for l in (h.logs or [])]
    )


@router.get("/", response_model=List[HabitResponse])
async def get_habits(
    active_only: bool = Query(True, description="Filter only active habits"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Habit)
        .where(Habit.user_id == current_user.id)
        .options(selectinload(Habit.logs))
        .order_by(Habit.created_at.desc())
    )
    if active_only:
        stmt = stmt.where(Habit.is_active == True)

    result = await db.execute(stmt)
    habits = result.scalars().all()
    today = date.today()
    return [habit_to_response(h, today) for h in habits]


@router.post("/", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
async def create_habit(
    habit_in: HabitCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    new_habit = Habit(
        **habit_in.model_dump(),
        user_id=current_user.id
    )
    db.add(new_habit)
    await db.commit()
    await db.refresh(new_habit)

    # Re-fetch with logs
    stmt = select(Habit).where(Habit.id == new_habit.id).options(selectinload(Habit.logs))
    h = (await db.execute(stmt)).scalar_one()
    return habit_to_response(h, date.today())


@router.get("/{habit_id}", response_model=HabitResponse)
async def get_habit(
    habit_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Habit).where(and_(Habit.id == habit_id, Habit.user_id == current_user.id)).options(selectinload(Habit.logs))
    habit = (await db.execute(stmt)).scalar_one_or_none()
    if not habit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")

    return habit_to_response(habit, date.today())


@router.patch("/{habit_id}", response_model=HabitResponse)
async def update_habit(
    habit_id: str,
    habit_in: HabitUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Habit).where(and_(Habit.id == habit_id, Habit.user_id == current_user.id)).options(selectinload(Habit.logs))
    habit = (await db.execute(stmt)).scalar_one_or_none()
    if not habit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")

    update_data = habit_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(habit, field, value)

    await db.commit()
    await db.refresh(habit)
    stmt = select(Habit).where(Habit.id == habit_id).options(selectinload(Habit.logs))
    refreshed_habit = (await db.execute(stmt)).scalar_one()
    return habit_to_response(refreshed_habit, date.today())


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habit(
    habit_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Habit).where(and_(Habit.id == habit_id, Habit.user_id == current_user.id))
    habit = (await db.execute(stmt)).scalar_one_or_none()
    if not habit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")

    await db.delete(habit)
    await db.commit()
    return None


@router.post("/{habit_id}/toggle", response_model=HabitResponse)
async def toggle_habit_date(
    habit_id: str,
    target_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Habit).where(and_(Habit.id == habit_id, Habit.user_id == current_user.id)).options(selectinload(Habit.logs))
    habit = (await db.execute(stmt)).scalar_one_or_none()
    if not habit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")

    log_day = target_date or date.today()
    stmt_log = select(HabitLog).where(and_(HabitLog.habit_id == habit_id, HabitLog.log_date == log_day))
    existing_log = (await db.execute(stmt_log)).scalar_one_or_none()

    if existing_log:
        await db.delete(existing_log)
    else:
        new_log = HabitLog(
            habit_id=habit.id,
            user_id=current_user.id,
            log_date=log_day,
            completed_value=habit.target_value,
            is_completed=True,
        )
        db.add(new_log)

    await db.commit()

    # Re-fetch updated habit
    stmt = select(Habit).where(Habit.id == habit_id).options(selectinload(Habit.logs))
    updated_habit = (await db.execute(stmt)).scalar_one()
    return habit_to_response(updated_habit, date.today())
