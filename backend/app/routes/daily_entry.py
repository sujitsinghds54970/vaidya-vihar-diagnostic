from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date
from pydantic import BaseModel

from app.database import get_db
from app.utils.auth_system import get_current_user

router = APIRouter()

class DailyEntryCreate(BaseModel):
    patient_id: int
    doctor_id: int
    visit_date: date
    consultation_fee: float = 0
    test_fee: float = 0
    test_type: str = ""
    notes: str = ""
    payment_status: str = "paid"
    branch_id: int

class DailyEntryResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    visit_date: date
    consultation_fee: float
    test_fee: float
    total_amount: float
    test_type: str
    notes: str
    payment_status: str
    branch_id: int
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/daily-entries", response_model=DailyEntryResponse)
async def create_daily_entry(entry: DailyEntryCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Create a new daily entry for patient visit"""
    
    # Verify user has access to this branch
    if current_user.branch_id != entry.branch_id:
        raise HTTPException(status_code=403, detail="Access denied to this branch")
    
    # Create the daily entry
    query = """
    INSERT INTO daily_entries (patient_id, doctor_id, visit_date, consultation_fee, 
                             test_fee, total_amount, test_type, notes, payment_status, 
                             branch_id, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    total_amount = entry.consultation_fee + entry.test_fee
    
    db.execute(query, (
        entry.patient_id, entry.doctor_id, entry.visit_date,
        entry.consultation_fee, entry.test_fee, total_amount,
        entry.test_type, entry.notes, entry.payment_status,
        entry.branch_id, datetime.now()
    ))
    
    # Get the created entry
    entry_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    result = db.execute("SELECT * FROM daily_entries WHERE id = ?", (entry_id,)).fetchone()
    
    db.commit()
    
    return DailyEntryResponse(**result._asdict())

@router.get("/daily-entries", response_model=List[DailyEntryResponse])
async def get_daily_entries(
    date: str = None,
    branch_id: int = None,
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    """Get daily entries with optional date and branch filtering"""
    
    query = "SELECT * FROM daily_entries WHERE 1=1"
    params = []
    
    if date:
        query += " AND visit_date = ?"
        params.append(date)
    
    if branch_id:
        query += " AND branch_id = ?"
        params.append(branch_id)
    else:
        # Default to user's branch
        query += " AND branch_id = ?"
        params.append(current_user.branch_id)
    
    query += " ORDER BY visit_date DESC, created_at DESC"
    
    results = db.execute(query, params).fetchall()
    
    return [DailyEntryResponse(**row._asdict()) for row in results]

@router.get("/daily-entries/{entry_id}", response_model=DailyEntryResponse)
async def get_daily_entry(entry_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Get a specific daily entry"""
    
    result = db.execute("SELECT * FROM daily_entries WHERE id = ?", (entry_id,)).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    if result.branch_id != current_user.branch_id:
        raise HTTPException(status_code=403, detail="Access denied to this entry")
    
    return DailyEntryResponse(**result._asdict())

@router.put("/daily-entries/{entry_id}", response_model=DailyEntryResponse)
async def update_daily_entry(
    entry_id: int, 
    entry_update: DailyEntryCreate,
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    """Update a daily entry"""
    
    # Check if entry exists and user has access
    existing = db.execute("SELECT * FROM daily_entries WHERE id = ?", (entry_id,)).fetchone()
    
    if not existing:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    if existing.branch_id != current_user.branch_id:
        raise HTTPException(status_code=403, detail="Access denied to this entry")
    
    # Update the entry
    total_amount = entry_update.consultation_fee + entry_update.test_fee
    
    db.execute("""
    UPDATE daily_entries SET 
        patient_id = ?, doctor_id = ?, visit_date = ?, consultation_fee = ?,
        test_fee = ?, total_amount = ?, test_type = ?, notes = ?,
        payment_status = ?, updated_at = ?
    WHERE id = ?
    """, (
        entry_update.patient_id, entry_update.doctor_id, entry_update.visit_date,
        entry_update.consultation_fee, entry_update.test_fee, total_amount,
        entry_update.test_type, entry_update.notes, entry_update.payment_status,
        datetime.now(), entry_id
    ))
    
    db.commit()
    
    # Get updated entry
    result = db.execute("SELECT * FROM daily_entries WHERE id = ?", (entry_id,)).fetchone()
    
    return DailyEntryResponse(**result._asdict())

@router.delete("/daily-entries/{entry_id}")
async def delete_daily_entry(entry_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Delete a daily entry"""
    
    # Check if entry exists and user has access
    existing = db.execute("SELECT * FROM daily_entries WHERE id = ?", (entry_id,)).fetchone()
    
    if not existing:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    if existing.branch_id != current_user.branch_id:
        raise HTTPException(status_code=403, detail="Access denied to this entry")
    
    db.execute("DELETE FROM daily_entries WHERE id = ?", (entry_id,))
    db.commit()
    
    return {"message": "Entry deleted successfully"}

@router.get("/daily-summary")
async def get_daily_summary(
    date: str = None,
    branch_id: int = None,
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    """Get daily summary statistics"""
    
    if not date:
        date = datetime.now().date().isoformat()
    
    if not branch_id:
        branch_id = current_user.branch_id
    
    # Get summary statistics
    summary = db.execute("""
    SELECT 
        COUNT(*) as total_patients,
        SUM(consultation_fee) as total_consultation_fee,
        SUM(test_fee) as total_test_fee,
        SUM(total_amount) as total_revenue,
        AVG(total_amount) as avg_revenue_per_patient
    FROM daily_entries 
    WHERE visit_date = ? AND branch_id = ?
    """, (date, branch_id)).fetchone()
    
    # Get payment status breakdown
    payment_status = db.execute("""
    SELECT 
        payment_status,
        COUNT(*) as count,
        SUM(total_amount) as amount
    FROM daily_entries 
    WHERE visit_date = ? AND branch_id = ?
    GROUP BY payment_status
    """, (date, branch_id)).fetchall()
    
    return {
        "date": date,
        "branch_id": branch_id,
        "total_patients": summary.total_patients or 0,
        "total_consultation_fee": summary.total_consultation_fee or 0,
        "total_test_fee": summary.total_test_fee or 0,
        "total_revenue": summary.total_revenue or 0,
        "avg_revenue_per_patient": round(summary.avg_revenue_per_patient or 0, 2),
        "payment_breakdown": [
            {
                "status": row.payment_status,
                "count": row.count,
                "amount": row.amount
            } for row in payment_status
        ]
    }
