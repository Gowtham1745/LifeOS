from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional
from datetime import datetime, date, timedelta, timezone

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.focus import FocusSession
from app.schemas.focus import FocusSessionCreate, FocusSessionResponse, FocusStatsResponse

router = APIRouter()


@router.get("/", response_model=List[FocusSessionResponse])
async def get_focus_sessions(
    limit: int = Query(30, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(FocusSession)
        .where(FocusSession.user_id == current_user.id)
        .order_by(FocusSession.completed_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/", response_model=FocusSessionResponse, status_code=status.HTTP_201_CREATED)
async def log_focus_session(
    session_in: FocusSessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    focus_sess = FocusSession(**session_in.model_dump(), user_id=current_user.id)
    db.add(focus_sess)
    await db.commit()
    await db.refresh(focus_sess)
    return focus_sess


@router.get("/stats", response_model=FocusStatsResponse)
async def get_focus_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    today = date.today()
    seven_days_ago = today - timedelta(days=6)

    stmt = select(FocusSession).where(FocusSession.user_id == current_user.id)
    all_sessions = (await db.execute(stmt)).scalars().all()

    today_minutes = 0
    today_sessions_count = 0
    week_minutes = 0

    daily_map = {
        (seven_days_ago + timedelta(days=i)).strftime("%Y-%m-%d"): 0
        for i in range(7)
    }

    for s in all_sessions:
        s_date = s.completed_at.date()
        s_date_str = s_date.strftime("%Y-%m-%d")

        if s_date == today:
            today_minutes += s.duration_minutes
            today_sessions_count += 1

        if s_date >= seven_days_ago:
            week_minutes += s.duration_minutes
            if s_date_str in daily_map:
                daily_map[s_date_str] += s.duration_minutes

    daily_trend = [
        {"date": d_str, "duration_minutes": mins}
        for d_str, mins in sorted(daily_map.items())
    ]

    return FocusStatsResponse(
        total_focus_minutes_today=today_minutes,
        total_sessions_today=today_sessions_count,
        total_focus_minutes_week=week_minutes,
        daily_focus_trend=daily_trend,
    )
