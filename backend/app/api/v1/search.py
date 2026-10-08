from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.task import Task
from app.models.habit import Habit
from app.models.goal import Goal
from app.models.note import Note
from app.models.journal import JournalEntry
from app.models.finance import Transaction
from app.schemas.search import GlobalSearchResponse, SearchResultItem

router = APIRouter()


@router.get("/", response_model=GlobalSearchResponse)
async def global_search(
    q: str = Query(..., min_length=1, description="Query string"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query_pattern = f"%{q.strip()}%"
    results: List[SearchResultItem] = []

    # 1. Tasks
    stmt_tasks = select(Task).where(
        and_(
            Task.user_id == current_user.id,
            or_(Task.title.ilike(query_pattern), Task.description.ilike(query_pattern))
        )
    ).limit(8)
    tasks = (await db.execute(stmt_tasks)).scalars().all()
    for t in tasks:
        results.append(SearchResultItem(
            id=t.id,
            type="task",
            title=t.title,
            subtitle=f"{t.priority.capitalize()} priority • {t.status.replace('_', ' ').capitalize()}",
            url="/tasks",
            category=t.category,
            date=t.due_date.strftime("%Y-%m-%d") if t.due_date else None,
        ))

    # 2. Habits
    stmt_habits = select(Habit).where(
        and_(
            Habit.user_id == current_user.id,
            Habit.name.ilike(query_pattern)
        )
    ).limit(8)
    habits = (await db.execute(stmt_habits)).scalars().all()
    for h in habits:
        results.append(SearchResultItem(
            id=h.id,
            type="habit",
            title=h.name,
            subtitle=f"{h.frequency.capitalize()} • Target: {h.target_value} {h.unit}",
            url="/habits",
            category=h.frequency,
        ))

    # 3. Goals
    stmt_goals = select(Goal).where(
        and_(
            Goal.user_id == current_user.id,
            or_(Goal.title.ilike(query_pattern), Goal.description.ilike(query_pattern))
        )
    ).limit(8)
    goals = (await db.execute(stmt_goals)).scalars().all()
    for g in goals:
        results.append(SearchResultItem(
            id=g.id,
            type="goal",
            title=g.title,
            subtitle=f"{g.category} • Target: {g.target_date.strftime('%b %d, %Y')}",
            url="/goals",
            category=g.category,
        ))

    # 4. Notes
    stmt_notes = select(Note).where(
        and_(
            Note.user_id == current_user.id,
            or_(Note.title.ilike(query_pattern), Note.content.ilike(query_pattern))
        )
    ).limit(8)
    notes = (await db.execute(stmt_notes)).scalars().all()
    for n in notes:
        results.append(SearchResultItem(
            id=n.id,
            type="note",
            title=n.title,
            subtitle=n.content[:60] + "..." if len(n.content) > 60 else n.content,
            url="/notes",
            category=n.category,
        ))

    # 5. Journal Entries
    stmt_journal = select(JournalEntry).where(
        and_(
            JournalEntry.user_id == current_user.id,
            or_(JournalEntry.title.ilike(query_pattern), JournalEntry.content.ilike(query_pattern))
        )
    ).limit(8)
    journal_entries = (await db.execute(stmt_journal)).scalars().all()
    for j in journal_entries:
        results.append(SearchResultItem(
            id=j.id,
            type="journal",
            title=j.title,
            subtitle=f"Mood: {j.mood} • {j.content[:50]}...",
            url="/journal",
            date=j.date.strftime("%Y-%m-%d"),
        ))

    # 6. Transactions
    stmt_tx = select(Transaction).where(
        and_(
            Transaction.user_id == current_user.id,
            or_(Transaction.description.ilike(query_pattern), Transaction.category.ilike(query_pattern))
        )
    ).limit(8)
    transactions = (await db.execute(stmt_tx)).scalars().all()
    for tx in transactions:
        results.append(SearchResultItem(
            id=tx.id,
            type="transaction",
            title=tx.description,
            subtitle=f"{tx.type.capitalize()} • {tx.amount} ({tx.category})",
            url="/finance",
            category=tx.category,
            date=tx.date.strftime("%Y-%m-%d"),
        ))

    return GlobalSearchResponse(
        query=q,
        total_results=len(results),
        results=results
    )
