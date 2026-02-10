#!/usr/bin/env python3
"""
VaidyaVihar Diagnostic ERP - Database Initialization Script
This script sets up the initial database schema and creates default admin user
"""

import sqlite3
import hashlib
import os
from datetime import datetime

def init_database():
    """Initialize the database with required tables"""
    
    # Create database connection
    conn = sqlite3.connect('vaidya_vihar.db')
    cursor = conn.cursor()
    
    print("🏥 Initializing VaidyaVihar Diagnostic ERP Database...")
    
    # Create tables
    
    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        phone VARCHAR(20),
        role VARCHAR(20) DEFAULT 'user',
        branch_id INTEGER,
        is_active BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (branch_id) REFERENCES branches (id)
    )
    ''')
    
    # Branches table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS branches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        address TEXT,
        phone VARCHAR(20),
        email VARCHAR(100),
        is_active BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Patients table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        date_of_birth DATE,
        gender VARCHAR(10),
        phone VARCHAR(20),
        email VARCHAR(100),
        address TEXT,
        emergency_contact VARCHAR(100),
        blood_group VARCHAR(10),
        medical_history TEXT,
        branch_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (branch_id) REFERENCES branches (id)
    )
    ''')
    
    # Daily Entries table (Core feature)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        doctor_id INTEGER,
        visit_date DATE NOT NULL,
        consultation_fee DECIMAL(10,2) DEFAULT 0,
        test_fee DECIMAL(10,2) DEFAULT 0,
        total_amount DECIMAL(10,2) DEFAULT 0,
        test_type VARCHAR(100),
        notes TEXT,
        payment_status VARCHAR(20) DEFAULT 'paid',
        branch_id INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients (id),
        FOREIGN KEY (doctor_id) REFERENCES users (id),
        FOREIGN KEY (branch_id) REFERENCES branches (id)
    )
    ''')
    
    # Staff table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS staff (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        position VARCHAR(50),
        department VARCHAR(50),
        salary DECIMAL(10,2),
        hire_date DATE,
        is_active BOOLEAN DEFAULT 1,
        branch_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (branch_id) REFERENCES branches (id)
    )
    ''')
    
    # Inventory items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        category VARCHAR(50),
        quantity INTEGER DEFAULT 0,
        unit VARCHAR(20),
        min_quantity INTEGER DEFAULT 0,
        unit_price DECIMAL(10,2),
        supplier VARCHAR(100),
        expiry_date DATE,
        branch_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (branch_id) REFERENCES branches (id)
    )
    ''')
    
    # Appointments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        doctor_id INTEGER,
        appointment_date DATE NOT NULL,
        appointment_time TIME,
        status VARCHAR(20) DEFAULT 'scheduled',
        notes TEXT,
        branch_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients (id),
        FOREIGN KEY (doctor_id) REFERENCES users (id),
        FOREIGN KEY (branch_id) REFERENCES branches (id)
    )
    ''')
    
    # Lab Results table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS lab_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        test_name VARCHAR(100) NOT NULL,
        result_value VARCHAR(255),
        normal_range VARCHAR(100),
        status VARCHAR(20) DEFAULT 'pending',
        report_date DATE,
        branch_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients (id),
        FOREIGN KEY (branch_id) REFERENCES branches (id)
    )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_entries_date ON daily_entries(visit_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_entries_branch ON daily_entries(branch_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_patients_branch ON patients(branch_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_branch ON users(branch_id)')
    
    conn.commit()
    conn.close()
    
    print("✅ Database tables created successfully!")

def create_default_data():
    """Create default admin user and sample branch"""
    
    conn = sqlite3.connect('vaidya_vihar.db')
    cursor = conn.cursor()
    
    print("👤 Creating default admin user and sample data...")
    
    # Create default branch
    cursor.execute('''
    INSERT OR IGNORE INTO branches (id, name, address, phone, email) 
    VALUES (1, 'Main Branch', '123 Healthcare Street, Medical City', '+1-555-0101', 'main@vaidyavihar.com')
    ''')
    
    # Create admin user (password: admin123)
    admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
    
    cursor.execute('''
    INSERT OR IGNORE INTO users (id, username, email, password_hash, first_name, last_name, phone, role, branch_id) 
    VALUES (1, 'admin', 'admin@vaidyavihar.com', ?, 'System', 'Administrator', '+1-555-0100', 'super_admin', 1)
    ''', (admin_password,))
    
    # Create sample patient
    cursor.execute('''
    INSERT OR IGNORE INTO patients (id, first_name, last_name, date_of_birth, gender, phone, branch_id) 
    VALUES (1, 'John', 'Doe', '1980-01-01', 'Male', '+1-555-0102', 1)
    ''')
    
    # Create sample daily entry
    cursor.execute('''
    INSERT OR IGNORE INTO daily_entries (id, patient_id, doctor_id, visit_date, consultation_fee, test_fee, test_type, branch_id) 
    VALUES (1, 1, 1, ?, 500.00, 200.00, 'Blood Test', 1)
    ''', (datetime.now().date(),))
    
    conn.commit()
    conn.close()
    
    print("✅ Default data created successfully!")

def main():
    """Main initialization function"""
    print("🚀 VaidyaVihar Diagnostic ERP - Database Setup")
    print("=" * 50)
    
    try:
        init_database()
        create_default_data()
        
        print("")
        print("🎉 Database setup completed successfully!")
        print("")
        print("📋 Default Credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        print("")
        print("🔧 Next Steps:")
        print("   1. Start the backend: cd backend && python -m uvicorn app.main:app --reload")
        print("   2. Start the frontend: cd frontend/vaidya-vihar-frontend && npm start")
        print("   3. Access the system at http://localhost:3000")
        print("")
        print("📖 For detailed setup instructions, see README.md")
        
    except Exception as e:
        print(f"❌ Error during database setup: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
