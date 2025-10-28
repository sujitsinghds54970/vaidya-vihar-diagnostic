from pydantic import BaseModel
from datetime import time

class AppointmentCreate(BaseModel):
    patient_id: int
    calendar_day_id: int
    time_slot: time

class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    calendar_day_id: int
    time_slot: time
    status: str

    class Config:
        orm_mode = True