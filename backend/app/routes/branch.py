from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.branch import Branch
from app.schemas.branch import BranchResponse
from app.utils.database import get_db

router = APIRouter()

@router.get("/branches/", response_model=list[BranchResponse])
def get_branches(db: Session = Depends(get_db)):
    return db.query(Branch).all()