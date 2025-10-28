from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.utils.database import Base

class TestEntry(Base):
    __tablename__ = "test_entries"

    id = Column(Integer, primary_key=True, index=True)
    test_name = Column(String, nullable=False)
    result = Column(String, nullable=True)
    price = Column(Float, nullable=False)

    patient_id = Column(Integer, ForeignKey("patient_entries.id"))
    patient = relationship("PatientEntry", backref="test_entries")