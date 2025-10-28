from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.utils.database import Base
from datetime import datetime

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String, default="unpaid")  # unpaid, paid, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="invoices")
    branch = relationship("Branch", back_populates="invoices")
    lab_results = relationship("LabResult", back_populates="invoice")