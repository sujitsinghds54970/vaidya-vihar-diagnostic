from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.utils.database import SessionLocal
from app.models.calendar_day import CalendarDay

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/calendar-days/")
def create_calendar_day(date: str, branch_id: int, summary: str = "", db: Session = Depends(get_db)):
    day = CalendarDay(date=date, branch_id=branch_id, summary=summary)
    db.add(day)
    db.commit()
    db.refresh(day)
    return day

@router.get("/calendar-days/")
def list_calendar_days(db: Session = Depends(get_db)):
    return db.query(CalendarDay).all()
