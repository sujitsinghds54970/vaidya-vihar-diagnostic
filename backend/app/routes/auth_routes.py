from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional

from app.utils.database import get_db
from app.utils.auth_system import (
    authenticate_user, create_user_token, update_last_login,
    auth_guard, TokenData, get_current_user
)
from app.models import User, Branch
from app.schemas.user import UserCreate, UserResponse, TokenResponse
from app.utils.auth_system import auth_guard

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """User login endpoint"""
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_user_token(user)
    
    # Update last login
    update_last_login(db, user)
    
    # Log activity
    auth_guard.log_activity(
        db=db, 
        user=user, 
        action="login", 
        entity_type="user", 
        entity_id=user.id, 
        description=f"User {user.username} logged in"
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "branch_id": user.branch_id
        }
    }


@router.post("/public-register", response_model=UserResponse)
def public_register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Public registration endpoint for patients, staff, and branch users"""
    
    # Check if username already exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    # Check if email already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Verify branch exists (if branch_id is provided and role is not patient)
    if user_data.branch_id and user_data.role != 'patient':
        branch = db.query(Branch).filter(Branch.id == user_data.branch_id).first()
        if not branch:
            raise HTTPException(
                status_code=404,
                detail="Branch not found"
            )
    
    # Set default role if not specified
    if not user_data.role:
        user_data.role = 'patient'
    
    # Validate role
    allowed_roles = ['patient', 'staff', 'branch_admin']
    if user_data.role not in allowed_roles:
        raise HTTPException(
            status_code=400,
            detail="Invalid role specified"
        )
    
    # For staff and branch_admin, require branch_id
    if user_data.role in ['staff', 'branch_admin'] and not user_data.branch_id:
        raise HTTPException(
            status_code=400,
            detail="Branch selection is required for staff and branch admin roles"
        )
    
    # Create new user
    hashed_password = auth_guard.hash_password(user_data.password)
    
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role,
        branch_id=user_data.branch_id,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Log activity
    auth_guard.log_activity(
        db=db, 
        user=db_user, 
        action="self_register", 
        entity_type="user", 
        entity_id=db_user.id, 
        description=f"User {db_user.username} self-registered as {db_user.role}"
    )
    
    return UserResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        first_name=db_user.first_name,
        last_name=db_user.last_name,
        role=db_user.role,
        branch_id=db_user.branch_id,
        is_active=db_user.is_active
    )

@router.post("/register", response_model=UserResponse)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_guard.require_role(['super_admin', 'branch_admin']))
):
    """Register new user (admin only)"""
    
    # Check if username already exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    # Check if email already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Verify branch exists (if branch_id is provided)
    if user_data.branch_id:
        branch = db.query(Branch).filter(Branch.id == user_data.branch_id).first()
        if not branch:
            raise HTTPException(
                status_code=404,
                detail="Branch not found"
            )
    
    # Create new user
    hashed_password = auth_guard.hash_password(user_data.password)
    
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role,
        branch_id=user_data.branch_id,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Log activity
    auth_guard.log_activity(
        db=db, 
        user=current_user, 
        action="create", 
        entity_type="user", 
        entity_id=db_user.id, 
        description=f"Created user {db_user.username}"
    )
    
    return UserResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        first_name=db_user.first_name,
        last_name=db_user.last_name,
        role=db_user.role,
        branch_id=db_user.branch_id,
        is_active=db_user.is_active
    )

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role,
        branch_id=current_user.branch_id,
        is_active=current_user.is_active
    )

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """User logout endpoint"""
    
    # Log activity
    auth_guard.log_activity(
        db=db, 
        user=current_user, 
        action="logout", 
        entity_type="user", 
        entity_id=current_user.id, 
        description=f"User {current_user.username} logged out"
    )
    
    return {"message": "Successfully logged out"}

@router.get("/branches")
def get_user_branches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get branches accessible to current user"""
    
    if current_user.role == 'super_admin':
        branches = db.query(Branch).filter(Branch.is_active == True).all()
    else:
        branches = db.query(Branch).filter(
            Branch.id == current_user.branch_id,
            Branch.is_active == True
        ).all()
    
    return [
        {
            "id": branch.id,
            "name": branch.name,
            "location": branch.location,
            "city": branch.city,
            "state": branch.state
        }
        for branch in branches
    ]

@router.post("/change-password")
def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    
    # Verify current password
    if not auth_guard.verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="Incorrect current password"
        )
    
    # Hash new password
    hashed_new_password = auth_guard.hash_password(new_password)
    current_user.hashed_password = hashed_new_password
    
    db.commit()
    
    # Log activity
    auth_guard.log_activity(
        db=db, 
        user=current_user, 
        action="password_change", 
        entity_type="user", 
        entity_id=current_user.id, 
        description=f"User {current_user.username} changed password"
    )
    
    return {"message": "Password changed successfully"}

@router.post("/refresh-token", response_model=TokenResponse)
def refresh_access_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Refresh access token"""
    
    access_token = create_user_token(current_user)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "role": current_user.role,
            "branch_id": current_user.branch_id
        }
    }

@router.get("/verify-token")
def verify_token_validity(current_user: User = Depends(get_current_user)):
    """Verify if current token is valid"""
    return {
        "valid": True,
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "role": current_user.role,
            "branch_id": current_user.branch_id
        }
    }
