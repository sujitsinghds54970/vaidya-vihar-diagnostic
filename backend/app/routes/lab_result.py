from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.lab_result import LabResult
from app.schemas.lab_result import LabResultCreate, LabResultResponse
from app.utils.database import get_db

router = APIRouter()

@router.post("/lab-results/", response_model=LabResultResponse, status_code=201)
def create_lab_result(result: LabResultCreate, db: Session = Depends(get_db)):
    new_result = LabResult(**result.model_dump())
    db.add(new_result)
    db.commit()
    db.refresh(new_result)
    return new_result

@router.get("/lab-results/{patient_id}", response_model=list[LabResultResponse])
def get_lab_results(patient_id: int, db: Session = Depends(get_db)):
    results = db.query(LabResult).filter(LabResult.patient_id == patient_id).all()
    return results