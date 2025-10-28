from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.utils.auth_guard import get_current_user
from app.models.user import User
from app.models.appointment import Appointment
from app.models.lab_test import LabTest
from sqlalchemy import func

router = APIRouter()

@router.get("/dashboard/")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    role = current_user.role

    if role == "admin":
        total_patients = db.query(func.count(PatientEntry.id)).scalar()
        total_appointments = db.query(func.count(Appointment.id)).scalar()
        total_tests = db.query(func.count(LabTest.id)).scalar()
        return {
            "role": "admin",
            "total_patients": total_patients,
            "total_appointments": total_appointments,
            "total_lab_tests": total_tests
        }

    elif role == "technician":
        assigned_tests = db.query(LabTest).filter(
            LabTest.technician_id == current_user.id,
            LabTest.status == "pending"
        ).count()
        completed_tests = db.query(LabTest).filter(
            LabTest.technician_id == current_user.id,
            LabTest.status == "completed"
        ).count()
        return {
            "role": "technician",
            "assigned_tests": assigned_tests,
            "completed_tests": completed_tests
        }

    elif role == "reception":
        today_appointments = db.query(Appointment).filter(
            func.date(Appointment.scheduled_time) == func.current_date()
        ).count()
        return {
            "role": "reception",
            "today_appointments": today_appointments
        }

    else:
        raise HTTPException(status_code=403, detail="Role not supported")