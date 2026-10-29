from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.session import get_db
from app.config import settings

router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint to verify backend and database connection."""
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "gemini_api_configured": bool(settings.GEMINI_API_KEY)
    }
