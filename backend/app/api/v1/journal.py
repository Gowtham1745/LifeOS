from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import date

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.journal import JournalEntry
from app.schemas.journal import JournalEntryCreate, JournalEntryUpdate, JournalEntryResponse

router = APIRouter()


@router.get("/", response_model=List[JournalEntryResponse])
async def get_journal_entries(
    mood: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(JournalEntry)
        .where(JournalEntry.user_id == current_user.id)
        .order_by(JournalEntry.date.desc(), JournalEntry.created_at.desc())
        .limit(limit)
    )
    if mood:
        stmt = stmt.where(JournalEntry.mood == mood)

    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_journal_entry(
    entry_in: JournalEntryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    entry = JournalEntry(**entry_in.model_dump(), user_id=current_user.id)
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.patch("/{entry_id}", response_model=JournalEntryResponse)
async def update_journal_entry(
    entry_id: str,
    entry_in: JournalEntryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(JournalEntry).where(and_(JournalEntry.id == entry_id, JournalEntry.user_id == current_user.id))
    entry = (await db.execute(stmt)).scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal entry not found")

    update_data = entry_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entry, field, value)

    await db.commit()
    await db.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_journal_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(JournalEntry).where(and_(JournalEntry.id == entry_id, JournalEntry.user_id == current_user.id))
    entry = (await db.execute(stmt)).scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal entry not found")

    await db.delete(entry)
    await db.commit()
    return None
