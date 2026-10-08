from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from typing import List, Optional

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse

router = APIRouter()


@router.get("/", response_model=List[NoteResponse])
async def get_notes(
    category: Optional[str] = Query(None),
    archived: bool = Query(False),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Note)
        .where(and_(Note.user_id == current_user.id, Note.is_archived == archived))
        .order_by(Note.is_pinned.desc(), Note.updated_at.desc())
    )
    if category:
        stmt = stmt.where(Note.category == category)
    if search:
        pattern = f"%{search.strip()}%"
        stmt = stmt.where(or_(Note.title.ilike(pattern), Note.content.ilike(pattern)))

    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_in: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    note = Note(**note_in.model_dump(), user_id=current_user.id)
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Note).where(and_(Note.id == note_id, Note.user_id == current_user.id))
    note = (await db.execute(stmt)).scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@router.patch("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: str,
    note_in: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Note).where(and_(Note.id == note_id, Note.user_id == current_user.id))
    note = (await db.execute(stmt)).scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    update_data = note_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(note, field, value)

    await db.commit()
    await db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Note).where(and_(Note.id == note_id, Note.user_id == current_user.id))
    note = (await db.execute(stmt)).scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    await db.delete(note)
    await db.commit()
    return None
