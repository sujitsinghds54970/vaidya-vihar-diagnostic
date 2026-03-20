#!/usr/bin/env python3
"""
Final Bhabua Branch Setup Script
Creates branch and admin user with proper credentials
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import bcrypt
from datetime import datetime

# Import models
from app.models.branch import Branch
from app.models import User

# Database connection
DATABASE_URL = "postgresql://vaidya_user:vaidya_password@db:5432/vaidya_vihar_db"

def setup_bhabua_branch():
    """Setup Bhabua branch and admin user"""
    
    print("🔧 Setting up Bhabua Branch...")
    
    try:
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # 1. Create/Update Bhabua Branch
        print("📍 Creating Bhabua branch...")
        branch = session.query(Branch).filter_by(name="Bhabua").first()
        
        if not branch:
            branch = Branch(
                name="Bhabua",
                address="Astitva Complex, opposite sadar hospital, Bhabua (Kaimur)-821101, Bihar",
                phone="6204422093",
                email="maamundeshwaribhabua@gmail.com",
                is_active=True,
                created_at=datetime.now()
            )
            session.add(branch)
            session.commit()
            print("✓ Bhabua branch created!")
        else:
            branch.address = "Astitva Complex, opposite sadar hospital, Bhabua (Kaimur)-821101, Bihar"
            branch.phone = "6204422093"
            branch.email = "maamundeshwaribhabua@gmail.com"
            branch.is_active = True
            session.commit()
            print("✓ Bhabua branch updated!")
        
        # 2. Create/Update Bhabua Admin User
        print("👤 Creating Bhabua admin user...")
        
        # Hash password
        password = "#Mundeshwaribhabua54970"
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Check if user exists
        user = session.query(User).filter_by(username="mundeshwaribhabua").first()
        
        if not user:
            user = User(
                username="mundeshwaribhabua",
                password_hash=password_hash,
                email="maamundeshwaribhabua@gmail.com",
                first_name="Bhabua",
                last_name="Administrator",
                role="branch_admin",
                branch_id=branch.id,
                is_active=True,
                created_at=datetime.now()
            )
            session.add(user)
            session.commit()
            print("✓ Bhabua admin user created!")
        else:
            user.password_hash = password_hash
            user.email = "maamundeshwaribhabua@gmail.com"
            user.branch_id = branch.id
            user.is_active = True
            session.commit()
            print("✓ Bhabua admin user updated!")
        
        # 3. Verify
        print("\n📊 Verification:")
        print(f"   Branch ID: {branch.id}")
        print(f"   Branch Name: {branch.name}")
        print(f"   User ID: {user.id}")
        print(f"   Username: {user.username}")
        print(f"   Role: {user.role}")
        
        session.close()
        print("\n✅ Bhabua branch setup complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = setup_bhabua_branch()
    sys.exit(0 if success else 1)
