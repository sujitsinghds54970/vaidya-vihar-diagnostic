#!/usr/bin/env python3
"""
Complete System Setup Script for VaidyaVihar Diagnostic ERP
This script initializes the database, creates branches, and sets up users
"""

import sys
import os
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import bcrypt

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.database import Base, get_db
from app.models import Branch, User, SystemSettings

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://vaidya_user:vaidya_password_123@localhost:5432/vaidya_vihar_db")

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def setup_database():
    """Create all database tables"""
    print("🔧 Setting up database...")
    
    try:
        engine = create_engine(DATABASE_URL)
        
        # Drop all existing tables (fresh start)
        print("  ⚠️  Dropping existing tables...")
        Base.metadata.drop_all(bind=engine)
        
        # Create all tables
        print("  ✅ Creating new tables...")
        Base.metadata.create_all(bind=engine)
        
        print("  ✅ Database tables created successfully!")
        return engine
    except Exception as e:
        print(f"  ❌ Error setting up database: {e}")
        sys.exit(1)

def create_branches(session):
    """Create branches including Mundeshwari Bhabua branch"""
    print("\n🏢 Creating branches...")
    
    branches_data = [
        {
            "name": "Mundeshwari Bhabua",
            "location": "Bhabua, Bihar",
            "address": "Main Road, Near District Hospital, Bhabua",
            "city": "Bhabua",
            "state": "Bihar",
            "pincode": "821101",
            "phone": "9876543210",
            "email": "bhabua@vaidyavihar.com",
            "license_number": "VV-BH-2024-001",
            "branch_code": "VVBH001"
        },
        {
            "name": "VaidyaVihar Head Office",
            "location": "Patna, Bihar",
            "address": "Exhibition Road, Patna",
            "city": "Patna",
            "state": "Bihar",
            "pincode": "800001",
            "phone": "9876543211",
            "email": "headoffice@vaidyavihar.com",
            "license_number": "VV-PT-2024-001",
            "branch_code": "VVHO001"
        }
    ]
    
    created_branches = []
    for branch_data in branches_data:
        # Check if branch already exists
        existing = session.query(Branch).filter(Branch.name == branch_data["name"]).first()
        if existing:
            print(f"  ⚠️  Branch '{branch_data['name']}' already exists, skipping...")
            created_branches.append(existing)
            continue
        
        branch = Branch(**branch_data)
        session.add(branch)
        session.flush()
        created_branches.append(branch)
        print(f"  ✅ Created branch: {branch_data['name']} (ID: {branch.id})")
    
    session.commit()
    return created_branches

def create_users(session, branches):
    """Create users including Mundeshwari Bhabua branch admin"""
    print("\n👥 Creating users...")
    
    # Find Mundeshwari Bhabua branch
    bhabua_branch = next((b for b in branches if b.name == "Mundeshwari Bhabua"), None)
    head_office = next((b for b in branches if b.name == "VaidyaVihar Head Office"), None)
    
    users_data = [
        {
            "username": "superadmin",
            "email": "admin@vaidyavihar.com",
            "password": "Admin@123",
            "role": "super_admin",
            "branch_id": head_office.id if head_office else None,
            "first_name": "Super",
            "last_name": "Admin",
            "phone": "9999999999"
        },
        {
            "username": "mundeshwaribhabua",
            "email": "bhabua@vaidyavihar.com",
            "password": "#Mundeshwaribhabua54970",
            "role": "branch_admin",
            "branch_id": bhabua_branch.id if bhabua_branch else None,
            "first_name": "Mundeshwari",
            "last_name": "Bhabua",
            "phone": "9876543210"
        },
        {
            "username": "bhabua_staff",
            "email": "staff.bhabua@vaidyavihar.com",
            "password": "Staff@Bhabua123",
            "role": "staff",
            "branch_id": bhabua_branch.id if bhabua_branch else None,
            "first_name": "Staff",
            "last_name": "Bhabua",
            "phone": "9876543211"
        }
    ]
    
    created_users = []
    for user_data in users_data:
        # Check if user already exists
        existing = session.query(User).filter(User.username == user_data["username"]).first()
        if existing:
            # Update password for existing user
            existing.hashed_password = hash_password(user_data["password"])
            existing.branch_id = user_data["branch_id"]
            existing.role = user_data["role"]
            session.commit()
            print(f"  ⚠️  User '{user_data['username']}' already exists, updated password and branch")
            created_users.append(existing)
            continue
        
        password = user_data.pop("password")
        user = User(
            **user_data,
            hashed_password=hash_password(password),
            is_active=True
        )
        session.add(user)
        session.flush()
        created_users.append(user)
        print(f"  ✅ Created user: {user_data['username']} ({user_data['role']}) - Branch: {user.branch_id}")
    
    session.commit()
    return created_users

def create_system_settings(session):
    """Create default system settings"""
    print("\n⚙️  Creating system settings...")
    
    settings_data = [
        {
            "setting_key": "app_name",
            "setting_value": "VaidyaVihar Diagnostic ERP",
            "setting_type": "string",
            "description": "Application name"
        },
        {
            "setting_key": "app_version",
            "setting_value": "2.0.0",
            "setting_type": "string",
            "description": "Application version"
        },
        {
            "setting_key": "currency",
            "setting_value": "INR",
            "setting_type": "string",
            "description": "Default currency"
        },
        {
            "setting_key": "timezone",
            "setting_value": "Asia/Kolkata",
            "setting_type": "string",
            "description": "Default timezone"
        },
        {
            "setting_key": "date_format",
            "setting_value": "DD/MM/YYYY",
            "setting_type": "string",
            "description": "Default date format"
        },
        {
            "setting_key": "enable_sms",
            "setting_value": "false",
            "setting_type": "boolean",
            "description": "Enable SMS notifications"
        },
        {
            "setting_key": "enable_email",
            "setting_value": "false",
            "setting_type": "boolean",
            "description": "Enable email notifications"
        },
        {
            "setting_key": "enable_whatsapp",
            "setting_value": "false",
            "setting_type": "boolean",
            "description": "Enable WhatsApp notifications"
        }
    ]
    
    for setting_data in settings_data:
        existing = session.query(SystemSettings).filter(
            SystemSettings.setting_key == setting_data["setting_key"]
        ).first()
        
        if existing:
            print(f"  ⚠️  Setting '{setting_data['setting_key']}' already exists, skipping...")
            continue
        
        setting = SystemSettings(**setting_data)
        session.add(setting)
        print(f"  ✅ Created setting: {setting_data['setting_key']}")
    
    session.commit()

def print_credentials(branches, users):
    """Print all credentials for reference"""
    print("\n" + "="*80)
    print("🎉 SYSTEM SETUP COMPLETED SUCCESSFULLY!")
    print("="*80)
    
    print("\n📋 BRANCH INFORMATION:")
    print("-" * 80)
    for branch in branches:
        print(f"\nBranch: {branch.name}")
        print(f"  ID: {branch.id}")
        print(f"  Code: {branch.branch_code}")
        print(f"  Location: {branch.location}")
        print(f"  Phone: {branch.phone}")
        print(f"  Email: {branch.email}")
    
    print("\n" + "="*80)
    print("🔐 USER CREDENTIALS:")
    print("="*80)
    
    credentials = [
        {
            "username": "superadmin",
            "password": "Admin@123",
            "role": "Super Admin",
            "access": "Full system access, all branches"
        },
        {
            "username": "mundeshwaribhabua",
            "password": "#Mundeshwaribhabua54970",
            "role": "Branch Admin (Mundeshwari Bhabua)",
            "access": "Full access to Bhabua branch features"
        },
        {
            "username": "bhabua_staff",
            "password": "Staff@Bhabua123",
            "role": "Staff (Mundeshwari Bhabua)",
            "access": "Staff-level access to Bhabua branch"
        }
    ]
    
    for cred in credentials:
        print(f"\n{cred['role']}:")
        print(f"  Username: {cred['username']}")
        print(f"  Password: {cred['password']}")
        print(f"  Access: {cred['access']}")
    
    print("\n" + "="*80)
    print("🌐 ACCESS INFORMATION:")
    print("="*80)
    print("\n  Backend API: http://localhost:8000")
    print("  API Documentation: http://localhost:8000/docs")
    print("  Frontend: http://localhost:3000")
    print("  Database: PostgreSQL on localhost:5432")
    print("\n" + "="*80)

def main():
    """Main setup function"""
    print("\n" + "="*80)
    print("🚀 VaidyaVihar Diagnostic ERP - Complete System Setup")
    print("="*80)
    
    try:
        # Setup database
        engine = setup_database()
        
        # Create session
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        # Create branches
        branches = create_branches(session)
        
        # Create users
        users = create_users(session, branches)
        
        # Create system settings
        create_system_settings(session)
        
        # Print credentials
        print_credentials(branches, users)
        
        session.close()
        
        print("\n✅ Setup completed successfully!")
        print("💡 You can now start the application using: docker-compose up -d")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
