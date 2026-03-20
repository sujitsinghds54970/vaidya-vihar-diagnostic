#!/usr/bin/env python3
"""
Script to create Bhabua branch and branch admin user using direct SQL
"""
import sqlite3
import bcrypt
from datetime import datetime

# Database path
DB_PATH = "./vaidya_vihar.db"

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_bhabua_branch_and_admin():
    """Create Bhabua branch and admin user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if Bhabua branch already exists
        cursor.execute("SELECT id, name FROM branches WHERE name = ?", ("Bhabua",))
        existing_branch = cursor.fetchone()
        
        if existing_branch:
            branch_id = existing_branch[0]
            print(f"✓ Bhabua branch already exists (ID: {branch_id})")
        else:
            # Create Bhabua branch
            cursor.execute("""
                INSERT INTO branches (name, address, phone, email, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                "Bhabua",
                "Main Road, Near District Hospital, Bhabua, Bihar - 821101",
                "9876543210",
                "bhabua@vaidyavihar.com",
                1,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            branch_id = cursor.lastrowid
            print(f"✓ Created Bhabua branch (ID: {branch_id})")
        
        # Check if branch admin already exists
        cursor.execute("SELECT id, username FROM users WHERE username = ?", ("bhabua_admin",))
        existing_admin = cursor.fetchone()
        
        if existing_admin:
            print(f"✓ Branch admin user already exists (Username: bhabua_admin)")
            admin_id = existing_admin[0]
        else:
            # Create branch admin user
            # Password: Bhabua@2026
            hashed_password = hash_password("Bhabua@2026")
            
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role, branch_id, 
                                 first_name, last_name, phone, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "bhabua_admin",
                "bhabua.admin@vaidyavihar.com",
                hashed_password,
                "branch_admin",
                branch_id,
                "Bhabua",
                "Administrator",
                "9876543210",
                1,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            admin_id = cursor.lastrowid
            print(f"✓ Created branch admin user (ID: {admin_id})")
        
        # Commit changes
        conn.commit()
        
        # Get branch details
        cursor.execute("SELECT * FROM branches WHERE id = ?", (branch_id,))
        branch = cursor.fetchone()
        
        # Print credentials
        print("\n" + "="*60)
        print("BHABUA BRANCH - LOGIN CREDENTIALS")
        print("="*60)
        print(f"\nBranch Details:")
        print(f"  Branch Name    : Bhabua")
        print(f"  Branch ID      : {branch_id}")
        print(f"  Address        : Main Road, Near District Hospital, Bhabua, Bihar - 821101")
        print(f"  Phone          : 9876543210")
        print(f"  Email          : bhabua@vaidyavihar.com")
        print(f"\nBranch Admin Login Credentials:")
        print(f"  Username       : bhabua_admin")
        print(f"  Password       : Bhabua@2026")
        print(f"  Role           : Branch Administrator")
        print(f"  Email          : bhabua.admin@vaidyavihar.com")
        print(f"\nAccess Level:")
        print(f"  ✓ Full access to Bhabua branch data")
        print(f"  ✓ Can manage patients, staff, inventory")
        print(f"  ✓ Can view reports and analytics")
        print(f"  ✓ Can create daily entries")
        print(f"  ✓ Can manage appointments and billing")
        print(f"  ✗ Cannot access other branches")
        print(f"  ✗ Cannot create new branches")
        print("\n" + "="*60)
        print("\n✓ Setup completed successfully!")
        print("\nNOTE: Please share these credentials securely with your")
        print("      Bhabua branch head. Advise them to change the password")
        print("      after first login for security.")
        print("\nLogin URL: http://your-domain.com/login")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        conn.rollback()
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("\n🏥 Vaidya Vihar Diagnostic - Branch Setup")
    print("Creating Bhabua branch and admin user...\n")
    
    success = create_bhabua_branch_and_admin()
    
    if success:
        exit(0)
    else:
        exit(1)
