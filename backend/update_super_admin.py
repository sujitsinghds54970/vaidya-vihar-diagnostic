#!/usr/bin/env python3
"""
Update Super Admin Credentials
Changes admin username to 'sujiterp' and password to '#Sujitvaidyavihar54970'
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    # Bcrypt has a 72 byte limit, truncate if necessary
    password_bytes = password.encode('utf-8')[:72]
    return pwd_context.hash(password_bytes.decode('utf-8'))

def update_super_admin_local():
    """Update super admin in local SQLite database"""
    print("🔄 Updating Super Admin in LOCAL database...")
    
    db_path = backend_dir / "vaidya_vihar.db"
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return False
    
    engine = create_engine(f"sqlite:///{db_path}")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Hash the new password
        hashed_password = hash_password("#Sujitvaidyavihar54970")
        
        # Update the admin user
        result = session.execute(
            text("""
                UPDATE users 
                SET username = :new_username,
                    hashed_password = :new_password,
                    email = :new_email,
                    full_name = :new_name
                WHERE role = 'super_admin'
            """),
            {
                "new_username": "sujiterp",
                "new_password": hashed_password,
                "new_email": "sujit@vaidyavihar.com",
                "new_name": "Sujit Singh - Super Admin"
            }
        )
        
        session.commit()
        
        if result.rowcount > 0:
            print("✅ Super Admin credentials updated successfully in LOCAL database!")
            print("\n📋 New Credentials:")
            print("   Username: sujiterp")
            print("   Password: #Sujitvaidyavihar54970")
            print("   Email: sujit@vaidyavihar.com")
            return True
        else:
            print("❌ No super admin user found to update")
            return False
            
    except Exception as e:
        print(f"❌ Error updating super admin: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def generate_production_sql():
    """Generate SQL for production database update"""
    print("\n🔄 Generating SQL for PRODUCTION database...")
    
    hashed_password = hash_password("#Sujitvaidyavihar54970")
    
    sql = f"""
-- Update Super Admin Credentials in Production
UPDATE users 
SET username = 'sujiterp',
    hashed_password = '{hashed_password}',
    email = 'sujit@vaidyavihar.com',
    full_name = 'Sujit Singh - Super Admin'
WHERE role = 'super_admin';
"""
    
    sql_file = backend_dir / "update_super_admin.sql"
    with open(sql_file, 'w') as f:
        f.write(sql)
    
    print(f"✅ SQL file created: {sql_file}")
    print("\n📝 To apply to production, run:")
    print(f"   docker exec vaidya_vihar_db psql -U vaidya_user -d vaidya_vihar_db -f /path/to/update_super_admin.sql")
    
    return sql

if __name__ == "__main__":
    print("=" * 60)
    print("🔐 UPDATING SUPER ADMIN CREDENTIALS")
    print("=" * 60)
    
    # Update local database
    local_success = update_super_admin_local()
    
    # Generate production SQL
    prod_sql = generate_production_sql()
    
    print("\n" + "=" * 60)
    if local_success:
        print("✅ LOCAL DATABASE UPDATED SUCCESSFULLY!")
    print("📄 PRODUCTION SQL GENERATED")
    print("=" * 60)
