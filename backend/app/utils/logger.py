def log_activity(db, user_id: int, action: str, detail: str = ""):
    from app.models.activity_log import ActivityLog  # ✅ Moved inside function
    log = ActivityLog(user_id=user_id, action=action, detail=detail)
    db.add(log)
    db.commit()