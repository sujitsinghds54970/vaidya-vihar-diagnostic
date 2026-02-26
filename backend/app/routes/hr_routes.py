"""
HR/Payroll Routes for VaidyaVihar Diagnostic ERP

HR management endpoints:
- Leave management
- Attendance tracking
- Employee profiles
- Holiday management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta, date
import uuid

from app.utils.database import get_db
from app.models.hr import (
    LeaveRequest, LeaveBalance, LeavePolicy, LeaveStatus, LeaveType,
    Attendance, AttendanceStatus, Holiday, EmployeeProfile, WorkShift
)

router = APIRouter()


# Pydantic Schemas
class LeaveRequestCreate(BaseModel):
    leave_type: str
    start_date: datetime
    end_date: datetime
    is_half_day: bool = False
    half_day_session: Optional[str] = None
    reason: Optional[str] = None
    emergency_contact: Optional[str] = None


class LeaveRequestUpdate(BaseModel):
    status: Optional[str] = None
    approved_by: Optional[int] = None
    rejection_reason: Optional[str] = None


class AttendanceCreate(BaseModel):
    user_id: int
    attendance_date: datetime
    status: str
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    notes: Optional[str] = None


class AttendanceUpdate(BaseModel):
    status: Optional[str] = None
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    notes: Optional[str] = None


class HolidayCreate(BaseModel):
    holiday_date: datetime
    holiday_name: str
    description: Optional[str] = None
    is_national_holiday: bool = False
    is_optional_holiday: bool = False
    branch_id: Optional[int] = None


class EmployeeProfileCreate(BaseModel):
    user_id: int
    employee_id: str
    department: Optional[str] = None
    designation: Optional[str] = None
    date_of_joining: Optional[datetime] = None
    shift_id: Optional[int] = None
    reporting_to: Optional[int] = None
    blood_group: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_number: Optional[str] = None
    emergency_contact_relation: Optional[str] = None


# Leave Endpoints
@router.post("/leave-requests")
async def create_leave_request(
    leave_data: LeaveRequestCreate,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Create a leave request"""
    # Calculate total days
    delta = leave_data.end_date - leave_data.start_date
    total_days = delta.days + 1
    
    if leave_data.is_half_day:
        total_days = 0.5
    
    leave_request = LeaveRequest(
        user_id=user_id,
        leave_type=LeaveType(leave_data.leave_type),
        start_date=leave_data.start_date,
        end_date=leave_data.end_date,
        total_days=total_days,
        is_half_day=leave_data.is_half_day,
        half_day_session=leave_data.half_day_session,
        reason=leave_data.reason,
        emergency_contact=leave_data.emergency_contact
    )
    
    db.add(leave_request)
    db.commit()
    db.refresh(leave_request)
    
    return {
        "success": True,
        "leave_request": {
            "id": leave_request.id,
            "leave_type": leave_request.leave_type.value if leave_request.leave_type else None,
            "start_date": leave_request.start_date.isoformat(),
            "end_date": leave_request.end_date.isoformat(),
            "total_days": leave_request.total_days,
            "status": leave_request.status.value if leave_request.status else None,
            "created_at": leave_request.created_at.isoformat()
        }
    }


@router.get("/leave-requests")
async def list_leave_requests(
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List leave requests"""
    query = db.query(LeaveRequest)
    
    if user_id:
        query = query.filter(LeaveRequest.user_id == user_id)
    if status:
        query = query.filter(LeaveRequest.status == LeaveStatus(status))
    
    requests = query.order_by(LeaveRequest.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "success": True,
        "leave_requests": [
            {
                "id": lr.id,
                "user_id": lr.user_id,
                "leave_type": lr.leave_type.value if lr.leave_type else None,
                "start_date": lr.start_date.isoformat(),
                "end_date": lr.end_date.isoformat(),
                "total_days": lr.total_days,
                "is_half_day": lr.is_half_day,
                "reason": lr.reason,
                "status": lr.status.value if lr.status else None,
                "created_at": lr.created_at.isoformat()
            }
            for lr in requests
        ]
    }


@router.put("/leave-requests/{request_id}")
async def update_leave_request(
    request_id: int,
    request_data: LeaveRequestUpdate,
    db: Session = Depends(get_db)
):
    """Update leave request (approve/reject)"""
    leave_request = db.query(LeaveRequest).filter(LeaveRequest.id == request_id).first()
    
    if not leave_request:
        raise HTTPException(status_code=404, detail="Leave request not found")
    
    if request_data.status:
        leave_request.status = LeaveStatus(request_data.status)
        
        if request_data.status == "approved":
            leave_request.approved_by = request_data.approved_by
            leave_request.approved_at = datetime.utcnow()
            
            # Update leave balance
            balance = db.query(LeaveBalance).filter(
                LeaveBalance.user_id == leave_request.user_id,
                LeaveBalance.leave_type == leave_request.leave_type
            ).first()
            
            if balance:
                balance.used += leave_request.total_days
                balance.available -= leave_request.total_days
                balance.pending -= leave_request.total_days
                
        elif request_data.status == "rejected":
            leave_request.rejection_reason = request_data.rejection_reason
    
    db.commit()
    db.refresh(leave_request)
    
    return {
        "success": True,
        "leave_request": {
            "id": leave_request.id,
            "status": leave_request.status.value if leave_request.status else None
        }
    }


@router.get("/leave-balance/{user_id}")
async def get_leave_balance(user_id: int, db: Session = Depends(get_db)):
    """Get leave balance for a user"""
    balances = db.query(LeaveBalance).filter(LeaveBalance.user_id == user_id).all()
    
    return {
        "success": True,
        "balances": [
            {
                "leave_type": bl.leave_type.value if bl.leave_type else None,
                "total_quota": bl.total_quota,
                "available": bl.available,
                "used": bl.used,
                "pending": bl.pending
            }
            for bl in balances
        ]
    }


@router.get("/leave-policies")
async def list_leave_policies(db: Session = Depends(get_db)):
    """List leave policies"""
    policies = db.query(LeavePolicy).filter(LeavePolicy.is_active == True).all()
    
    return {
        "success": True,
        "policies": [
            {
                "id": p.id,
                "leave_type": p.leave_type.value if p.leave_type else None,
                "annual_quota": p.annual_quota,
                "monthly_quota": p.monthly_quota,
                "requires_approval": p.requires_approval,
                "description": p.description
            }
            for p in policies
        ]
    }


# Attendance Endpoints
@router.post("/attendance")
async def create_attendance(attendance_data: AttendanceCreate, db: Session = Depends(get_db)):
    """Record attendance"""
    # Calculate work duration if both check-in and check-out provided
    work_duration = 0
    if attendance_data.check_in and attendance_data.check_out:
        delta = attendance_data.check_out - attendance_data.check_in
        work_duration = delta.total_seconds() / 3600
    
    attendance = Attendance(
        user_id=attendance_data.user_id,
        attendance_date=attendance_data.attendance_date,
        status=AttendanceStatus(attendance_data.status),
        check_in=attendance_data.check_in,
        check_out=attendance_data.check_out,
        work_duration_hours=work_duration,
        notes=attendance_data.notes
    )
    
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    
    return {
        "success": True,
        "attendance": {
            "id": attendance.id,
            "user_id": attendance.user_id,
            "attendance_date": attendance.attendance_date.isoformat(),
            "status": attendance.status.value if attendance.status else None,
            "check_in": attendance.check_in.isoformat() if attendance.check_in else None,
            "check_out": attendance.check_out.isoformat() if attendance.check_out else None,
            "work_duration_hours": attendance.work_duration_hours
        }
    }


@router.get("/attendance")
async def list_attendance(
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List attendance records"""
    query = db.query(Attendance)
    
    if user_id:
        query = query.filter(Attendance.user_id == user_id)
    if start_date:
        query = query.filter(Attendance.attendance_date >= start_date)
    if end_date:
        query = query.filter(Attendance.attendance_date <= end_date)
    
    records = query.order_by(Attendance.attendance_date.desc()).offset(skip).limit(limit).all()
    
    return {
        "success": True,
        "attendance": [
            {
                "id": att.id,
                "user_id": att.user_id,
                "attendance_date": att.attendance_date.isoformat(),
                "status": att.status.value if att.status else None,
                "check_in": att.check_in.isoformat() if att.check_in else None,
                "check_out": att.check_out.isoformat() if att.check_out else None,
                "work_duration_hours": att.work_duration_hours
            }
            for att in records
        ]
    }


@router.get("/attendance/today")
async def get_today_attendance(db: Session = Depends(get_db)):
    """Get today's attendance for all users"""
    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())
    
    attendance = db.query(Attendance).filter(
        Attendance.attendance_date.between(start_of_day, end_of_day)
    ).all()
    
    return {
        "success": True,
        "attendance": [
            {
                "id": att.id,
                "user_id": att.user_id,
                "status": att.status.value if att.status else None,
                "check_in": att.check_in.isoformat() if att.check_in else None
            }
            for att in attendance
        ]
    }


@router.put("/attendance/{attendance_id}")
async def update_attendance(
    attendance_id: int,
    attendance_data: AttendanceUpdate,
    db: Session = Depends(get_db)
):
    """Update attendance record"""
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")
    
    if attendance_data.status:
        attendance.status = AttendanceStatus(attendance_data.status)
    if attendance_data.check_in:
        attendance.check_in = attendance_data.check_in
    if attendance_data.check_out:
        attendance.check_out = attendance_data.check_out
    if attendance_data.notes is not None:
        attendance.notes = attendance_data.notes
    
    # Recalculate work duration
    if attendance.check_in and attendance.check_out:
        delta = attendance.check_out - attendance.check_in
        attendance.work_duration_hours = delta.total_seconds() / 3600
    
    db.commit()
    db.refresh(attendance)
    
    return {
        "success": True,
        "attendance": {
            "id": attendance.id,
            "status": attendance.status.value if attendance.status else None,
            "work_duration_hours": attendance.work_duration_hours
        }
    }


# Holiday Endpoints
@router.post("/holidays")
async def create_holiday(holiday_data: HolidayCreate, db: Session = Depends(get_db)):
    """Create a holiday"""
    holiday = Holiday(
        holiday_date=holiday_data.holiday_date,
        holiday_name=holiday_data.holiday_name,
        description=holiday_data.description,
        is_national_holiday=holiday_data.is_national_holiday,
        is_optional_holiday=holiday_data.is_optional_holiday,
        branch_id=holiday_data.branch_id
    )
    
    db.add(holiday)
    db.commit()
    db.refresh(holiday)
    
    return {
        "success": True,
        "holiday": {
            "id": holiday.id,
            "holiday_name": holiday.holiday_name,
            "holiday_date": holiday.holiday_date.isoformat(),
            "is_national_holiday": holiday.is_national_holiday
        }
    }


@router.get("/holidays")
async def list_holidays(
    year: Optional[int] = None,
    branch_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """List holidays"""
    query = db.query(Holiday).filter(Holiday.is_active == True)
    
    if year:
        start_of_year = datetime(year, 1, 1)
        end_of_year = datetime(year, 12, 31, 23, 59, 59)
        query = query.filter(Holiday.holiday_date.between(start_of_year, end_of_year))
    
    if branch_id:
        query = query.filter((Holiday.branch_id == branch_id) | (Holiday.branch_id == None))
    
    holidays = query.order_by(Holiday.holiday_date).all()
    
    return {
        "success": True,
        "holidays": [
            {
                "id": h.id,
                "holiday_name": h.holiday_name,
                "holiday_date": h.holiday_date.isoformat(),
                "is_national_holiday": h.is_national_holiday,
                "is_optional_holiday": h.is_optional_holiday
            }
            for h in holidays
        ]
    }


# Employee Profile Endpoints
@router.post("/employee-profiles")
async def create_employee_profile(profile_data: EmployeeProfileCreate, db: Session = Depends(get_db)):
    """Create employee profile"""
    profile = EmployeeProfile(
        user_id=profile_data.user_id,
        employee_id=profile_data.employee_id,
        department=profile_data.department,
        designation=profile_data.designation,
        date_of_joining=profile_data.date_of_joining,
        shift_id=profile_data.shift_id,
        reporting_to=profile_data.reporting_to,
        blood_group=profile_data.blood_group,
        emergency_contact_name=profile_data.emergency_contact_name,
        emergency_contact_number=profile_data.emergency_contact_number,
        emergency_contact_relation=profile_data.emergency_contact_relation
    )
    
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    return {
        "success": True,
        "profile": {
            "id": profile.id,
            "user_id": profile.user_id,
            "employee_id": profile.employee_id,
            "department": profile.department,
            "designation": profile.designation
        }
    }


@router.get("/employee-profiles")
async def list_employee_profiles(
    department: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List employee profiles"""
    query = db.query(EmployeeProfile)
    
    if department:
        query = query.filter(EmployeeProfile.department == department)
    
    profiles = query.offset(skip).limit(limit).all()
    
    return {
        "success": True,
        "profiles": [
            {
                "id": p.id,
                "user_id": p.user_id,
                "employee_id": p.employee_id,
                "department": p.department,
                "designation": p.designation,
                "date_of_joining": p.date_of_joining.isoformat() if p.date_of_joining else None,
                "employment_status": p.employment_status
            }
            for p in profiles
        ]
    }


@router.get("/employee-profiles/{user_id}")
async def get_employee_profile(user_id: int, db: Session = Depends(get_db)):
    """Get employee profile"""
    profile = db.query(EmployeeProfile).filter(EmployeeProfile.user_id == user_id).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    
    return {
        "success": True,
        "profile": {
            "id": profile.id,
            "user_id": profile.user_id,
            "employee_id": profile.employee_id,
            "department": profile.department,
            "designation": profile.designation,
            "date_of_joining": profile.date_of_joining.isoformat() if profile.date_of_joining else None,
            "blood_group": profile.blood_group,
            "emergency_contact_name": profile.emergency_contact_name,
            "emergency_contact_number": profile.emergency_contact_number,
            "employment_status": profile.employment_status
        }
    }


# Work Shift Endpoints
@router.get("/shifts")
async def list_shifts(db: Session = Depends(get_db)):
    """List work shifts"""
    shifts = db.query(WorkShift).filter(WorkShift.is_active == True).all()
    
    return {
        "success": True,
        "shifts": [
            {
                "id": s.id,
                "shift_name": s.shift_name,
                "shift_code": s.shift_code,
                "start_time": s.start_time.isoformat() if s.start_time else None,
                "end_time": s.end_time.isoformat() if s.end_time else None,
                "total_hours": s.total_hours
            }
            for s in shifts
        ]
    }

