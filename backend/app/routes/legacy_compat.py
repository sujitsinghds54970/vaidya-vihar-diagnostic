from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Branch
from app.models.appointment import Appointment
from app.models.payment import Invoice
from app.models.lab_result import LabResult

router = APIRouter()

@router.get("/branches/")
def get_branches(db: Session = Depends(get_db)):
    return db.query(Branch).all()

@router.post("/appointments/", status_code=201)
def create_appointment(payload: dict, db: Session = Depends(get_db)):
    obj = Appointment(**payload)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/appointments/by-day/{calendar_day_id}")
def get_appointments_by_day(calendar_day_id: int, db: Session = Depends(get_db)):
    return db.query(Appointment).filter(Appointment.calendar_day_id == calendar_day_id).all()

@router.post("/invoices/", status_code=201)
def create_invoice(payload: dict, db: Session = Depends(get_db)):
    normalized = dict(payload)
    if "total_amount" not in normalized and "amount" in normalized:
        normalized["total_amount"] = normalized["amount"]
    normalized.setdefault("invoice_number", f"LEGACY-{int(__import__('time').time() * 1000)}")
    obj = Invoice(**normalized)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/invoices/{invoice_id}")
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    return db.query(Invoice).filter(Invoice.id == invoice_id).first()

@router.post("/lab-results/", status_code=201)
def create_lab_result(payload: dict, db: Session = Depends(get_db)):
    obj = LabResult(**payload)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/lab-results/{result_id}")
def get_lab_result(result_id: int, db: Session = Depends(get_db)):
    return db.query(LabResult).filter(LabResult.id == result_id).first()
