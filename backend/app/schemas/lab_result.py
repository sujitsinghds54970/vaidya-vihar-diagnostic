from pydantic import BaseModel

class LabResultCreate(BaseModel):
    test_name: str
    result_value: float
    unit: str | None = None
    reference_range: str | None = None
    invoice_id: int
    patient_id: int

class LabResultResponse(BaseModel):
    id: int
    test_name: str
    result_value: float
    unit: str | None
    reference_range: str | None
    invoice_id: int
    patient_id: int

    class Config:
        orm_mode = True