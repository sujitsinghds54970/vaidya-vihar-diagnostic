from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.utils.database import Base

class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    location = Column(String(200), nullable=False)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    pincode = Column(String(10), nullable=False)
    phone = Column(String(15), nullable=False)
    email = Column(String(100), nullable=False)
    license_number = Column(String(100), unique=True)
    established_date = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    users = relationship("User", back_populates="branch")
    patients = relationship("Patient", back_populates="branch")
    daily_entries = relationship("DailyEntry", back_populates="branch")
    staff = relationship("Staff", back_populates="branch")
    inventory_items = relationship("InventoryItem", back_populates="branch")
    appointments = relationship("Appointment", back_populates="branch")
    invoices = relationship("Invoice", back_populates="branch")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="staff")  # super_admin, branch_admin, staff, patient
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime)
    
    # Personal details
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(15), nullable=False)
    
    # Relationships
    branch = relationship("Branch", back_populates="users")
    activity_logs = relationship("ActivityLog", back_populates="user")

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(20), unique=True, nullable=False)  # Auto-generated
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    gender = Column(String(10), nullable=False)  # Male, Female, Other
    phone = Column(String(15), nullable=False)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    pincode = Column(String(10), nullable=False)
    emergency_contact = Column(String(15), nullable=False)
    emergency_contact_name = Column(String(200), nullable=False)
    
    # Medical Information
    blood_group = Column(String(5), nullable=True)
    allergies = Column(Text, nullable=True)
    chronic_conditions = Column(Text, nullable=True)
    current_medications = Column(Text, nullable=True)
    
    # Registration Details
    registration_date = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    branch = relationship("Branch", back_populates="patients")
    daily_entries = relationship("DailyEntry", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient")
    invoices = relationship("Invoice", back_populates="patient")
    lab_results = relationship("LabResult", back_populates="patient")

class DailyEntry(Base):
    __tablename__ = "daily_entries"

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)
    
    # Entry Details
    entry_date = Column(DateTime, nullable=False)
    entry_time = Column(DateTime, default=func.now())
    
    # Doctor Information
    doctor_name = Column(String(200), nullable=False)
    doctor_specialization = Column(String(100), nullable=True)
    consultation_fee = Column(DECIMAL(10, 2), nullable=False)
    
    # Patient Information
    patient_name = Column(String(200), nullable=False)
    patient_mobile = Column(String(15), nullable=False)
    patient_address = Column(Text, nullable=False)
    
    # Test Information
    test_names = Column(Text, nullable=False)  # JSON or comma-separated
    test_cost = Column(DECIMAL(10, 2), default=0)
    discount = Column(DECIMAL(10, 2), default=0)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    
    # Payment Information
    payment_status = Column(String(20), default="pending")  # pending, paid, partial
    payment_mode = Column(String(20))  # cash, card, online, insurance
    amount_paid = Column(DECIMAL(10, 2), default=0)
    
    # Additional Information
    notes = Column(Text, nullable=True)
    referred_by = Column(String(200), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    branch = relationship("Branch", back_populates="daily_entries")
    patient = relationship("Patient", back_populates="daily_entries")
    creator = relationship("User")

class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Employee Details
    employee_id = Column(String(20), unique=True, nullable=False)
    department = Column(String(100), nullable=False)  # reception, lab, billing, admin
    position = Column(String(100), nullable=False)
    date_of_joining = Column(DateTime, nullable=False)
    salary = Column(DECIMAL(12, 2), nullable=False)
    
    # Personal Information
    date_of_birth = Column(DateTime, nullable=False)
    qualification = Column(String(200), nullable=True)
    experience_years = Column(Integer, default=0)
    
    # Attendance & Performance
    total_leaves = Column(Integer, default=0)
    leaves_taken = Column(Integer, default=0)
    performance_rating = Column(Integer, default=5)  # 1-5 scale
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    branch = relationship("Branch", back_populates="staff")
    user = relationship("User")
    attendance_records = relationship("AttendanceRecord", back_populates="staff")
    salary_records = relationship("SalaryRecord", back_populates="staff")

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    
    # Date & Time
    attendance_date = Column(DateTime, nullable=False)
    check_in_time = Column(DateTime, nullable=True)
    check_out_time = Column(DateTime, nullable=True)
    
    # Status
    status = Column(String(20), default="present")  # present, absent, late, half_day, leave
    late_minutes = Column(Integer, default=0)
    overtime_minutes = Column(Integer, default=0)
    
    # Additional Info
    notes = Column(Text, nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    staff = relationship("Staff", back_populates="attendance_records")
    approver = relationship("User")

class SalaryRecord(Base):
    __tablename__ = "salary_records"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    
    # Salary Details
    month = Column(Integer, nullable=False)  # 1-12
    year = Column(Integer, nullable=False)
    base_salary = Column(DECIMAL(12, 2), nullable=False)
    bonus = Column(DECIMAL(10, 2), default=0)
    deductions = Column(DECIMAL(10, 2), default=0)
    
    # Calculated Fields
    gross_salary = Column(DECIMAL(12, 2), nullable=False)
    net_salary = Column(DECIMAL(12, 2), nullable=False)
    
    # Payment Details
    payment_date = Column(DateTime, nullable=True)
    payment_status = Column(String(20), default="pending")  # pending, paid, processed
    payment_mode = Column(String(20), nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    staff = relationship("Staff", back_populates="salary_records")

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    
    # Item Details
    item_code = Column(String(50), unique=True, nullable=False)
    item_name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)  # reagent, equipment, consumable, medicine
    subcategory = Column(String(100), nullable=True)
    unit = Column(String(50), nullable=False)  # pieces, ml, kg, etc.
    
    # Stock Information
    current_stock = Column(Integer, default=0)
    minimum_stock = Column(Integer, default=0)
    maximum_stock = Column(Integer, default=0)
    reorder_level = Column(Integer, default=0)
    
    # Financial Information
    purchase_price = Column(DECIMAL(10, 2), nullable=False)
    selling_price = Column(DECIMAL(10, 2), nullable=False)
    supplier = Column(String(200), nullable=True)
    supplier_contact = Column(String(15), nullable=True)
    
    # Expiry & Batch Information
    batch_number = Column(String(100), nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    manufacture_date = Column(DateTime, nullable=True)
    
    # Status & Tracking
    is_active = Column(Boolean, default=True)
    last_restocked = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    branch = relationship("Branch", back_populates="inventory_items")
    stock_movements = relationship("StockMovement", back_populates="item")

class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    
    # Movement Details
    movement_type = Column(String(20), nullable=False)  # purchase, consumption, wastage, adjustment
    quantity = Column(Integer, nullable=False)
    previous_stock = Column(Integer, nullable=False)
    new_stock = Column(Integer, nullable=False)
    
    # Reference Information
    reference_number = Column(String(100), nullable=True)  # PO number, invoice number, etc.
    movement_date = Column(DateTime, default=func.now())
    notes = Column(Text, nullable=True)
    
    # User Information
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    item = relationship("InventoryItem", back_populates="stock_movements")
    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by])


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    
    # Appointment Details
    appointment_date = Column(DateTime, nullable=False)
    appointment_time = Column(String(10), nullable=False)  # HH:MM format
    appointment_type = Column(String(50), nullable=False)  # consultation, test, follow_up
    department = Column(String(100), nullable=False)
    
    # Doctor Information
    doctor_name = Column(String(200), nullable=False)
    doctor_specialization = Column(String(100), nullable=True)
    
    # Status & Notes
    status = Column(String(20), default="scheduled")  # scheduled, confirmed, completed, cancelled, no_show
    notes = Column(Text, nullable=True)
    
    # Timing
    check_in_time = Column(DateTime, nullable=True)
    completion_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    branch = relationship("Branch", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    
    # Invoice Details
    invoice_number = Column(String(50), unique=True, nullable=False)
    invoice_date = Column(DateTime, default=func.now())
    due_date = Column(DateTime, nullable=True)
    
    # Amount Details
    subtotal = Column(DECIMAL(12, 2), nullable=False)
    tax_amount = Column(DECIMAL(10, 2), default=0)
    discount_amount = Column(DECIMAL(10, 2), default=0)
    total_amount = Column(DECIMAL(12, 2), nullable=False)
    paid_amount = Column(DECIMAL(12, 2), default=0)
    balance_amount = Column(DECIMAL(12, 2), nullable=False)
    
    # Payment Details
    payment_status = Column(String(20), default="pending")  # pending, partial, paid, overdue
    payment_method = Column(String(20), nullable=True)  # cash, card, online, insurance
    payment_date = Column(DateTime, nullable=True)
    
    # Status & Notes
    status = Column(String(20), default="draft")  # draft, sent, paid, cancelled, refunded
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    branch = relationship("Branch", back_populates="invoices")
    patient = relationship("Patient", back_populates="invoices")
    invoice_items = relationship("InvoiceItem", back_populates="invoice")

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    
    # Item Details
    item_name = Column(String(200), nullable=False)
    item_description = Column(Text, nullable=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    total_price = Column(DECIMAL(10, 2), nullable=False)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="invoice_items")

class LabResult(Base):
    __tablename__ = "lab_results"

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    
    # Test Details
    test_name = Column(String(200), nullable=False)
    test_category = Column(String(100), nullable=False)  # blood_test, urine_test, etc.
    test_date = Column(DateTime, nullable=False)
    result_date = Column(DateTime, default=func.now())
    
    # Test Results
    results = Column(Text, nullable=False)  # JSON or detailed text
    normal_range = Column(String(200), nullable=True)
    interpretation = Column(Text, nullable=True)
    status = Column(String(20), default="pending")  # pending, completed, reviewed, reported
    
    # Doctor Information
    requested_by = Column(String(200), nullable=True)
    reviewed_by = Column(String(200), nullable=True)
    lab_technician = Column(String(200), nullable=True)
    
    # Files & Reports
    report_file_path = Column(String(500), nullable=True)
    is_pdf_generated = Column(Boolean, default=False)
    
    # Relationships
    branch = relationship("Branch")
    patient = relationship("Patient", back_populates="lab_results")

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Activity Details
    action = Column(String(100), nullable=False)  # create, update, delete, login, etc.
    entity_type = Column(String(50), nullable=False)  # patient, appointment, invoice, etc.
    entity_id = Column(Integer, nullable=True)
    description = Column(Text, nullable=False)
    
    # Technical Details
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    timestamp = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="activity_logs")

class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String(100), unique=True, nullable=False)
    setting_value = Column(Text, nullable=False)
    setting_type = Column(String(50), default="string")  # string, integer, boolean, json
    description = Column(Text, nullable=True)
    is_editable = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
