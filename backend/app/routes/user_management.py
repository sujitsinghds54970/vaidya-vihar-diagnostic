from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.database import get_db
from app.utils.auth_guard import get_current_user

router = APIRouter()

@router.post("/users/")
def create_user(
    username: str,
    password: str,
    role: str,
    branch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create users")

    hashed_password = password + "_hashed"  # Replace with real hashing
    user = User(
        username=username,
        hashed_password=hashed_password,
        role=role,
        branch_id=branch_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "branch_id": user.branch_id
    }
