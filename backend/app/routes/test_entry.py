from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.utils.database import SessionLocal
from app.models.test_entry import TestEntry

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/tests/")
def create_test(test_name: str, price: float, patient_id: int, result: str = "", db: Session = Depends(get_db)):
    test = TestEntry(test_name=test_name, price=price, patient_id=patient_id, result=result)
    db.add(test)
    db.commit()
    db.refresh(test)
    return test

@router.get("/tests/")
def list_tests(db: Session = Depends(get_db)):
    return db.query(TestEntry).all()