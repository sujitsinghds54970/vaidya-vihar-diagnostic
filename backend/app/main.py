from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from datetime import datetime


# Import your existing routers and components
from app.routes.auth_routes import router as auth_router
from app.routes.patient_management import router as patient_router
from app.routes.staff_management import router as staff_router
from app.routes.inventory_management import router as inventory_router
from app.routes.export_routes import router as export_router
from app.routes.analytics import router as analytics_router
from app.routes.daily_entry import router as daily_entry_router

# New Feature Routers
from app.routes.payment_routes import router as payment_router
from app.routes.accounting_routes import router as accounting_router
from app.routes.hr_routes import router as hr_router
from app.routes.lis_routes import router as lis_router
from app.routes.patient_portal_routes import router as patient_portal_router
from app.routes.doctor_portal_routes import router as doctor_portal_router

# Create FastAPI app
app = FastAPI(
    title="VaidyaVihar Diagnostic ERP API",
    description="Comprehensive ERP system for diagnostic centers",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers - Existing
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(patient_router, prefix="/api/patients", tags=["Patients"])
app.include_router(staff_router, prefix="/api/staff", tags=["Staff"])
app.include_router(inventory_router, prefix="/api/inventory", tags=["Inventory"])
app.include_router(export_router, prefix="/api/export", tags=["Export"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(daily_entry_router, prefix="/api/daily-entry", tags=["Daily Entry"])

# New Feature Routers
app.include_router(payment_router, prefix="/api/payments", tags=["Payments"])
app.include_router(accounting_router, prefix="/api/accounting", tags=["Accounting"])
app.include_router(hr_router, prefix="/api/hr", tags=["HR & Payroll"])
app.include_router(lis_router, prefix="/api/lis", tags=["LIS"])
app.include_router(patient_portal_router, prefix="/api/patient-portal", tags=["Patient Portal"])
app.include_router(doctor_portal_router, prefix="/api/doctor-portal", tags=["Doctor Portal"])

@app.get("/")
async def root():
    return {"message": "VaidyaVihar Diagnostic ERP API", "version": "2.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "VaidyaVihar Diagnostic ERP API"
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
