#!/usr/bin/env python3
"""
Script to update Bhabua branch credentials with custom details
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

def update_bhabua_credentials():
    """Update Bhabua branch and admin credentials"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Update Bhabua branch details
        cursor.execute("""
            UPDATE branches 
            SET address = ?, phone = ?, email = ?
            WHERE name = 'Bhabua'
        """, (
            "Astitva Complex, opposite sadar hospital, Bhabua (Kaimur)-821101, Bihar",
            "6204422093",
            "mundeshwaribhabua@vaidyavihar.com"
        ))
        
        print("✓ Updated Bhabua branch details")
        
        # Delete old admin user
        cursor.execute("DELETE FROM users WHERE username = 'bhabua_admin'")
        print("✓ Removed old admin user")
        
        # Get branch ID
        cursor.execute("SELECT id FROM branches WHERE name = 'Bhabua'")
        branch_result = cursor.fetchone()
        
        if not branch_result:
            print("✗ Bhabua branch not found!")
            return False
            
        branch_id = branch_result[0]
        
        # Create new admin user with custom credentials
        hashed_password = hash_password("#MUNDESHWARI54970")
        
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, branch_id, 
                             first_name, last_name, phone, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "mundeshwaribhabua",
            "mundeshwaribhabua@vaidyavihar.com",
            hashed_password,
            "branch_admin",
            branch_id,
            "Mundeshwari",
            "Bhabua",
            "6204422093",
            1,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        admin_id = cursor.lastrowid
        print(f"✓ Created new admin user (ID: {admin_id})")
        
        # Commit changes
        conn.commit()
        
        # Print credentials
        print("\n" + "="*60)
        print("BHABUA BRANCH - UPDATED CREDENTIALS")
        print("="*60)
        print(f"\nBranch Details:")
        print(f"  Branch Name    : Bhabua")
        print(f"  Branch ID      : {branch_id}")
        print(f"  Address        : Astitva Complex, opposite sadar hospital")
        print(f"                   Bhabua (Kaimur)-821101, Bihar")
        print(f"  Phone          : 6204422093")
        print(f"  Email          : mundeshwaribhabua@vaidyavihar.com")
        print(f"\nBranch Admin Login Credentials:")
        print(f"  Username       : mundeshwaribhabua")
        print(f"  Password       : #MUNDESHWARI54970")
        print(f"  Role           : Branch Administrator")
        print(f"  Email          : mundeshwaribhabua@vaidyavihar.com")
        print(f"  Phone          : 6204422093")
        print("\n" + "="*60)
        print("\n✓ Credentials updated successfully!")
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
    print("\n🏥 Vaidya Vihar Diagnostic - Update Bhabua Credentials")
    print("Updating credentials...\n")
    
    success = update_bhabua_credentials()
    
    if success:
        exit(0)
    else:
        exit(1)
