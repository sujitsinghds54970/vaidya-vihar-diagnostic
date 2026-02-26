"""
HR/Payroll Models for VaidyaVihar Diagnostic ERP

Leave management and HR module:
- Leave types and policies
- Leave requests and approvals
- Leave balance tracking
- Staff attendance
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.utils.database import Base
import enum


class LeaveType(str, enum.Enum):
    """Leave type enumeration"""
    CASUAL = "casual"
    SICK = "sick"
    PRIVILEGED = "privileged"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    BEREAVEMENT = "bereavement"
    UNPAID = "unpaid"
    WORK_FROM_HOME = "work_from_home"
    COMPENSATORY = "compensatory"
    OTHER = "other"


class LeaveStatus(str, enum.Enum):
    """Leave status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class AttendanceStatus(str, enum.Enum):
    """Attendance status enumeration"""
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    HALF_DAY = "half_day"
    LEAVE = "leave"
    HOLIDAY = "holiday"
    WEEKOFF = "weekoff"


class LeavePolicy(Base):
    """Leave policy configuration"""
    __tablename__ = "leave_policies"

    id = Column(Integer, primary_key=True, index=True)
    leave_type = Column(SQLEnum(LeaveType), nullable=False, unique=True)
    
    # Allowance
    annual_quota = Column(Integer, default=0)  # Days per year
    monthly_quota = Column(Float, default=0)  # Days per month
    max_consecutive_days = Column(Integer, default=0)
    
    # Rules
    requires_approval = Column(Boolean, default=True)
    requires_document = Column(Boolean, default=False)
    can_carry_forward = Column(Boolean, default=False)
    max_carry_forward = Column(Integer, default=0)
    carry_forward_expiry_days = Column(Integer, default=0)
    
    # Encashment
    can_encash = Column(Boolean, default=False)
    max_encash_per_year = Column(Integer, default=0)
    
    # Probation rules
    applicable_after_days = Column(Integer, default=0)  # Days after joining
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Description
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LeaveBalance(Base):
    """Leave balance tracking per employee"""
    __tablename__ = "leave_balances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    leave_type = Column(SQLEnum(LeaveType), nullable=False)
    
    # Balance
    total_quota = Column(Integer, default=0)
    available = Column(Integer, default=0)
    used = Column(Integer, default=0)
    pending = Column(Integer, default=0)
    carried_forward = Column(Integer, default=0)
    
    # Period
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")


class LeaveRequest(Base):
    """Leave request model"""
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    leave_type = Column(SQLEnum(LeaveType), nullable=False)
    
    # Dates
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    total_days = Column(Float, default=0)
    
    # Half day options
    is_half_day = Column(Boolean, default=False)
    half_day_session = Column(String, nullable=True)  # morning, afternoon
    
    # Reason
    reason = Column(Text, nullable=True)
    emergency_contact = Column(String, nullable=True)
    
    # Document
    document_path = Column(String, nullable=True)
    
    # Status
    status = Column(SQLEnum(LeaveStatus), default=LeaveStatus.PENDING)
    
    # Approval
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Alternate arrangement
    alternate_arrangement = Column(Text, nullable=True)
    handover_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    approver = relationship("User", foreign_keys=[approved_by])


class Holiday(Base):
    """Company holidays"""
    __tablename__ = "holidays"

    id = Column(Integer, primary_key=True, index=True)
    holiday_date = Column(DateTime, nullable=False)
    holiday_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Type
    is_national_holiday = Column(Boolean, default=False)
    is_optional_holiday = Column(Boolean, default=False)
    
    # Branch specific
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)
    
    # Recurring
    is_recurring = Column(Boolean, default=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    branch = relationship("Branch")


class Attendance(Base):
    """Daily attendance tracking"""
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    attendance_date = Column(DateTime, nullable=False)
    
    # Status
    status = Column(SQLEnum(AttendanceStatus), default=AttendanceStatus.ABSENT)
    
    # Check-in/Check-out
    check_in = Column(DateTime, nullable=True)
    check_out = Column(DateTime, nullable=True)
    work_duration_hours = Column(Float, default=0)
    
    # Late arrival
    is_late = Column(Boolean, default=False)
    late_minutes = Column(Integer, default=0)
    
    # Overtime
    overtime_hours = Column(Float, default=0)
    overtime_approved = Column(Boolean, default=False)
    
    # Location (for remote/work from home)
    work_location = Column(String, nullable=True)  # office, home, field
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Approved by
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    approver = relationship("User", foreign_keys=[approved_by])


class AttendanceRegularization(Base):
    """Attendance correction requests"""
    __tablename__ = "attendance_regularizations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    attendance_id = Column(Integer, ForeignKey("attendances.id"), nullable=True)
    
    # Original data
    original_date = Column(DateTime, nullable=False)
    original_status = Column(String, nullable=True)
    original_check_in = Column(DateTime, nullable=True)
    original_check_out = Column(DateTime, nullable=True)
    
    # Requested data
    requested_status = Column(String, nullable=False)
    requested_check_in = Column(DateTime, nullable=True)
    requested_check_out = Column(DateTime, nullable=True)
    
    # Reason
    reason = Column(Text, nullable=True)
    
    # Status
    status = Column(SQLEnum(LeaveStatus), default=LeaveStatus.PENDING)
    
    # Approval
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    attendance = relationship("Attendance")
    approver = relationship("User", foreign_keys=[approved_by])


class WorkShift(Base):
    """Work shift configurations"""
    __tablename__ = "work_shifts"

    id = Column(Integer, primary_key=True, index=True)
    shift_name = Column(String, nullable=False)
    shift_code = Column(String, nullable=False, unique=True)
    
    # Timing
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    break_start = Column(DateTime, nullable=True)
    break_end = Column(DateTime, nullable=True)
    break_duration_minutes = Column(Integer, default=0)
    
    # Working hours
    total_hours = Column(Float, default=0)
    flexible_timing = Column(Boolean, default=False)
    late_mark_threshold_minutes = Column(Integer, default=0)
    
    # Days
    working_days = Column(String, nullable=True)  # JSON array of days
    
    # Status
    is_active = Column(Boolean, default=True)
    is_night_shift = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmployeeProfile(Base):
    """Extended employee profile for HR"""
    __tablename__ = "employee_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Personal details
    date_of_birth = Column(DateTime, nullable=True)
    gender = Column(String, nullable=True)
    blood_group = Column(String, nullable=True)
    marital_status = Column(String, nullable=True)
    
    # Employment details
    employee_id = Column(String, nullable=False, unique=True)
    department = Column(String, nullable=True)
    designation = Column(String, nullable=True)
    date_of_joining = Column(DateTime, nullable=True)
    probation_end_date = Column(DateTime, nullable=True)
    confirmation_date = Column(DateTime, nullable=True)
    
    # Work details
    shift_id = Column(Integer, ForeignKey("work_shifts.id"), nullable=True)
    reporting_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Salary details (encrypted in production)
    bank_name = Column(String, nullable=True)
    bank_account_number = Column(String, nullable=True)
    ifsc_code = Column(String, nullable=True)
    pan_number = Column(String, nullable=True)
    aadhar_number = Column(String, nullable=True)
    
    # Emergency contact
    emergency_contact_name = Column(String, nullable=True)
    emergency_contact_number = Column(String, nullable=True)
    emergency_contact_relation = Column(String, nullable=True)
    
    # Documents
    photo_path = Column(String, nullable=True)
    resume_path = Column(String, nullable=True)
    
    # Status
    employment_status = Column(String, default="active")  # active, on_leave, terminated
    is_rotational = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    shift = relationship("WorkShift")
    manager = relationship("User", foreign_keys=[reporting_to])


class LeaveApprovalWorkflow(Base):
    """Custom approval workflows for leave"""
    __tablename__ = "leave_approval_workflows"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Leave types this workflow applies to
    leave_types = Column(String, nullable=True)  # JSON array
    
    # Approval levels
    approval_levels = Column(String, nullable=True)  # JSON array of user IDs
    
    # Conditions
    min_days_for_approval = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

