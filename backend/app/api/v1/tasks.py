from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timezone, date

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.task import Task, Subtask
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, SubtaskCreate, SubtaskUpdate, SubtaskResponse

router = APIRouter()


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    status: Optional[str] = Query(None, description="Filter by status: todo, in_progress, completed, archived"),
    priority: Optional[str] = Query(None, description="Filter by priority: low, medium, high, urgent"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search keyword in title/description"),
    due_date: Optional[date] = Query(None, description="Filter by specific due date"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Task)
        .where(Task.user_id == current_user.id)
        .options(selectinload(Task.subtasks))
        .order_by(Task.due_date.asc().nullslast(), Task.created_at.desc())
    )

    if status:
        stmt = stmt.where(Task.status == status)
    if priority:
        stmt = stmt.where(Task.priority == priority)
    if category:
        stmt = stmt.where(Task.category == category)
    if due_date:
        stmt = stmt.where(Task.due_date == due_date)
    if search:
        search_term = f"%{search.strip()}%"
        stmt = stmt.where(or_(Task.title.ilike(search_term), Task.description.ilike(search_term)))

    result = await db.execute(stmt)
    tasks = result.scalars().all()
    return tasks


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    task_data = task_in.model_dump(exclude={"subtasks"})
    new_task = Task(**task_data, user_id=current_user.id)
    if new_task.status == "completed":
        new_task.completed_at = datetime.now(timezone.utc)
    
    db.add(new_task)
    await db.flush()

    if task_in.subtasks:
        for idx, subtask_in in enumerate(task_in.subtasks):
            subtask = Subtask(
                task_id=new_task.id,
                title=subtask_in.title,
                is_completed=subtask_in.is_completed,
                position=idx,
            )
            db.add(subtask)

    await db.commit()

    stmt = select(Task).where(Task.id == new_task.id).options(selectinload(Task.subtasks))
    result = await db.execute(stmt)
    return result.scalar_one()


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Task).where(and_(Task.id == task_id, Task.user_id == current_user.id)).options(selectinload(Task.subtasks))
    task = (await db.execute(stmt)).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_in: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Task).where(and_(Task.id == task_id, Task.user_id == current_user.id)).options(selectinload(Task.subtasks))
    task = (await db.execute(stmt)).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    update_data = task_in.model_dump(exclude_unset=True)
    
    # Handle status change to/from completed
    if "status" in update_data:
        new_status = update_data["status"]
        if new_status == "completed" and task.status != "completed":
            task.completed_at = datetime.now(timezone.utc)
        elif new_status != "completed" and task.status == "completed":
            task.completed_at = None

    for field, value in update_data.items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Task).where(and_(Task.id == task_id, Task.user_id == current_user.id))
    task = (await db.execute(stmt)).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    await db.delete(task)
    await db.commit()
    return None


@router.post("/{task_id}/duplicate", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Task).where(and_(Task.id == task_id, Task.user_id == current_user.id)).options(selectinload(Task.subtasks))
    task = (await db.execute(stmt)).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    new_task = Task(
        user_id=current_user.id,
        title=f"{task.title} (Copy)",
        description=task.description,
        status="todo",
        priority=task.priority,
        due_date=task.due_date,
        due_time=task.due_time,
        category=task.category,
        tags=list(task.tags),
        estimated_duration=task.estimated_duration,
        recurrence=task.recurrence,
    )
    db.add(new_task)
    await db.flush()

    for sub in task.subtasks:
        db.add(Subtask(
            task_id=new_task.id,
            title=sub.title,
            is_completed=False,
            position=sub.position,
        ))

    await db.commit()
    
    stmt = select(Task).where(Task.id == new_task.id).options(selectinload(Task.subtasks))
    return (await db.execute(stmt)).scalar_one()


@router.post("/{task_id}/subtasks", response_model=SubtaskResponse, status_code=status.HTTP_201_CREATED)
async def create_subtask(
    task_id: str,
    subtask_in: SubtaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Task).where(and_(Task.id == task_id, Task.user_id == current_user.id))
    task = (await db.execute(stmt)).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    subtask = Subtask(
        task_id=task.id,
        title=subtask_in.title,
        is_completed=subtask_in.is_completed,
        position=subtask_in.position,
    )
    db.add(subtask)
    await db.commit()
    await db.refresh(subtask)
    return subtask


@router.patch("/{task_id}/subtasks/{subtask_id}", response_model=SubtaskResponse)
async def update_subtask(
    task_id: str,
    subtask_id: str,
    subtask_in: SubtaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Task).where(and_(Task.id == task_id, Task.user_id == current_user.id))
    task = (await db.execute(stmt)).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    stmt = select(Subtask).where(and_(Subtask.id == subtask_id, Subtask.task_id == task_id))
    subtask = (await db.execute(stmt)).scalar_one_or_none()
    if not subtask:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subtask not found")

    update_data = subtask_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(subtask, field, value)

    await db.commit()
    await db.refresh(subtask)
    return subtask


@router.delete("/{task_id}/subtasks/{subtask_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subtask(
    task_id: str,
    subtask_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Task).where(and_(Task.id == task_id, Task.user_id == current_user.id))
    task = (await db.execute(stmt)).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    stmt = select(Subtask).where(and_(Subtask.id == subtask_id, Subtask.task_id == task_id))
    subtask = (await db.execute(stmt)).scalar_one_or_none()
    if not subtask:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subtask not found")

    await db.delete(subtask)
    await db.commit()
    return None
