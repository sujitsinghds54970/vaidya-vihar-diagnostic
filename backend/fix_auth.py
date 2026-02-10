#!/usr/bin/env python3
"""
Fix authentication system - Update admin password with proper bcrypt hash
"""

import bcrypt
import sqlite3
import os

def fix_admin_password():
    """Update admin password with bcrypt hash"""
    
    # Connect to database
    conn = sqlite3.connect('vaidya_vihar.db')
    cursor = conn.cursor()
    
    # New password
    new_password = "VaidyaVihar2024!"
    
    # Generate bcrypt hash
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')
    
    # Update admin password
    cursor.execute('''
    UPDATE users 
    SET password_hash = ? 
    WHERE username = 'admin'
    ''', (hashed_password,))
    
    if cursor.rowcount == 0:
        print("❌ Admin user not found!")
        return False
    
    conn.commit()
    conn.close()
    
    print(f"✅ Admin password updated successfully!")
    print(f"🔑 New credentials:")
    print(f"   Username: admin")
    print(f"   Password: {new_password}")
    
    return True

def verify_auth_system():
    """Verify the authentication system works"""
    
    # Test password verification
    test_password = "VaidyaVihar2024!"
    
    conn = sqlite3.connect('vaidya_vihar.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT password_hash FROM users WHERE username = "admin"')
    result = cursor.fetchone()
    
    if result:
        stored_hash = result[0]
        
        # Test bcrypt verification
        if bcrypt.checkpw(test_password.encode('utf-8'), stored_hash.encode('utf-8')):
            print("✅ Password verification test passed!")
            return True
        else:
            print("❌ Password verification failed!")
            return False
    else:
        print("❌ Admin user not found!")
        return False

if __name__ == "__main__":
    print("🔧 Fixing VaidyaVihar Authentication System")
    print("=" * 50)
    
    # Fix admin password
    if fix_admin_password():
        # Verify the fix
        if verify_auth_system():
            print("\n🎉 Authentication system fixed successfully!")
        else:
            print("\n❌ Authentication verification failed!")
    else:
        print("\n❌ Failed to fix authentication system!")
