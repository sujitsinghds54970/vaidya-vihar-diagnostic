#!/usr/bin/env python3
"""
VaidyaVihar Diagnostic ERP - Complete Database Initialization Script
This script creates all tables and initializes the database with default data
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from datetime import datetime, date
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import database configuration
from app.database import Base, engine, SessionLocal

# Import all models to ensure they're registered
from app.models import (
    Branch, User, Patient, DailyEntry, Staff, AttendanceRecord,
    SalaryRecord, InventoryItem, StockMovement, Appointment, Invoice,
    InvoiceItem, LabResult, ActivityLog, SystemSettings
)

# Import additional models
try:
    from app.models.lis import (
        TestOrder, TestOrderItem, Sample, TestResult,
        LabTestMaster, LISReportTemplate, GeneratedReport,
        QualityControl, InstrumentCalibration
    )
    logger.info("✓ LIS models imported successfully")
except Exception as e:
    logger.warning(f"⚠ LIS models import failed: {e}")

try:
    from app.models.payment import Payment, Refund
    logger.info("✓ Payment models imported successfully")
except Exception as e:
    logger.warning(f"⚠ Payment models import failed: {e}")

try:
    from app.models.accounting import ExpenseEntry, ExpenseCategory, Transaction, Account
    logger.info("✓ Accounting models imported successfully")
except Exception as e:
    logger.warning(f"⚠ Accounting models import failed: {e}")

try:
    from app.models.hr import LeaveRequest, EmployeeProfile, Attendance
    logger.info("✓ HR models imported successfully")
except Exception as e:
    logger.warning(f"⚠ HR models import failed: {e}")

try:
    from app.models.patient_portal import PatientAppointment, PatientPrescription, PatientPortalUser
    logger.info("✓ Patient Portal models imported successfully")
except Exception as e:
    logger.warning(f"⚠ Patient Portal models import failed: {e}")

try:
    from app.models.doctor import Doctor, DoctorBranch, ReportDistribution, DoctorNotification, DoctorSchedule
    logger.info("✓ Doctor models imported successfully")
except Exception as e:
    logger.warning(f"⚠ Doctor models import failed: {e}")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_tables():
    """Create all database tables"""
    logger.info("🔨 Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ All tables created successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        return False

def create_default_branch(db):
    """Create default branch"""
    logger.info("🏢 Creating default branch...")
    try:
        # Check if branch already exists
        existing_branch = db.query(Branch).filter(Branch.branch_code == "MAIN001").first()
        if existing_branch:
            logger.info("ℹ️  Default branch already exists")
            return existing_branch
        
        branch = Branch(
            name="Main Branch - Bhabua",
            location="Bhabua, Bihar",
            address="Near Civil Court, Bhabua",
            city="Bhabua",
            state="Bihar",
            pincode="821101",
            phone="+91-9876543210",
            email="bhabua@vaidyavihar.com",
            license_number="LIC-BHABUA-2024",
            branch_code="MAIN001",
            opening_hours="Mon-Sat: 8:00 AM - 8:00 PM, Sun: 9:00 AM - 2:00 PM",
            facilities="X-Ray, Ultrasound, ECG, Laboratory, Pharmacy",
            is_active=True
        )
        db.add(branch)
        db.commit()
        db.refresh(branch)
        logger.info(f"✅ Branch created: {branch.name} (ID: {branch.id})")
        return branch
    except Exception as e:
        logger.error(f"❌ Error creating branch: {e}")
        db.rollback()
        return None

def create_admin_user(db, branch_id):
    """Create super admin user"""
    logger.info("👤 Creating admin user...")
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            logger.info("ℹ️  Admin user already exists")
            return existing_admin
        
        hashed_password = pwd_context.hash("admin123")
        
        admin = User(
            username="admin",
            email="admin@vaidyavihar.com",
            hashed_password=hashed_password,
            first_name="System",
            last_name="Administrator",
            phone="+91-9876543210",
            role="super_admin",
            branch_id=branch_id,
            is_active=True
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        logger.info(f"✅ Admin user created: {admin.username} (ID: {admin.id})")
        return admin
    except Exception as e:
        logger.error(f"❌ Error creating admin user: {e}")
        db.rollback()
        return None

def create_sample_data(db, branch_id, admin_id):
    """Create sample data for testing"""
    logger.info("📊 Creating sample data...")
    try:
        # Create sample patient
        existing_patient = db.query(Patient).filter(Patient.patient_id == "PAT001").first()
        if not existing_patient:
            patient = Patient(
                patient_id="PAT001",
                branch_id=branch_id,
                first_name="Rajesh",
                last_name="Kumar",
                date_of_birth=datetime(1985, 5, 15),
                gender="Male",
                phone="+91-9876543211",
                email="rajesh.kumar@example.com",
                address="123 Main Street",
                city="Bhabua",
                state="Bihar",
                pincode="821101",
                emergency_contact="+91-9876543212",
                emergency_contact_name="Sunita Kumar",
                blood_group="O+",
                is_active=True
            )
            db.add(patient)
            logger.info("✅ Sample patient created")
        
        # Create sample inventory item
        existing_item = db.query(InventoryItem).filter(InventoryItem.item_code == "INV001").first()
        if not existing_item:
            inventory_item = InventoryItem(
                branch_id=branch_id,
                item_code="INV001",
                item_name="Blood Test Kit",
                category="consumable",
                unit="pieces",
                current_stock=100,
                minimum_stock=20,
                maximum_stock=500,
                reorder_level=30,
                purchase_price=50.00,
                selling_price=100.00,
                supplier="Medical Supplies Inc.",
                is_active=True
            )
            db.add(inventory_item)
            logger.info("✅ Sample inventory item created")
        
        # Create system settings
        settings = [
            ("company_name", "VaidyaVihar Diagnostic Center", "string", "Company Name"),
            ("currency", "INR", "string", "Default Currency"),
            ("tax_rate", "18", "integer", "Default Tax Rate (%)"),
            ("enable_sms", "false", "boolean", "Enable SMS Notifications"),
            ("enable_email", "false", "boolean", "Enable Email Notifications"),
        ]
        
        for key, value, type_, desc in settings:
            existing_setting = db.query(SystemSettings).filter(SystemSettings.setting_key == key).first()
            if not existing_setting:
                setting = SystemSettings(
                    setting_key=key,
                    setting_value=value,
                    setting_type=type_,
                    description=desc,
                    is_editable=True
                )
                db.add(setting)
        
        db.commit()
        logger.info("✅ Sample data created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error creating sample data: {e}")
        db.rollback()
        return False

def main():
    """Main initialization function"""
    print("=" * 70)
    print("🏥 VaidyaVihar Diagnostic ERP - Database Initialization")
    print("=" * 70)
    print()
    
    try:
        # Step 1: Create tables
        if not create_tables():
            logger.error("Failed to create tables. Exiting.")
            return False
        
        # Step 2: Create session
        db = SessionLocal()
        
        try:
            # Step 3: Create default branch
            branch = create_default_branch(db)
            if not branch:
                logger.error("Failed to create default branch. Exiting.")
                return False
            
            # Step 4: Create admin user
            admin = create_admin_user(db, branch.id)
            if not admin:
                logger.error("Failed to create admin user. Exiting.")
                return False
            
            # Step 5: Create sample data
            create_sample_data(db, branch.id, admin.id)
            
            print()
            print("=" * 70)
            print("🎉 Database initialization completed successfully!")
            print("=" * 70)
            print()
            print("📋 Default Credentials:")
            print(f"   Username: admin")
            print(f"   Password: admin123")
            print(f"   Branch: {branch.name}")
            print()
            print("🚀 Next Steps:")
            print("   1. Start the backend server:")
            print("      cd backend && uvicorn app.main:app --reload")
            print()
            print("   2. Start the frontend:")
            print("      cd frontend/vaidya-vihar-frontend && npm start")
            print()
            print("   3. Access the application:")
            print("      http://localhost:3000")
            print()
            print("=" * 70)
            
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Fatal error during initialization: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
