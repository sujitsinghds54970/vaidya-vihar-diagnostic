from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional
from datetime import datetime, timedelta, time
from decimal import Decimal

from app.utils.database import get_db
from app.utils.auth_system import auth_guard, require_staff, get_current_user
from app.models import User, Branch, Staff, AttendanceRecord, SalaryRecord
from pydantic import BaseModel, Field
from datetime import time as dt_time

# Pydantic models for staff management
class StaffCreate(BaseModel):
    user_id: int
    department: str = Field(..., min_length=1, max_length=100)
    position: str = Field(..., min_length=1, max_length=100)
    date_of_joining: datetime
    salary: float = Field(..., gt=0)
    date_of_birth: datetime
    qualification: Optional[str] = Field(None, max_length=200)
    experience_years: int = Field(..., ge=0)

class StaffUpdate(BaseModel):
    department: Optional[str] = None
    position: Optional[str] = None
    salary: Optional[float] = None
    qualification: Optional[str] = None
    experience_years: Optional[int] = None
    total_leaves: Optional[int] = None
    leaves_taken: Optional[int] = None
    performance_rating: Optional[int] = Field(None, ge=1, le=5)
    is_active: Optional[bool] = None

class StaffResponse(BaseModel):
    id: int
    employee_id: str
    branch_id: int
    user_id: int
    department: str
    position: str
    date_of_joining: datetime
    salary: float
    date_of_birth: datetime
    qualification: Optional[str]
    experience_years: int
    total_leaves: int
    leaves_taken: int
    performance_rating: int
    is_active: bool
    created_at: datetime
    
    # Include user info
    first_name: str
    last_name: str
    username: str
    email: str
    phone: str
    role: str
    
    # Include branch info
    branch_name: str
    branch_location: str
    
    class Config:
        from_attributes = True

class AttendanceRecordCreate(BaseModel):
    attendance_date: datetime
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    status: str = Field(default="present", pattern=r"^(present|absent|late|half_day|leave)$")
    late_minutes: int = Field(default=0, ge=0)
    overtime_minutes: int = Field(default=0, ge=0)
    notes: Optional[str] = None

class AttendanceRecordUpdate(BaseModel):
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    status: Optional[str] = None
    late_minutes: Optional[int] = None
    overtime_minutes: Optional[int] = None
    notes: Optional[str] = None

class AttendanceRecordResponse(BaseModel):
    id: int
    staff_id: int
    attendance_date: datetime
    check_in_time: Optional[datetime]
    check_out_time: Optional[datetime]
    status: str
    late_minutes: int
    overtime_minutes: int
    notes: Optional[str]
    approved_by: Optional[int]
    created_at: datetime
    
    # Include staff info
    employee_id: str
    staff_name: str
    department: str
    
    class Config:
        from_attributes = True

class SalaryRecordCreate(BaseModel):
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020, le=2030)
    base_salary: float = Field(..., gt=0)
    bonus: float = Field(default=0, ge=0)
    deductions: float = Field(default=0, ge=0)
    payment_mode: Optional[str] = Field(None, pattern=r"^(cash|card|online|cheque)$")

class SalaryRecordResponse(BaseModel):
    id: int
    staff_id: int
    month: int
    year: int
    base_salary: float
    bonus: float
    deductions: float
    gross_salary: float
    net_salary: float
    payment_date: Optional[datetime]
    payment_status: str
    payment_mode: Optional[str]
    created_at: datetime
    
    # Include staff info
    employee_id: str
    staff_name: str
    department: str
    
    class Config:
        from_attributes = True

router = APIRouter()

@router.post("/staff/", response_model=StaffResponse)
def create_staff(
    staff_data: StaffCreate,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Create a new staff member"""
    
    # Check if user exists
    user = db.query(User).filter(User.id == staff_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check branch access
    if current_user.role != 'super_admin':
        staff_data.branch_id = current_user.branch_id
    
    # Generate employee ID
    branch = db.query(Branch).filter(Branch.id == staff_data.branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    branch_code = branch.name[:2].upper()
    last_staff = db.query(Staff).filter(
        Staff.branch_id == staff_data.branch_id
    ).order_by(desc(Staff.id)).first()
    
    if last_staff:
        try:
            last_number = int(last_staff.employee_id[-4:])
            new_number = last_number + 1
        except:
            new_number = 1
    else:
        new_number = 1
    
    employee_id = f"VV{branch_code}{new_number:04d}"
    
    # Check if employee ID already exists
    if db.query(Staff).filter(Staff.employee_id == employee_id).first():
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    
    # Create staff record
    db_staff = Staff(
        branch_id=staff_data.branch_id,
        user_id=staff_data.user_id,
        employee_id=employee_id,
        department=staff_data.department,
        position=staff_data.position,
        date_of_joining=staff_data.date_of_joining,
        salary=staff_data.salary,
        date_of_birth=staff_data.date_of_birth,
        qualification=staff_data.qualification,
        experience_years=staff_data.experience_years
    )
    
    db.add(db_staff)
    db.commit()
    db.refresh(db_staff)
    
    # Log activity
    auth_guard.log_activity(
        db=db,
        user=current_user,
        action="create",
        entity_type="staff",
        entity_id=db_staff.id,
        description=f"Created staff member {employee_id}"
    )
    
    return db_staff

@router.get("/staff/", response_model=List[StaffResponse])
def get_staff_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    branch_id: Optional[int] = Query(None),
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Get list of staff members"""
    
    # Filter by branch access
    if current_user.role == 'super_admin':
        query = db.query(Staff).join(User).join(Branch)
        if branch_id:
            query = query.filter(Staff.branch_id == branch_id)
    else:
        query = db.query(Staff).join(User).join(Branch).filter(
            Staff.branch_id == current_user.branch_id
        )
    
    # Search functionality
    if search:
        search_filter = or_(
            User.first_name.ilike(f"%{search}%"),
            User.last_name.ilike(f"%{search}%"),
            User.username.ilike(f"%{search}%"),
            Staff.employee_id.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    

    if department:
        # Department filter
        query = query.filter(Staff.department == department)
    
    # Only active staff
    query = query.filter(Staff.is_active == True, User.is_active == True)
    
    staff_list = query.order_by(desc(Staff.date_of_joining)).offset(skip).limit(limit).all()
    
    return staff_list

@router.get("/staff/{staff_id}", response_model=StaffResponse)
def get_staff(
    staff_id: int,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Get staff member by ID"""
    
    staff = db.query(Staff).filter(Staff.id == staff_id).join(User).join(Branch).first()
    
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    # Check branch access
    if current_user.role != 'super_admin' and staff.branch_id != current_user.branch_id:
        raise HTTPException(status_code=403, detail="Access denied to this staff member")
    
    return staff

@router.put("/staff/{staff_id}", response_model=StaffResponse)
def update_staff(
    staff_id: int,
    staff_data: StaffUpdate,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Update staff member information"""
    
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    # Check branch access
    if current_user.role != 'super_admin' and staff.branch_id != current_user.branch_id:
        raise HTTPException(status_code=403, detail="Access denied to this staff member")
    
    # Update fields
    for field, value in staff_data.dict(exclude_unset=True).items():
        setattr(staff, field, value)
    
    db.commit()
    db.refresh(staff)
    
    # Log activity
    auth_guard.log_activity(
        db=db,
        user=current_user,
        action="update",
        entity_type="staff",
        entity_id=staff.id,
        description=f"Updated staff member {staff.employee_id}"
    )
    
    return staff

@router.delete("/staff/{staff_id}")
def deactivate_staff(
    staff_id: int,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Deactivate staff member (soft delete)"""
    
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    # Check branch access
    if current_user.role != 'super_admin' and staff.branch_id != current_user.branch_id:
        raise HTTPException(status_code=403, detail="Access denied to this staff member")
    
    # Deactivate staff
    staff.is_active = False
    db.commit()
    
    # Log activity
    auth_guard.log_activity(
        db=db,
        user=current_user,
        action="deactivate",
        entity_type="staff",
        entity_id=staff.id,
        description=f"Deactivated staff member {staff.employee_id}"
    )
    
    return {"message": "Staff member deactivated successfully"}

# Attendance Management
@router.post("/attendance/", response_model=AttendanceRecordResponse)
def create_attendance_record(
    attendance_data: AttendanceRecordCreate,
    staff_id: int,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Create attendance record for staff"""
    
    staff = db.query(Staff).filter(Staff.id == staff_id).join(User).join(Branch).first()
    
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    # Check branch access
    if current_user.role != 'super_admin' and staff.branch_id != current_user.branch_id:
        raise HTTPException(status_code=403, detail="Access denied to this staff member")
    
    # Check for existing attendance record for the same date
    existing_record = db.query(AttendanceRecord).filter(
        and_(
            AttendanceRecord.staff_id == staff_id,
            AttendanceRecord.attendance_date >= attendance_data.attendance_date.date(),
            AttendanceRecord.attendance_date < attendance_data.attendance_date.date() + timedelta(days=1)
        )
    ).first()
    
    if existing_record:
        raise HTTPException(
            status_code=400,
            detail="Attendance record already exists for this date"
        )
    
    # Create attendance record
    db_attendance = AttendanceRecord(
        staff_id=staff_id,
        attendance_date=attendance_data.attendance_date,
        check_in_time=attendance_data.check_in_time,
        check_out_time=attendance_data.check_out_time,
        status=attendance_data.status,
        late_minutes=attendance_data.late_minutes,
        overtime_minutes=attendance_data.overtime_minutes,
        notes=attendance_data.notes,
        approved_by=current_user.id
    )
    
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    
    # Log activity
    auth_guard.log_activity(
        db=db,
        user=current_user,
        action="create",
        entity_type="attendance_record",
        entity_id=db_attendance.id,
        description=f"Created attendance record for {staff.employee_id} on {attendance_data.attendance_date.date()}"
    )
    
    return db_attendance

@router.get("/attendance/", response_model=List[AttendanceRecordResponse])
def get_attendance_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    staff_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    status: Optional[str] = Query(None),
    branch_id: Optional[int] = Query(None),
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Get attendance records with filtering"""
    
    # Filter by branch access
    if current_user.role == 'super_admin':
        query = db.query(AttendanceRecord).join(Staff).join(User).join(Branch)
        if branch_id:
            query = query.filter(Staff.branch_id == branch_id)
    else:
        query = db.query(AttendanceRecord).join(Staff).join(User).join(Branch).filter(
            Staff.branch_id == current_user.branch_id
        )
    
    # Apply filters
    if staff_id:
        query = query.filter(AttendanceRecord.staff_id == staff_id)
    if start_date:
        query = query.filter(AttendanceRecord.attendance_date >= start_date)
    if end_date:
        query = query.filter(AttendanceRecord.attendance_date <= end_date)
    if status:
        query = query.filter(AttendanceRecord.status == status)
    
    records = query.order_by(desc(AttendanceRecord.attendance_date)).offset(skip).limit(limit).all()
    
    return records

@router.put("/attendance/{attendance_id}", response_model=AttendanceRecordResponse)
def update_attendance_record(
    attendance_id: int,
    attendance_data: AttendanceRecordUpdate,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Update attendance record"""
    
    attendance = db.query(AttendanceRecord).filter(AttendanceRecord.id == attendance_id).join(Staff).join(User).join(Branch).first()
    
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    # Check branch access
    if current_user.role != 'super_admin' and attendance.staff.branch_id != current_user.branch_id:
        raise HTTPException(status_code=403, detail="Access denied to this attendance record")
    
    # Update fields
    for field, value in attendance_data.dict(exclude_unset=True).items():
        setattr(attendance, field, value)
    
    db.commit()
    db.refresh(attendance)
    
    # Log activity
    auth_guard.log_activity(
        db=db,
        user=current_user,
        action="update",
        entity_type="attendance_record",
        entity_id=attendance.id,
        description=f"Updated attendance record {attendance.id}"
    )
    
    return attendance

@router.get("/attendance/summary")
def get_attendance_summary(
    year: int = Query(..., ge=2020, le=2030),
    month: int = Query(..., ge=1, le=12),
    staff_id: Optional[int] = Query(None),
    branch_id: Optional[int] = Query(None),
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Get attendance summary for a specific month"""
    
    # Filter by branch access
    if current_user.role == 'super_admin':
        query = db.query(AttendanceRecord).join(Staff).join(User).join(Branch)
        if branch_id:
            query = query.filter(Staff.branch_id == branch_id)
    else:
        query = db.query(AttendanceRecord).join(Staff).join(User).join(Branch).filter(
            Staff.branch_id == current_user.branch_id
        )
    
    # Date range for the month
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)
    
    query = query.filter(
        and_(
            AttendanceRecord.attendance_date >= start_date,
            AttendanceRecord.attendance_date <= end_date
        )
    )
    
    if staff_id:
        query = query.filter(AttendanceRecord.staff_id == staff_id)
    
    records = query.all()
    
    # Calculate summary
    summary = {
        "period": f"{year}-{month:02d}",
        "total_records": len(records),
        "present_days": len([r for r in records if r.status == "present"]),
        "absent_days": len([r for r in records if r.status == "absent"]),
        "late_days": len([r for r in records if r.status == "late"]),
        "half_days": len([r for r in records if r.status == "half_day"]),
        "leave_days": len([r for r in records if r.status == "leave"]),
        "total_late_minutes": sum(r.late_minutes for r in records),
        "total_overtime_minutes": sum(r.overtime_minutes for r in records)
    }
    
    return summary

# Salary Management
@router.post("/salary/", response_model=SalaryRecordResponse)
def create_salary_record(
    salary_data: SalaryRecordCreate,
    staff_id: int,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Create salary record for staff"""
    
    staff = db.query(Staff).filter(Staff.id == staff_id).join(User).join(Branch).first()
    
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    # Check branch access
    if current_user.role != 'super_admin' and staff.branch_id != current_user.branch_id:
        raise HTTPException(status_code=403, detail="Access denied to this staff member")
    
    # Check if salary record already exists for this month/year
    existing_record = db.query(SalaryRecord).filter(
        and_(
            SalaryRecord.staff_id == staff_id,
            SalaryRecord.month == salary_data.month,
            SalaryRecord.year == salary_data.year
        )
    ).first()
    
    if existing_record:
        raise HTTPException(
            status_code=400,
            detail="Salary record already exists for this month/year"
        )
    
    # Calculate gross and net salary
    gross_salary = salary_data.base_salary + salary_data.bonus
    net_salary = gross_salary - salary_data.deductions
    
    # Create salary record
    db_salary = SalaryRecord(
        staff_id=staff_id,
        month=salary_data.month,
        year=salary_data.year,
        base_salary=salary_data.base_salary,
        bonus=salary_data.bonus,
        deductions=salary_data.deductions,
        gross_salary=gross_salary,
        net_salary=net_salary,
        payment_mode=salary_data.payment_mode
    )
    
    db.add(db_salary)
    db.commit()
    db.refresh(db_salary)
    
    # Log activity
    auth_guard.log_activity(
        db=db,
        user=current_user,
        action="create",
        entity_type="salary_record",
        entity_id=db_salary.id,
        description=f"Created salary record for {staff.employee_id} for {salary_data.year}-{salary_data.month:02d}"
    )
    
    return db_salary

@router.get("/salary/", response_model=List[SalaryRecordResponse])
def get_salary_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    staff_id: Optional[int] = Query(None),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    branch_id: Optional[int] = Query(None),
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Get salary records with filtering"""
    
    # Filter by branch access
    if current_user.role == 'super_admin':
        query = db.query(SalaryRecord).join(Staff).join(User).join(Branch)
        if branch_id:
            query = query.filter(Staff.branch_id == branch_id)
    else:
        query = db.query(SalaryRecord).join(Staff).join(User).join(Branch).filter(
            Staff.branch_id == current_user.branch_id
        )
    
    # Apply filters
    if staff_id:
        query = query.filter(SalaryRecord.staff_id == staff_id)
    if year:
        query = query.filter(SalaryRecord.year == year)
    if month:
        query = query.filter(SalaryRecord.month == month)
    
    records = query.order_by(desc(SalaryRecord.year), desc(SalaryRecord.month)).offset(skip).limit(limit).all()
    
    return records

@router.put("/salary/{salary_id}/mark-paid")
def mark_salary_as_paid(
    salary_id: int,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Mark salary as paid"""
    
    salary = db.query(SalaryRecord).filter(SalaryRecord.id == salary_id).join(Staff).join(User).join(Branch).first()
    
    if not salary:
        raise HTTPException(status_code=404, detail="Salary record not found")
    
    # Check branch access
    if current_user.role != 'super_admin' and salary.staff.branch_id != current_user.branch_id:
        raise HTTPException(status_code=403, detail="Access denied to this salary record")
    
    # Mark as paid
    salary.payment_status = "paid"
    salary.payment_date = datetime.utcnow()
    
    db.commit()
    
    # Log activity
    auth_guard.log_activity(
        db=db,
        user=current_user,
        action="update",
        entity_type="salary_record",
        entity_id=salary.id,
        description=f"Marked salary as paid for {salary.staff.employee_id}"
    )
    
    return {"message": "Salary marked as paid successfully"}

@router.get("/departments")
def get_departments(
    branch_id: Optional[int] = Query(None),
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Get list of departments"""
    
    # Filter by branch access
    if current_user.role == 'super_admin':
        query = db.query(Staff.department).distinct()
        if branch_id:
            query = query.filter(Staff.branch_id == branch_id)
    else:
        query = db.query(Staff.department).filter(
            Staff.branch_id == current_user.branch_id
        ).distinct()
    
    departments = query.all()
    
    return [{"department": dept[0]} for dept in departments]
