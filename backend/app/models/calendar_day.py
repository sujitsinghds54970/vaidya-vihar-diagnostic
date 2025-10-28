from sqlalchemy import Column, Integer, Date, String, ForeignKey
from sqlalchemy.orm import relationship
from app.utils.database import Base

class CalendarDay(Base):
    __tablename__ = "calendar_days"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    status = Column(String, default="open")
    summary = Column(String, nullable=True)

    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    branch = relationship("Branch", back_populates="calendar_days")
    release_day_id = Column(Integer, ForeignKey("release_days.id"))
    release_day = relationship("ReleaseDay", back_populates="calendar_days")
    appointments = relationship("Appointment", back_populates="calendar_day")