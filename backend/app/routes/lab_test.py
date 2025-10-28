from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.lab_test import LabTest
from app.models.user import User
from app.utils.database import get_db
from app.utils.auth_guard import get_current_user

router = APIRouter()

@router.post("/lab-tests/")
def assign_lab_test(
    patient_id: int,
    technician_id: int,
    test_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "technician"]:
        raise HTTPException(status_code=403, detail="Access denied")

    test = LabTest(
        patient_id=patient_id,
        technician_id=technician_id,
        test_type=test_type
    )
    db.add(test)
    db.commit()
    db.refresh(test)

    return {
        "id": test.id,
        "test_type": test.test_type,
        "status": test.status,
        "created_at": test.created_at.isoformat()
    }
@router.put("/lab-tests/{test_id}/result/")
def submit_lab_result(
    test_id: int,
    result: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "technician":
        raise HTTPException(status_code=403, detail="Only technicians can submit results")

    test = db.query(LabTest).filter(LabTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    test.result = result
    test.status = "completed"
    db.commit()
    db.refresh(test)

    return {
        "id": test.id,
        "status": test.status,
        "result": test.result
    }
from weasyprint import HTML
from fastapi.responses import Response

@router.get("/lab-tests/{test_id}/pdf/")
def generate_lab_report_pdf(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    test = db.query(LabTest).filter(LabTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    html_content = f"""
    <html>
    <head><title>Lab Report #{test.id}</title></head>
    <body>
        <h1>Lab Report</h1>
        <p><strong>Test ID:</strong> {test.id}</p>
        <p><strong>Patient ID:</strong> {test.patient_id}</p>
        <p><strong>Technician ID:</strong> {test.technician_id}</p>
        <p><strong>Test Type:</strong> {test.test_type}</p>
        <p><strong>Status:</strong> {test.status}</p>
        <p><strong>Result:</strong><br>{test.result}</p>
        <p><strong>Created At:</strong> {test.created_at.strftime('%Y-%m-%d %H:%M')}</p>
    </body>
    </html>
    """

    pdf = HTML(string=html_content).write_pdf()
    return Response(content=pdf, media_type="application/pdf")