#!/usr/bin/env python3
"""
Script to create Bhabua branch and branch admin user
"""
import sys
import os
from datetime import datetime

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Branch, User
from app.utils.auth_system import AuthGuard
from app.utils.database import Base

# Database configuration
DATABASE_URL = "sqlite:///./vaidya_vihar.db"

# Create engine and session
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_bhabua_branch_and_admin():
    """Create Bhabua branch and admin user"""
    db = SessionLocal()
    auth_guard = AuthGuard()
    
    try:
        # Check if Bhabua branch already exists
        existing_branch = db.query(Branch).filter(Branch.name == "Bhabua").first()
        
        if existing_branch:
            print(f"✓ Bhabua branch already exists (ID: {existing_branch.id})")
            branch = existing_branch
        else:
            # Create Bhabua branch (using actual database schema)
            branch = Branch(
                name="Bhabua",
                address="Main Road, Near District Hospital, Bhabua, Bihar - 821101",
                phone="9876543210",
                email="bhabua@vaidyavihar.com",
                is_active=True
            )
            
            db.add(branch)
            db.commit()
            db.refresh(branch)
            print(f"✓ Created Bhabua branch (ID: {branch.id})")
        
        # Check if branch admin already exists
        existing_admin = db.query(User).filter(User.username == "bhabua_admin").first()
        
        if existing_admin:
            print(f"✓ Branch admin user already exists (Username: {existing_admin.username})")
            admin_user = existing_admin
        else:
            # Create branch admin user
            # Password: Bhabua@2026
            hashed_password = auth_guard.hash_password("Bhabua@2026")
            
            admin_user = User(
                username="bhabua_admin",
                email="bhabua.admin@vaidyavihar.com",
                hashed_password=hashed_password,
                role="branch_admin",
                branch_id=branch.id,
                first_name="Bhabua",
                last_name="Administrator",
                phone="9876543210",
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print(f"✓ Created branch admin user (Username: {admin_user.username})")
        
        # Print credentials
        print("\n" + "="*60)
        print("BHABUA BRANCH - LOGIN CREDENTIALS")
        print("="*60)
        print(f"\nBranch Details:")
        print(f"  Branch Name    : {branch.name}")
        print(f"  Branch ID      : {branch.id}")
        print(f"  Address        : {branch.address}")
        print(f"  Phone          : {branch.phone}")
        print(f"  Email          : {branch.email}")
        print(f"\nBranch Admin Login Credentials:")
        print(f"  Username       : bhabua_admin")
        print(f"  Password       : Bhabua@2026")
        print(f"  Role           : Branch Administrator")
        print(f"  Email          : bhabua.admin@vaidyavihar.com")
        print(f"\nAccess Level:")
        print(f"  - Full access to Bhabua branch data")
        print(f"  - Can manage patients, staff, inventory")
        print(f"  - Can view reports and analytics")
        print(f"  - Can create daily entries")
        print(f"  - Cannot access other branches")
        print(f"  - Cannot create new branches")
        print("\n" + "="*60)
        print("\n✓ Setup completed successfully!")
        print("\nNOTE: Please share these credentials securely with your")
        print("      Bhabua branch head. Advise them to change the password")
        print("      after first login for security.")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("\n🏥 Vaidya Vihar Diagnostic - Branch Setup")
    print("Creating Bhabua branch and admin user...\n")
    
    success = create_bhabua_branch_and_admin()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
