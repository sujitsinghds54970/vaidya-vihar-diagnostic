from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from app.utils.database import Base

class ExpenseEntry(Base):
    __tablename__ = "expense_entries"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)  # e.g. "Lab Supplies", "Electricity"
    notes = Column(String, nullable=True)

    calendar_day_id = Column(Integer, ForeignKey("calendar_days.id"))
    calendar_day = relationship("CalendarDay", backref="expense_entries")