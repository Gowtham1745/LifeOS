from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.calendar import CalendarEvent
from app.schemas.calendar import CalendarEventCreate, CalendarEventUpdate, CalendarEventResponse

router = APIRouter()


@router.get("/", response_model=List[CalendarEventResponse])
async def get_events(
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(CalendarEvent)
        .where(CalendarEvent.user_id == current_user.id)
        .order_by(CalendarEvent.start_time.asc())
    )
    if start:
        stmt = stmt.where(CalendarEvent.end_time >= start)
    if end:
        stmt = stmt.where(CalendarEvent.start_time <= end)

    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/", response_model=CalendarEventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_in: CalendarEventCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    event = CalendarEvent(**event_in.model_dump(), user_id=current_user.id)
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


@router.patch("/{event_id}", response_model=CalendarEventResponse)
async def update_event(
    event_id: str,
    event_in: CalendarEventUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(CalendarEvent).where(and_(CalendarEvent.id == event_id, CalendarEvent.user_id == current_user.id))
    event = (await db.execute(stmt)).scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    update_data = event_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)

    await db.commit()
    await db.refresh(event)
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(CalendarEvent).where(and_(CalendarEvent.id == event_id, CalendarEvent.user_id == current_user.id))
    event = (await db.execute(stmt)).scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    await db.delete(event)
    await db.commit()
    return None
