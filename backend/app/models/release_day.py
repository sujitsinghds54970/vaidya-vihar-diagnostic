from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.utils.database import Base

class ReleaseDay(Base):
    __tablename__ = "release_days"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # or any other field you need

    calendar_days = relationship("CalendarDay", back_populates="release_day")