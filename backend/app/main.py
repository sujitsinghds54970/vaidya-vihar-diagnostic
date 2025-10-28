from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt
from datetime import datetime, timedelta
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import FastAPI
from app.routes.branch import router as branch_router
from app.routes.calendar_day import router as calendar_day_router

app = FastAPI(
    title="VaidyaVihar Diagnostic ERP",
    description="Backend API for managing branches, calendar days, patient entries, and more.",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
users_db = {
    "admin": {
        "username": "admin",
        "password": "admin123"
    }
}
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt.encode({
        "sub": user["username"],
        "exp": datetime.utcnow() + timedelta(hours=1)
    }, SECRET_KEY, algorithm=ALGORITHM)
    from fastapi import Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except Exception:
        raise HTTPException(status_code=403, detail="Invalid or expired token")
    @app.get("/patients")
    def get_patients(user: str = Depends(verify_token)):
     return patients

@app.get("/lab-results")
def get_lab_results(user: str = Depends(verify_token)):
    return lab_results

@app.get("/invoices")
def get_invoices(user: str = Depends(verify_token)):
    return invoices

    return {"access_token": token, "token_type": "bearer"}
patients = [
    {
        "id": 1,
        "name": "Amit Verma",
        "age": 34,
        "gender": "Male",
        "phone": "9876543210",
        "email": "amit@example.com"
    },
    {
        "id": 2,
        "name": "Neha Joshi",
        "age": 29,
        "gender": "Female",
        "phone": "9123456780",
        "email": "neha@example.com"
    }
]
@app.get("/patients")
def get_patients():
    return patients
lab_results = [
    {
        "id": 1,
        "patient_name": "Amit Verma",
        "test": "CBC",
        "result": "Normal",
        "date": "2025-09-08"
    },
    {
        "id": 2,
        "patient_name": "Neha Joshi",
        "test": "Blood Sugar",
        "result": "High",
        "date": "2025-09-07"
    }
]
@app.get("/lab-results")
def get_lab_results():
    return lab_results
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.include_router(branch_router, prefix="/api", tags=["Branch"])
app.include_router(calendar_day_router, prefix="/api", tags=["CalendarDay"])
from app.routes.expense_entry import router as expense_entry_router

app.include_router(expense_entry_router, prefix="/api", tags=["ExpenseEntry"])
from app.routes.note_entry import router as note_entry_router

app.include_router(note_entry_router, prefix="/api", tags=["NoteEntry"])
from app.routes.daily_report import router as daily_report_router
app.include_router(daily_report_router, prefix="/api", tags=["DailyReport"])
from app.routes.test_entry import router as test_entry_router
app.include_router(test_entry_router, prefix="/api", tags=["TestEntry"])
from app.routes.billing_entry import router as billing_entry_router
app.include_router(billing_entry_router, prefix="/api", tags=["BillingEntry"])
from app.routes.auth import router as auth_router
app.include_router(auth_router, prefix="/api", tags=["Auth"])
from app.routes.inventory_item import router as inventory_item_router
app.include_router(inventory_item_router, prefix="/api", tags=["Inventory"])
from app.routes.analytics import router as analytics_router
app.include_router(analytics_router, prefix="/api", tags=["Analytics"])
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from app.routes.activity_log import router as activity_log_router
app.include_router(activity_log_router, prefix="/api", tags=["ActivityLog"])
from app.routes.appointment import router as appointment_router
app.include_router(appointment_router, prefix="/api", tags=["Appointment"])
from app.routes.mobile_api import router as mobile_api_router
app.include_router(mobile_api_router, prefix="/api", tags=["MobileAPI"])
from app.routes.analytics import router as analytics_router
app.include_router(analytics_router, prefix="/api", tags=["Analytics"])
from app.routes.invoice import router as invoice_router
app.include_router(invoice_router, prefix="/api", tags=["Invoice"])
from app.routes.lab_test import router as lab_test_router
app.include_router(lab_test_router, prefix="/api", tags=["LabTest"])
from app.routes.lab_test import router as lab_test_router
app.include_router(lab_test_router, prefix="/api", tags=["LabTest"])
from app.routes.dashboard import router as dashboard_router
app.include_router(dashboard_router, prefix="/api", tags=["Dashboard"])
from app.routes.user_management import router as user_router
app.include_router(user_router, prefix="/api", tags=["UserManagement"])
from app.routes.data_export import router as export_router
app.include_router(export_router, prefix="/api", tags=["DataExport"])
from app.routes.mobile_dashboard import router as mobile_dash_router
app.include_router(mobile_dash_router, prefix="/api", tags=["MobileDashboard"])
from app.routes import invoice
app.include_router(invoice.router)
from app.routes import lab_result
app.include_router(lab_result.router)
from app.routes import appointment
from app.routes import admin
app.include_router(admin.router)
from app.routes import analytics
app.include_router(analytics.router)
from app.routes import export
app.include_router(export.router)
from fastapi import FastAPI
from app.routes import login

app = FastAPI()
app.include_router(login.router)
