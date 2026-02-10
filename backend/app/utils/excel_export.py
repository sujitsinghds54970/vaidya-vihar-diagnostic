import os
from datetime import datetime, timedelta
from typing import List, Optional
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
import uuid

from app.models import DailyEntry, Patient, Branch, User, Invoice, LabResult
from app.utils.auth_system import auth_guard
from app.schemas.user import MonthlyReportRequest, ExportResponse

class ExcelExportService:
    def __init__(self, base_path: str = "/tmp/exports"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
    
    def generate_monthly_patient_report(
        self, 
        db: Session, 
        year: int, 
        month: int, 
        branch_id: Optional[int] = None,
        doctor_name: Optional[str] = None
    ) -> ExportResponse:
        """Generate monthly patient history Excel report"""
        
        try:
            # Date range for the month
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1) - timedelta(days=1)
            
            # Query daily entries for the month
            query = db.query(DailyEntry).filter(
                and_(
                    DailyEntry.entry_date >= start_date,
                    DailyEntry.entry_date <= end_date
                )
            )
            
            # Filter by branch if specified
            if branch_id:
                query = query.filter(DailyEntry.branch_id == branch_id)
            
            # Filter by doctor if specified
            if doctor_name:
                query = query.filter(DailyEntry.doctor_name.ilike(f"%{doctor_name}%"))
            
            # Order by date
            entries = query.order_by(DailyEntry.entry_date).all()
            
            if not entries:
                return ExportResponse(
                    success=False,
                    message=f"No entries found for {year}-{month:02d}"
                )
            
            # Prepare data for Excel
            report_data = []
            
            for entry in entries:
                # Get branch info
                branch = db.query(Branch).filter(Branch.id == entry.branch_id).first()
                
                # Get patient info if available
                patient_info = ""
                if entry.patient_id:
                    patient = db.query(Patient).filter(Patient.id == entry.patient_id).first()
                    if patient:
                        patient_info = f"{patient.first_name} {patient.last_name}"
                
                report_data.append({
                    "Date": entry.entry_date.strftime("%Y-%m-%d"),
                    "Time": entry.entry_time.strftime("%H:%M:%S"),
                    "Branch": branch.name if branch else "N/A",
                    "Branch Location": branch.location if branch else "N/A",
                    "Doctor Name": entry.doctor_name,
                    "Doctor Specialization": entry.doctor_specialization or "N/A",
                    "Consultation Fee": float(entry.consultation_fee),
                    "Patient Name": entry.patient_name,
                    "Patient Mobile": entry.patient_mobile,
                    "Patient Address": entry.patient_address,
                    "Test Names": entry.test_names,
                    "Test Cost": float(entry.test_cost),
                    "Discount": float(entry.discount),
                    "Total Amount": float(entry.total_amount),
                    "Payment Status": entry.payment_status,
                    "Payment Mode": entry.payment_mode or "N/A",
                    "Amount Paid": float(entry.amount_paid),
                    "Balance Amount": float(entry.total_amount - entry.amount_paid),
                    "Referred By": entry.referred_by or "N/A",
                    "Notes": entry.notes or "N/A",
                    "Patient ID": entry.patient_id if entry.patient_id else "Walk-in"
                })
            
            # Create DataFrame
            df = pd.DataFrame(report_data)
            
            # Create Excel file with multiple sheets
            filename = f"vaidya_vihar_monthly_report_{year}_{month:02d}_{uuid.uuid4().hex[:8]}.xlsx"
            filepath = os.path.join(self.base_path, filename)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Main report sheet
                df.to_excel(writer, sheet_name='Monthly Report', index=False)
                
                # Summary sheet
                summary_data = {
                    "Metric": [
                        "Total Patients",
                        "Total Entries",
                        "Total Consultation Fee",
                        "Total Test Cost",
                        "Total Amount",
                        "Total Paid",
                        "Total Pending",
                        "Cash Payments",
                        "Card Payments",
                        "Online Payments",
                        "Insurance Payments"
                    ],
                    "Value": [
                        df["Patient Mobile"].nunique(),
                        len(df),
                        df["Consultation Fee"].sum(),
                        df["Test Cost"].sum(),
                        df["Total Amount"].sum(),
                        df["Amount Paid"].sum(),
                        df["Balance Amount"].sum(),
                        len(df[df["Payment Mode"] == "cash"]),
                        len(df[df["Payment Mode"] == "card"]),
                        len(df[df["Payment Mode"] == "online"]),
                        len(df[df["Payment Mode"] == "insurance"])
                    ]
                }
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Doctor-wise report
                doctor_summary = df.groupby("Doctor Name").agg({
                    "Patient Mobile": "nunique",
                    "Total Amount": "sum",
                    "Amount Paid": "sum"
                }).reset_index()
                doctor_summary.columns = ["Doctor Name", "Total Patients", "Total Amount", "Total Paid"]
                doctor_summary.to_excel(writer, sheet_name='Doctor Summary', index=False)
                
                # Payment status report
                payment_status = df.groupby("Payment Status").agg({
                    "Patient Mobile": "nunique",
                    "Total Amount": "sum",
                    "Amount Paid": "sum"
                }).reset_index()
                payment_status.columns = ["Payment Status", "Count", "Total Amount", "Total Paid"]
                payment_status.to_excel(writer, sheet_name='Payment Status', index=False)
            
            return ExportResponse(
                success=True,
                message=f"Monthly report generated successfully for {year}-{month:02d}",
                file_path=filepath,
                download_url=f"/api/export/download/{filename}"
            )
            
        except Exception as e:
            return ExportResponse(
                success=False,
                message=f"Error generating report: {str(e)}"
            )
    
    def generate_staff_attendance_report(
        self,
        db: Session,
        year: int,
        month: int,
        branch_id: Optional[int] = None
    ) -> ExportResponse:
        """Generate staff attendance Excel report"""
        
        try:
            from app.models import Staff, AttendanceRecord
            
            # Query staff with attendance records
            query = db.query(Staff).join(AttendanceRecord)
            
            # Filter by branch if specified
            if branch_id:
                query = query.filter(Staff.branch_id == branch_id)
            
            staff_list = query.all()
            
            if not staff_list:
                return ExportResponse(
                    success=False,
                    message=f"No staff records found for {year}-{month:02d}"
                )
            
            report_data = []
            
            for staff in staff_list:
                # Get branch info
                branch = db.query(Branch).filter(Branch.id == staff.branch_id).first()
                
                # Get attendance records for the month
                start_date = datetime(year, month, 1)
                if month == 12:
                    end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
                else:
                    end_date = datetime(year, month + 1, 1) - timedelta(days=1)
                
                attendance_records = db.query(AttendanceRecord).filter(
                    and_(
                        AttendanceRecord.staff_id == staff.id,
                        AttendanceRecord.attendance_date >= start_date,
                        AttendanceRecord.attendance_date <= end_date
                    )
                ).all()
                
                # Calculate summary
                total_days = len(attendance_records)
                present_days = len([r for r in attendance_records if r.status == "present"])
                absent_days = len([r for r in attendance_records if r.status == "absent"])
                late_days = len([r for r in attendance_records if r.status == "late"])
                leave_days = len([r for r in attendance_records if r.status == "leave"])
                
                report_data.append({
                    "Employee ID": staff.employee_id,
                    "Staff Name": f"{staff.user.first_name} {staff.user.last_name}",
                    "Branch": branch.name if branch else "N/A",
                    "Department": staff.department,
                    "Position": staff.position,
                    "Total Working Days": total_days,
                    "Present Days": present_days,
                    "Absent Days": absent_days,
                    "Late Days": late_days,
                    "Leave Days": leave_days,
                    "Attendance Percentage": round((present_days / total_days * 100) if total_days > 0 else 0, 2),
                    "Salary": float(staff.salary),
                    "Date of Joining": staff.date_of_joining.strftime("%Y-%m-%d")
                })
            
            # Create DataFrame
            df = pd.DataFrame(report_data)
            
            # Create Excel file
            filename = f"vaidya_vihar_staff_attendance_{year}_{month:02d}_{uuid.uuid4().hex[:8]}.xlsx"
            filepath = os.path.join(self.base_path, filename)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Attendance Report', index=False)
                
                # Summary sheet
                summary_data = {
                    "Metric": [
                        "Total Staff",
                        "Average Attendance %",
                        "Total Salary",
                        "Departments"
                    ],
                    "Value": [
                        len(df),
                        df["Attendance Percentage"].mean(),
                        df["Salary"].sum(),
                        df["Department"].nunique()
                    ]
                }
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            return ExportResponse(
                success=True,
                message=f"Staff attendance report generated successfully for {year}-{month:02d}",
                file_path=filepath,
                download_url=f"/api/export/download/{filename}"
            )
            
        except Exception as e:
            return ExportResponse(
                success=False,
                message=f"Error generating staff attendance report: {str(e)}"
            )
    
    def generate_inventory_report(
        self,
        db: Session,
        branch_id: Optional[int] = None
    ) -> ExportResponse:
        """Generate inventory status Excel report"""
        
        try:
            from app.models import InventoryItem
            
            query = db.query(InventoryItem)
            
            # Filter by branch if specified
            if branch_id:
                query = query.filter(InventoryItem.branch_id == branch_id)
            
            items = query.all()
            
            if not items:
                return ExportResponse(
                    success=False,
                    message="No inventory items found"
                )
            
            report_data = []
            
            for item in items:
                # Get branch info
                branch = db.query(Branch).filter(Branch.id == item.branch_id).first()
                
                # Calculate stock status
                if item.current_stock <= 0:
                    stock_status = "Out of Stock"
                elif item.current_stock <= item.minimum_stock:
                    stock_status = "Low Stock"
                elif item.current_stock >= item.maximum_stock:
                    stock_status = "Overstocked"
                else:
                    stock_status = "Normal"
                
                # Check expiry status
                expiry_status = "N/A"
                if item.expiry_date:
                    days_to_expiry = (item.expiry_date - datetime.now()).days
                    if days_to_expiry < 0:
                        expiry_status = "Expired"
                    elif days_to_expiry <= 30:
                        expiry_status = "Expiring Soon"
                    else:
                        expiry_status = "Valid"
                
                report_data.append({
                    "Item Code": item.item_code,
                    "Item Name": item.item_name,
                    "Category": item.category,
                    "Subcategory": item.subcategory or "N/A",
                    "Unit": item.unit,
                    "Branch": branch.name if branch else "N/A",
                    "Current Stock": item.current_stock,
                    "Minimum Stock": item.minimum_stock,
                    "Maximum Stock": item.maximum_stock,
                    "Reorder Level": item.reorder_level,
                    "Stock Status": stock_status,
                    "Purchase Price": float(item.purchase_price),
                    "Selling Price": float(item.selling_price),
                    "Supplier": item.supplier or "N/A",
                    "Supplier Contact": item.supplier_contact or "N/A",
                    "Batch Number": item.batch_number or "N/A",
                    "Expiry Date": item.expiry_date.strftime("%Y-%m-%d") if item.expiry_date else "N/A",
                    "Expiry Status": expiry_status,
                    "Manufacture Date": item.manufacture_date.strftime("%Y-%m-%d") if item.manufacture_date else "N/A",
                    "Last Restocked": item.last_restocked.strftime("%Y-%m-%d %H:%M") if item.last_restocked else "N/A"
                })
            
            # Create DataFrame
            df = pd.DataFrame(report_data)
            
            # Create Excel file
            filename = f"vaidya_vihar_inventory_report_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}.xlsx"
            filepath = os.path.join(self.base_path, filename)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Inventory Report', index=False)
                
                # Summary sheet
                total_value = (df["Current Stock"] * df["Purchase Price"]).sum()
                low_stock_items = len(df[df["Stock Status"] == "Low Stock"])
                expired_items = len(df[df["Expiry Status"] == "Expired"])
                
                summary_data = {
                    "Metric": [
                        "Total Items",
                        "Total Inventory Value",
                        "Low Stock Items",
                        "Expired Items",
                        "Categories",
                        "Suppliers"
                    ],
                    "Value": [
                        len(df),
                        total_value,
                        low_stock_items,
                        expired_items,
                        df["Category"].nunique(),
                        df["Supplier"].nunique()
                    ]
                }
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Category-wise report
                category_summary = df.groupby("Category").agg({
                    "Current Stock": "sum",
                    "Purchase Price": "sum"
                }).reset_index()
                category_summary["Total Value"] = category_summary["Current Stock"] * category_summary["Purchase Price"]
                category_summary.to_excel(writer, sheet_name='Category Summary', index=False)
            
            return ExportResponse(
                success=True,
                message="Inventory report generated successfully",
                file_path=filepath,
                download_url=f"/api/export/download/{filename}"
            )
            
        except Exception as e:
            return ExportResponse(
                success=False,
                message=f"Error generating inventory report: {str(e)}"
            )
    
    def download_file(self, filename: str) -> Optional[str]:
        """Download generated Excel file"""
        filepath = os.path.join(self.base_path, filename)
        if os.path.exists(filepath):
            return filepath
        return None
    
    def cleanup_old_files(self, days: int = 7):
        """Clean up files older than specified days"""
        try:
            cutoff_time = datetime.now() - timedelta(days=days)
            
            for filename in os.listdir(self.base_path):
                filepath = os.path.join(self.base_path, filename)
                if os.path.isfile(filepath):
                    file_modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if file_modified_time < cutoff_time:
                        os.remove(filepath)
        except Exception as e:
            print(f"Error cleaning up old files: {str(e)}")

# Export service instance
export_service = ExcelExportService()
