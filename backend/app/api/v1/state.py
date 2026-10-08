from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.state import UserState
from app.schemas.state import StatePayload, StateResponse

router = APIRouter()


@router.get("/", response_model=StateResponse)
async def get_state(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(UserState).where(UserState.user_id == current_user.id))
    state = result.scalar_one_or_none()
    if not state:
        state = UserState(user_id=current_user.id, data={})
        db.add(state)
        await db.commit()
        await db.refresh(state)
    return StateResponse(data=state.data or {})


@router.put("/", response_model=StateResponse)
async def save_state(
    payload: StatePayload,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(UserState).where(UserState.user_id == current_user.id))
    state = result.scalar_one_or_none()
    if not state:
        state = UserState(user_id=current_user.id, data=payload.data)
        db.add(state)
    else:
        state.data = payload.data
    await db.commit()
    await db.refresh(state)
    return StateResponse(data=state.data or {})
