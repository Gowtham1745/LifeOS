from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.api.deps import get_db, get_current_user
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User, UserSettings
from app.models.notification import Notification
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, UserSettingsUpdate, UserSettingsResponse

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, response: Response, db: AsyncSession = Depends(get_db)):
    # Check if email is already taken
    stmt = select(User).where(User.email == user_in.email.lower().strip())
    existing_user = (await db.execute(stmt)).scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    # Create new user
    new_user = User(
        email=user_in.email.lower().strip(),
        full_name=user_in.full_name.strip(),
        hashed_password=hash_password(user_in.password),
        is_active=True,
    )
    db.add(new_user)
    await db.flush()

    # Create default settings
    default_settings = UserSettings(
        user_id=new_user.id,
        theme="system",
        currency="USD",
        timezone="UTC",
        working_hours_start="09:00",
        working_hours_end="18:00",
        notification_preferences={
            "task_due": True,
            "habit_reminders": True,
            "goal_deadlines": True,
            "budget_warnings": True,
            "subscription_renewals": True,
        },
        onboarding_completed=False,
    )
    db.add(default_settings)

    # Create welcome notification
    welcome_notification = Notification(
        user_id=new_user.id,
        title="Welcome to LifeOS! 👋",
        message="Your unified personal operating system is ready. Start by setting your habits, goals, and today's tasks.",
        type="system",
        link="/dashboard",
    )
    db.add(welcome_notification)

    await db.commit()

    # Re-fetch user with settings loaded
    stmt = select(User).where(User.id == new_user.id).options(selectinload(User.settings))
    loaded_user = (await db.execute(stmt)).scalar_one()

    access_token = create_access_token(subject=loaded_user.id)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=False,  # Set to True in production HTTPS
        max_age=60 * 60 * 24 * 7,
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=loaded_user,
    )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, response: Response, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == credentials.email.lower().strip()).options(selectinload(User.settings))
    user = (await db.execute(stmt)).scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact support."
        )

    access_token = create_access_token(subject=user.id)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24 * 7,
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/settings", response_model=UserSettingsResponse)
async def update_settings(
    settings_in: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(UserSettings).where(UserSettings.user_id == current_user.id)
    settings = (await db.execute(stmt)).scalar_one_or_none()

    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)

    update_data = settings_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)

    await db.commit()
    await db.refresh(settings)
    return settings


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out"}
