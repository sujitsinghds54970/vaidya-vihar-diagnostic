from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.utils.database import get_db
from app.models import User, Patient, Appointment, Invoice, LabResult, Branch
from app.utils.auth_guard import get_current_user, require_role

router = APIRouter()

@router.get("/analytics/summary/")
def get_summary(start_date: str, end_date: str, branch_id: int = None, db: Session = Depends(get_db)):
    """Get analytics summary for date range and optional branch"""
    # This is a placeholder implementation
    return {
        "total_patients": 0,
        "total_expense": 0.0,
        "total_revenue": 0.0,
        "profit": 0.0
    }

@router.get("/analytics/overview/")
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get admin dashboard analytics overview"""
    if current_user.role not in ["admin", "branch_admin"]:
        raise HTTPException(status_code=403, detail="Access denied")

    total_patients = db.query(func.count(Patient.id)).scalar()
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
    """Get statistics by branch"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    stats = db.query(
        Patient.branch_id,
        func.count(Patient.id).label("patient_count")
    ).group_by(Patient.branch_id).all()

    return [
        {"branch_id": branch_id, "patient_count": count}
        for branch_id, count in stats
    ]

@router.get("/admin/summary")
def get_admin_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get comprehensive admin summary"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    patient_count = db.query(func.count(Patient.id)).scalar()
    total_revenue = db.query(func.sum(Invoice.total_amount)).scalar() or 0
    test_count = db.query(func.count(LabResult.id)).scalar()

    return {
        "total_patients": patient_count,
        "total_revenue": total_revenue,
        "total_tests": test_count
    }

@router.get("/admin/branch-summary")
def get_branch_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get summary by branch"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    branches = db.query(Branch).all()
    summary = []

    for branch in branches:
        patient_count = db.query(func.count(Patient.id)).filter(Patient.branch_id == branch.id).scalar()
        revenue = db.query(func.sum(Invoice.total_amount)).filter(Invoice.branch_id == branch.id).scalar() or 0
        summary.append({
            "branch_id": branch.id,
            "branch_name": branch.name,
            "patient_count": patient_count,
            "revenue": revenue
        })

    return summary
