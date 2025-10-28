from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.utils.database import SessionLocal
from app.models.expense_entry import ExpenseEntry

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/expenses/")
def create_expense(amount: float, category: str, calendar_day_id: int, notes: str = "", db: Session = Depends(get_db)):
    expense = ExpenseEntry(amount=amount, category=category, calendar_day_id=calendar_day_id, notes=notes)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense

@router.get("/expenses/")
def list_expenses(db: Session = Depends(get_db)):
    return db.query(ExpenseEntry).all()