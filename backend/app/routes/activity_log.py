from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.database import SessionLocal
from app.models.user import User
from app.utils.auth_guard import get_current_user

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Admin-only route to view activity logs
@router.get("/activity-logs/")
def list_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    # Import inside function to avoid circular import
    from app.models.activity_log import ActivityLog

    logs = db.query(ActivityLog).order_by(ActivityLog.timestamp.desc()).limit(100).all()
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "detail": log.detail,
            "timestamp": log.timestamp.isoformat()
        }
        for log in logs
    ]