from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate, AppointmentResponse
from app.utils.database import get_db

router = APIRouter()

@router.post("/appointments/", response_model=AppointmentResponse, status_code=201)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    new_appointment = Appointment(**appointment.model_dump())
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment

@router.get("/appointments/by-day/{calendar_day_id}", response_model=list[AppointmentResponse])
def get_appointments_by_day(calendar_day_id: int, db: Session = Depends(get_db)):
    appointments = db.query(Appointment).filter(Appointment.calendar_day_id == calendar_day_id).all()
    return appointments