from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.utils.database import SessionLocal
from app.models.calendar_day import CalendarDay
from app.models.expense_entry import ExpenseEntry
from app.models.billing_entry import BillingEntry

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/analytics/summary/")
def get_summary(start_date: str, end_date: str, branch_id: int = None, db: Session = Depends(get_db)):
    query = db.query(CalendarDay).filter(CalendarDay.date.between(start_date, end_date))
    if branch_id:
        query = query.filter(CalendarDay.branch_id == branch_id)
    days = query.all()

    total_patients = 0
    total_expense = 0.0
    total_revenue = 0.0

    for day in days:
        patients = db.query(PatientEntry).filter(PatientEntry.calendar_day_id == day.id).count()
        expenses = db.query(ExpenseEntry).filter(ExpenseEntry.calendar_day_id == day.id).all()
        bills = db.query(BillingEntry).filter(BillingEntry.patient.has(calendar_day_id=day.id)).all()

        total_patients += patients
        total_expense += sum(e.amount for e in expenses)
        total_revenue += sum(b.paid_amount for b in bills)

    return {
        "total_patients": total_patients,
        "total_expense": total_expense,
        "total_revenue": total_revenue,
        "profit": total_revenue - total_expense
    }
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.utils.auth_guard import get_current_user
from app.models.user import User
from app.models.appointment import Appointment
from sqlalchemy import func

router = APIRouter()

@router.get("/analytics/overview/")
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    total_patients = db.query(func.count(PatientEntry.id)).scalar()
    total_appointments = db.query(func.count(Appointment.id)).scalar()
    upcoming = db.query(func.count(Appointment.id)).filter(Appointment.status == "scheduled").scalar()
    completed = db.query(func.count(Appointment.id)).filter(Appointment.status == "completed").scalar()

    return {
        "total_patients": total_patients,
        "total_appointments": total_appointments,
        "upcoming_appointments": upcoming,
        "completed_appointments": completed
    }
@router.get("/analytics/branches/")
def get_branch_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    stats = db.query(
        PatientEntry.branch_id,
        func.count(PatientEntry.id).label("patient_count")
    ).group_by(PatientEntry.branch_id).all()

    return [
        {"branch_id": branch_id, "patient_count": count}
        for branch_id, count in stats
    ]

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.utils.database import get_db
from app.models.invoice import Invoice
from app.models.appointment import Appointment
from app.models.lab_result import LabResult
from app.models.branch import Branch
from app.utils.auth_guard import require_role

router = APIRouter()

@router.get("/admin/summary", dependencies=[Depends(require_role("admin"))])
def get_admin_summary(db: Session = Depends(get_db)):
    patient_count = db.query(func.count(Appointment.id)).scalar()
    total_revenue = db.query(func.sum(Invoice.total_amount)).scalar() or 0
    test_count = db.query(func.count(LabResult.id)).scalar()

    return {
        "total_patients": patient_count,
        "total_revenue": total_revenue,
        "total_tests": test_count
    }

@router.get("/admin/branch-summary", dependencies=[Depends(require_role("admin"))])
def get_branch_summary(db: Session = Depends(get_db)):
    branches = db.query(Branch).all()
    summary = []

    for branch in branches:
        patient_count = db.query(func.count(Appointment.id)).filter(Appointment.calendar_day.has(branch_id=branch.id)).scalar()
        revenue = db.query(func.sum(Invoice.total_amount)).filter(Invoice.branch_id == branch.id).scalar() or 0
        summary.append({
            "branch_id": branch.id,
            "branch_name": branch.name,
            "patient_count": patient_count,
            "revenue": revenue
        })

    return summary