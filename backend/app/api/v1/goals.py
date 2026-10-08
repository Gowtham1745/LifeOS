from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.goal import Goal, GoalMilestone
from app.schemas.goal import GoalCreate, GoalUpdate, GoalResponse, GoalMilestoneCreate, GoalMilestoneUpdate, GoalMilestoneResponse

router = APIRouter()


def compute_goal_progress(goal: Goal) -> float:
    """Calculate progress percentage based on current/target value or milestones"""
    if goal.milestones and len(goal.milestones) > 0:
        completed = sum(1 for m in goal.milestones if m.is_completed)
        return round((completed / len(goal.milestones)) * 100, 1)
    elif goal.target_value and goal.target_value > 0:
        return min(100.0, round((goal.current_value / goal.target_value) * 100, 1))
    return 0.0


def goal_to_response(goal: Goal) -> GoalResponse:
    progress = compute_goal_progress(goal)
    return GoalResponse(
        id=goal.id,
        user_id=goal.user_id,
        title=goal.title,
        description=goal.description,
        category=goal.category,
        target_value=goal.target_value,
        current_value=goal.current_value,
        unit=goal.unit,
        start_date=goal.start_date,
        target_date=goal.target_date,
        status=goal.status,
        created_at=goal.created_at,
        updated_at=goal.updated_at,
        progress_percentage=progress,
        milestones=[GoalMilestoneResponse.model_validate(m) for m in (goal.milestones or [])]
    )


@router.get("/", response_model=List[GoalResponse])
async def get_goals(
    status: Optional[str] = Query(None, description="Filter by status: active, completed, paused, cancelled"),
    category: Optional[str] = Query(None, description="Filter by category"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Goal)
        .where(Goal.user_id == current_user.id)
        .options(selectinload(Goal.milestones))
        .order_by(Goal.target_date.asc())
    )
    if status:
        stmt = stmt.where(Goal.status == status)
    if category:
        stmt = stmt.where(Goal.category == category)

    result = await db.execute(stmt)
    goals = result.scalars().all()
    return [goal_to_response(g) for g in goals]


@router.post("/", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal_in: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    goal_data = goal_in.model_dump(exclude={"milestones"})
    new_goal = Goal(**goal_data, user_id=current_user.id)
    db.add(new_goal)
    await db.flush()

    if goal_in.milestones:
        for m_in in goal_in.milestones:
            m = GoalMilestone(
                goal_id=new_goal.id,
                title=m_in.title,
                is_completed=m_in.is_completed,
                target_date=m_in.target_date,
            )
            db.add(m)

    await db.commit()

    stmt = select(Goal).where(Goal.id == new_goal.id).options(selectinload(Goal.milestones))
    g = (await db.execute(stmt)).scalar_one()
    return goal_to_response(g)


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Goal).where(and_(Goal.id == goal_id, Goal.user_id == current_user.id)).options(selectinload(Goal.milestones))
    goal = (await db.execute(stmt)).scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    return goal_to_response(goal)


@router.patch("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: str,
    goal_in: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Goal).where(and_(Goal.id == goal_id, Goal.user_id == current_user.id)).options(selectinload(Goal.milestones))
    goal = (await db.execute(stmt)).scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    update_data = goal_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(goal, field, value)

    await db.commit()
    await db.refresh(goal)
    stmt = select(Goal).where(Goal.id == goal_id).options(selectinload(Goal.milestones))
    refreshed_goal = (await db.execute(stmt)).scalar_one()
    return goal_to_response(refreshed_goal)


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Goal).where(and_(Goal.id == goal_id, Goal.user_id == current_user.id))
    goal = (await db.execute(stmt)).scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    await db.delete(goal)
    await db.commit()
    return None


@router.post("/{goal_id}/milestones", response_model=GoalMilestoneResponse, status_code=status.HTTP_201_CREATED)
async def create_milestone(
    goal_id: str,
    milestone_in: GoalMilestoneCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Goal).where(and_(Goal.id == goal_id, Goal.user_id == current_user.id))
    goal = (await db.execute(stmt)).scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    milestone = GoalMilestone(
        goal_id=goal.id,
        title=milestone_in.title,
        is_completed=milestone_in.is_completed,
        target_date=milestone_in.target_date,
    )
    db.add(milestone)
    await db.commit()
    await db.refresh(milestone)
    return milestone


@router.patch("/{goal_id}/milestones/{milestone_id}", response_model=GoalMilestoneResponse)
async def update_milestone(
    goal_id: str,
    milestone_id: str,
    milestone_in: GoalMilestoneUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Goal).where(and_(Goal.id == goal_id, Goal.user_id == current_user.id))
    goal = (await db.execute(stmt)).scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    stmt_m = select(GoalMilestone).where(and_(GoalMilestone.id == milestone_id, GoalMilestone.goal_id == goal_id))
    milestone = (await db.execute(stmt_m)).scalar_one_or_none()
    if not milestone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")

    update_data = milestone_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(milestone, field, value)

    await db.commit()
    await db.refresh(milestone)
    return milestone


@router.delete("/{goal_id}/milestones/{milestone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_milestone(
    goal_id: str,
    milestone_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Goal).where(and_(Goal.id == goal_id, Goal.user_id == current_user.id))
    goal = (await db.execute(stmt)).scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    stmt_m = select(GoalMilestone).where(and_(GoalMilestone.id == milestone_id, GoalMilestone.goal_id == goal_id))
    milestone = (await db.execute(stmt_m)).scalar_one_or_none()
    if not milestone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")

    await db.delete(milestone)
    await db.commit()
    return None
