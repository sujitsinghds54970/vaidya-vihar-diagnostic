from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional
from datetime import datetime

from app.utils.database import get_db
from app.utils.auth_system import auth_guard, require_staff, get_current_user
from app.models import User, Branch
from pydantic import BaseModel, Field

# Pydantic models for branch management
class BranchCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    location: str = Field(..., min_length=1, max_length=200)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    pincode: str = Field(..., min_length=6, max_length=10)
    phone: str = Field(..., min_length=10, max_length=15)
    email: Optional[str] = Field(None, max_length=200)
    address: str = Field(..., min_length=5)
    license_number: Optional[str] = Field(None, max_length=100)
    opening_hours: Optional[str] = Field(None, max_length=500)
    facilities: Optional[str] = Field(None, max_length=1000)

class BranchUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    license_number: Optional[str] = None
    opening_hours: Optional[str] = None
    facilities: Optional[str] = None
    is_active: Optional[bool] = None

class BranchResponse(BaseModel):
    id: int
    name: str
    location: str
    city: str
    state: str
    pincode: str
    phone: str
    email: Optional[str]
    address: str
    license_number: Optional[str]
    opening_hours: Optional[str]
    facilities: Optional[str]
    branch_code: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Computed fields
    total_staff: Optional[int] = 0
    total_patients: Optional[int] = 0
    monthly_revenue: Optional[float] = 0.0
    
    class Config:
        from_attributes = True

class BranchStatistics(BaseModel):
    branch_id: int
    branch_name: str
    total_staff: int
    total_patients: int
    monthly_revenue: float
    total_appointments: int
    pending_payments: float
    inventory_value: float
    active_services: int

router = APIRouter()

@router.post("/branches/", response_model=BranchResponse)
def create_branch(
    branch_data: BranchCreate,
    current_user: User = Depends(auth_guard.require_role(['super_admin'])),
    db: Session = Depends(get_db)
):
    """Create a new branch (super admin only)"""
    
    # Check for duplicate branch name
    existing_branch = db.query(Branch).filter(Branch.name == branch_data.name).first()
    
    if existing_branch:
        raise HTTPException(
            status_code=400,
            detail="Branch with this name already exists"
        )
    
    # Generate branch code
    branch_name = branch_data.name.upper().replace(" ", "")[:3]
    last_branch = db.query(Branch).order_by(desc(Branch.id)).first()
    
    if last_branch:
        try:
            last_number = int(last_branch.branch_code[-3:])
            new_number = last_number + 1
        except:
            new_number = 1
    else:
        new_number = 1
    
    branch_code = f"VV{branch_name[:2]}{new_number:03d}"
    
    # Create branch
    db_branch = Branch(
        name=branch_data.name,
        location=branch_data.location,
        city=branch_data.city,
        state=branch_data.state,
        pincode=branch_data.pincode,
        phone=branch_data.phone,
        email=branch_data.email,
        address=branch_data.address,
        license_number=branch_data.license_number,
        opening_hours=branch_data.opening_hours,
        facilities=branch_data.facilities,
        branch_code=branch_code
    )
    
    db.add(db_branch)
    db.commit()
    db.refresh(db_branch)
    
    # Log activity
    auth_guard.log_activity(
        db=db,
        user=current_user,
        action="create",
        entity_type="branch",
        entity_id=db_branch.id,
        description=f"Created branch {db_branch.name}"
    )
    
    return db_branch

@router.get("/branches/", response_model=List[BranchResponse])
def get_branches(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    active_only: bool = Query(True),
    include_stats: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of branches with filtering"""
    
    # Super admin can see all branches, others only their branch
    if current_user.role == 'super_admin':
        query = db.query(Branch)
    else:
        query = db.query(Branch).filter(Branch.id == current_user.branch_id)
    
    # Apply filters
    if search:
        query = query.filter(
            Branch.name.ilike(f"%{search}%") |
            Branch.location.ilike(f"%{search}%") |
            Branch.city.ilike(f"%{search}%") |
            Branch.branch_code.ilike(f"%{search}%")
        )
    
    if city:
        query = query.filter(Branch.city == city)
    
    if state:
        query = query.filter(Branch.state == state)
    
    if active_only:
        query = query.filter(Branch.is_active == True)
    
    branches = query.order_by(desc(Branch.created_at)).offset(skip).limit(limit).all()
    
    # Add statistics if requested
    if include_stats:
        for branch in branches:
            # Calculate statistics
            from app.models import Staff, Patient, DailyEntry, InventoryItem
            
            # Total staff
            branch.total_staff = db.query(Staff).filter(
                Staff.branch_id == branch.id,
                Staff.is_active == True
            ).count()
            
            # Total patients
            branch.total_patients = db.query(Patient).filter(
                Patient.branch_id == branch.id,
                Patient.is_active == True
            ).count()
            
            # Monthly revenue (current month)
            current_month = datetime.now().replace(day=1)
            monthly_revenue = db.query(DailyEntry).filter(
                and_(
                    DailyEntry.branch_id == branch.id,
                    DailyEntry.entry_date >= current_month
                )
            ).all()
            
            branch.monthly_revenue = sum(float(entry.total_amount) for entry in monthly_revenue)
    
    return branches

@router.get("/branches/{branch_id}", response_model=BranchResponse)
def get_branch(
    branch_id: int,
    include_stats: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get branch by ID"""
    
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    # Check access - super admin can see all, others only their branch
    if current_user.role != 'super_admin' and branch.id != current_user.branch_id:
        raise HTTPException(status_code=403, detail="Access denied to this branch")
    
    # Add statistics if requested
    if include_stats:
        from app.models import Staff, Patient, DailyEntry, InventoryItem
        
        # Total staff
        branch.total_staff = db.query(Staff).filter(
            Staff.branch_id == branch.id,
            Staff.is_active == True
        ).count()
        
        # Total patients
        branch.total_patients = db.query(Patient).filter(
            Patient.branch_id == branch.id,
            Patient.is_active == True
        ).count()
        
        # Monthly revenue (current month)
        current_month = datetime.now().replace(day=1)
        monthly_revenue = db.query(DailyEntry).filter(
            and_(
                DailyEntry.branch_id == branch.id,
                DailyEntry.entry_date >= current_month
            )
        ).all()
        
        branch.monthly_revenue = sum(float(entry.total_amount) for entry in monthly_revenue)
    
    return branch

@router.put("/branches/{branch_id}", response_model=BranchResponse)
def update_branch(
    branch_id: int,
    branch_data: BranchUpdate,
    current_user: User = Depends(auth_guard.require_role(['super_admin', 'branch_admin'])),
    db: Session = Depends(get_db)
):
    """Update branch information"""
    
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    # Check access - super admin can update any, branch admin can only update their branch
    if current_user.role == 'branch_admin' and branch.id != current_user.branch_id:
        raise HTTPException(status_code=403, detail="Access denied to this branch")
    
    # Update fields
    for field, value in branch_data.dict(exclude_unset=True).items():
        setattr(branch, field, value)
    
    # Update timestamp
    branch.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(branch)
    
    # Log activity
    auth_guard.log_activity(
        db=db,
        user=current_user,
        action="update",
        entity_type="branch",
        entity_id=branch.id,
        description=f"Updated branch {branch.name}"
    )
    
    return branch

@router.delete("/branches/{branch_id}")
def deactivate_branch(
    branch_id: int,
    current_user: User = Depends(auth_guard.require_role(['super_admin'])),
    db: Session = Depends(get_db)
):
    """Deactivate branch (super admin only)"""
    
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    # Check if branch has active staff or patients
    from app.models import Staff, Patient
    
    active_staff = db.query(Staff).filter(
        and_(
            Staff.branch_id == branch_id,
            Staff.is_active == True
        )
    ).count()
    
    active_patients = db.query(Patient).filter(
        and_(
            Patient.branch_id == branch_id,
            Patient.is_active == True
        )
    ).count()
    
    if active_staff > 0 or active_patients > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot deactivate branch with active staff or patients. Please transfer or deactivate them first."
        )
    
    # Deactivate branch
    branch.is_active = False
    branch.updated_at = datetime.utcnow()
    
    db.commit()
    
    # Log activity
    auth_guard.log_activity(
        db=db,
        user=current_user,
        action="deactivate",
        entity_type="branch",
        entity_id=branch.id,
        description=f"Deactivated branch {branch.name}"
    )
    
    return {"message": "Branch deactivated successfully"}

@router.get("/branches/{branch_id}/statistics", response_model=BranchStatistics)
def get_branch_statistics(
    branch_id: int,
    year: int = Query(datetime.now().year, ge=2020, le=2030),
    month: int = Query(datetime.now().month, ge=1, le=12),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive branch statistics"""
    
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    # Check access
    if current_user.role != 'super_admin' and branch.id != current_user.branch_id:
        raise HTTPException(status_code=403, detail="Access denied to this branch")
    
    from app.models import Staff, Patient, DailyEntry, InventoryItem, Invoice
    
    # Calculate date range for the month
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - datetime.timedelta(days=1)
    
    # Total staff
    total_staff = db.query(Staff).filter(
        and_(
            Staff.branch_id == branch_id,
            Staff.is_active == True
        )
    ).count()
    
    # Total patients
    total_patients = db.query(Patient).filter(
        and_(
            Patient.branch_id == branch_id,
            Patient.is_active == True
        )
    ).count()
    
    # Monthly revenue
    daily_entries = db.query(DailyEntry).filter(
        and_(
            DailyEntry.branch_id == branch_id,
            DailyEntry.entry_date >= start_date,
            DailyEntry.entry_date <= end_date
        )
    ).all()
    
    monthly_revenue = sum(float(entry.total_amount) for entry in daily_entries)
    
    # Total appointments (based on daily entries)
    total_appointments = len(daily_entries)
    
    # Pending payments
    pending_payments = sum(
        float(entry.total_amount - entry.amount_paid) 
        for entry in daily_entries 
        if entry.payment_status != 'paid'
    )
    
    # Inventory value
    inventory_items = db.query(InventoryItem).filter(
        and_(
            InventoryItem.branch_id == branch_id,
            InventoryItem.is_active == True
        )
    ).all()
    
    inventory_value = sum(
        float(item.current_stock * item.purchase_price) 
        for item in inventory_items
    )
    
    # Active services (unique test names performed in the month)
    active_services = len(set(entry.test_names for entry in daily_entries if entry.test_names))
    
    return BranchStatistics(
        branch_id=branch.id,
        branch_name=branch.name,
        total_staff=total_staff,
        total_patients=total_patients,
        monthly_revenue=monthly_revenue,
        total_appointments=total_appointments,
        pending_payments=pending_payments,
        inventory_value=inventory_value,
        active_services=active_services
    )

@router.get("/branches/cities")
def get_branch_cities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of cities with branches"""
    
    if current_user.role == 'super_admin':
        cities = db.query(Branch.city).distinct().filter(Branch.is_active == True).all()
    else:
        cities = db.query(Branch.city).filter(
            and_(
                Branch.id == current_user.branch_id,
                Branch.is_active == True
            )
        ).distinct().all()
    
    return [{"city": city[0]} for city in cities]

@router.get("/branches/states")
def get_branch_states(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of states with branches"""
    
    if current_user.role == 'super_admin':
        states = db.query(Branch.state).distinct().filter(Branch.is_active == True).all()
    else:
        states = db.query(Branch.state).filter(
            and_(
                Branch.id == current_user.branch_id,
                Branch.is_active == True
            )
        ).distinct().all()
    
    return [{"state": state[0]} for state in states]

@router.post("/branches/{branch_id}/assign-staff")
def assign_staff_to_branch(
    branch_id: int,
    user_id: int,
    current_user: User = Depends(auth_guard.require_role(['super_admin'])),
    db: Session = Depends(get_db)
):
    """Assign user to a branch (super admin only)"""
    
    # Check if branch exists
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user's branch
    user.branch_id = branch_id
    db.commit()
    
    # Log activity
    auth_guard.log_activity(
        db=db,
        user=current_user,
        action="assign",
        entity_type="user",
        entity_id=user_id,
        description=f"Assigned user {user.username} to branch {branch.name}"
    )
    
    return {"message": f"User {user.username} assigned to branch {branch.name} successfully"}
