from pydantic import BaseModel
from datetime import datetime

class InvoiceCreate(BaseModel):
    patient_id: int
    branch_id: int
    total_amount: float

class InvoiceResponse(BaseModel):
    id: int
    patient_id: int
    branch_id: int
    total_amount: float
    status: str
    created_at: datetime

    class Config:
        orm_mode = True