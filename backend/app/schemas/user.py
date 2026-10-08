from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, Dict, Any
from datetime import datetime


class UserSettingsBase(BaseModel):
    theme: str = "system"
    currency: str = "USD"
    timezone: str = "UTC"
    working_hours_start: str = "09:00"
    working_hours_end: str = "18:00"
    notification_preferences: Dict[str, Any] = Field(default_factory=dict)
    onboarding_completed: bool = False


class UserSettingsUpdate(BaseModel):
    theme: Optional[str] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    working_hours_start: Optional[str] = None
    working_hours_end: Optional[str] = None
    notification_preferences: Optional[Dict[str, Any]] = None
    onboarding_completed: Optional[bool] = None


class UserSettingsResponse(UserSettingsBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=6, max_length=100)
    confirm_password: Optional[str] = None

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: Optional[str], info) -> Optional[str]:
        if v is not None and "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    settings: Optional[UserSettingsResponse] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
