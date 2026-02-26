# New Features Implementation Plan

## Features to Implement:

### 1. Laboratory Information System (LIS) - Test ordering, results
- Enhanced LabTest and LabResult models
- Test ordering workflow
- Sample collection tracking
- Result entry and validation
- Report generation

### 2. SMS/WhatsApp Notifications - Appointment reminders
- Integrate existing SMS/WhatsApp services
- Appointment reminder scheduling
- Automated notifications for:
  - Appointment confirmation
  - Appointment reminders (24h, 2h before)
  - Report ready notifications
  - Payment confirmations

### 3. Payment Gateway - Razorpay/PayU integration
- Payment models
- Razorpay integration
- PayU integration
- Payment status tracking
- Invoice generation with payment links

### 4. Doctor Portal - Separate doctor login
- Doctor authentication
- Doctor dashboard
- View assigned patients
- View patient reports
- Prescription management

### 5. Patient Portal - View own reports
- Patient self-registration
- Patient dashboard
- View own reports
- Download reports
- Appointment booking

### 6. Accounting Module - Expense tracking
- Expense categories
- Expense entry
- Income vs Expense tracking
- Financial reports

### 7. HR/Payroll - Leave management
- Leave types
- Leave requests
- Leave approval workflow
- Leave balance tracking
- Staff attendance

### 8. Mobile App - React Native/Flutter
- Mobile API endpoints
- Mobile-friendly frontend pages
- Push notification support

---

## Implementation Order:
1. Database Models (Backend)
2. API Routes (Backend)
3. Frontend Components
4. Integration & Testing

## Files to Create/Modify:
- Backend Models: lab_test.py, lab_result.py, payment.py, expense.py, leave.py, etc.
- Backend Routes: lis_routes.py, payment_routes.py, doctor_portal.py, patient_portal.py, accounting_routes.py, hr_routes.py
- Frontend: New dashboard components for each feature

