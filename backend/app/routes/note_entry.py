from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.utils.database import SessionLocal
from app.models.note_entry import NoteEntry

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/notes/")
def create_note(content: str, calendar_day_id: int, author: str = "", db: Session = Depends(get_db)):
    note = NoteEntry(content=content, calendar_day_id=calendar_day_id, author=author)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

@router.get("/notes/")
def list_notes(db: Session = Depends(get_db)):
    return db.query(NoteEntry).all()