from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Optional, List
import bcrypt
import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.utils.database import get_db
from app.models import User, Branch, ActivityLog

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-for-vaidya-vihar-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Rate Limiting
limiter = Limiter(key_func=get_remote_address)

# Security
security = HTTPBearer()

class TokenData:
    def __init__(self, username: str = None, branch_id: int = None, role: str = None):
        self.username = username
        self.branch_id = branch_id
        self.role = role

class AuthGuard:
    def __init__(self, allowed_roles: Optional[List[str]] = None):
        self.allowed_roles = allowed_roles or []
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
        """Verify JWT token and return user data"""
        try:
            payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            branch_id: int = payload.get("branch_id")
            role: str = payload.get("role")
            
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return TokenData(username=username, branch_id=branch_id, role=role)
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def get_current_user(self, token_data: TokenData = Depends(verify_token), db: Session = Depends(get_db)) -> User:
        """Get current authenticated user from database"""
        user = db.query(User).filter(User.username == token_data.username).first()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
    
    def require_role(self, allowed_roles: List[str]):
        """Decorator to require specific roles"""
        def role_checker(current_user: User = Depends(get_current_user)):
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            return current_user
        return role_checker
    
    def require_branch_access(self, current_user: User = Depends(get_current_user)):
        """Ensure user has access to their assigned branch"""
        if current_user.branch_id is None and current_user.role != 'super_admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Branch access required"
            )
        return current_user
    
    def log_activity(self, db: Session, user: User, action: str, entity_type: str, entity_id: int = None, description: str = ""):
        """Log user activity for audit trail"""
        activity = ActivityLog(
            user_id=user.id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            timestamp=datetime.utcnow()
        )
        db.add(activity)
        db.commit()

# Authentication functions
def authenticate_user(db: Session, username: str, password: str):
    """Authenticate user with username and password"""
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        return False
    
    if not AuthGuard().verify_password(password, user.hashed_password):
        return False
    
    if not user.is_active:
        return False
    
    return user

def create_user_token(user: User):
    """Create access token for user"""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    token_data = {
        "sub": user.username,
        "branch_id": user.branch_id,
        "role": user.role,
        "user_id": user.id
    }
    
    return AuthGuard().create_access_token(data=token_data, expires_delta=access_token_expires)

def update_last_login(db: Session, user: User):
    """Update user's last login timestamp"""
    user.last_login = datetime.utcnow()
    db.commit()

# FastAPI dependencies
auth_guard = AuthGuard()
get_current_user = auth_guard.get_current_user
verify_token = auth_guard.verify_token

# Role-based dependencies
require_super_admin = auth_guard.require_role(['super_admin'])
require_branch_admin = auth_guard.require_role(['super_admin', 'branch_admin'])
require_staff = auth_guard.require_role(['super_admin', 'branch_admin', 'staff'])
require_patient = auth_guard.require_role(['patient'])
require_all_users = auth_guard.require_role(['super_admin', 'branch_admin', 'staff', 'patient'])

# Branch access dependency
require_branch_access = auth_guard.require_branch_access
