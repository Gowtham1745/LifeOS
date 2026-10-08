from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.habits import router as habits_router
from app.api.v1.goals import router as goals_router
from app.api.v1.finance import router as finance_router
from app.api.v1.calendar import router as calendar_router
from app.api.v1.notes import router as notes_router
from app.api.v1.journal import router as journal_router
from app.api.v1.focus import router as focus_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.search import router as search_router
from app.api.v1.ai_assistant import router as ai_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
api_v1_router.include_router(tasks_router, prefix="/tasks", tags=["Tasks"])
api_v1_router.include_router(habits_router, prefix="/habits", tags=["Habits"])
api_v1_router.include_router(goals_router, prefix="/goals", tags=["Goals"])
api_v1_router.include_router(finance_router, prefix="/finance", tags=["Finance"])
api_v1_router.include_router(calendar_router, prefix="/calendar", tags=["Calendar"])
api_v1_router.include_router(notes_router, prefix="/notes", tags=["Notes"])
api_v1_router.include_router(journal_router, prefix="/journal", tags=["Journal"])
api_v1_router.include_router(focus_router, prefix="/focus", tags=["Focus"])
api_v1_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
api_v1_router.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
api_v1_router.include_router(search_router, prefix="/search", tags=["Search"])
api_v1_router.include_router(ai_router, prefix="/ai", tags=["AI Assistant"])
