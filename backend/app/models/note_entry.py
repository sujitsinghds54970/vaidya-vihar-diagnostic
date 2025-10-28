from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.utils.database import Base

class NoteEntry(Base):
    __tablename__ = "note_entries"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    author = Column(String, nullable=True)  # Optional: who wrote the note

    calendar_day_id = Column(Integer, ForeignKey("calendar_days.id"))
    calendar_day = relationship("CalendarDay", backref="note_entries")