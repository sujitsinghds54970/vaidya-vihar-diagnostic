from fastapi import APIRouter, Depends
from app.utils.auth_guard import require_role

router = APIRouter()

@router.get("/admin-only")
def admin_data(user=Depends(require_role("admin"))):
    return {"message": "Welcome Admin"}