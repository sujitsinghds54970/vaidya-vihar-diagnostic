from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.database import SessionLocal
from app.models.inventory_item import InventoryItem

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/inventory/")
def add_item(name: str, category: str, unit: str, quantity: float, threshold: float, db: Session = Depends(get_db)):
    item = InventoryItem(name=name, category=category, unit=unit, quantity=quantity, threshold=threshold)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get("/inventory/")
def list_items(db: Session = Depends(get_db)):
    return db.query(InventoryItem).all()

@router.put("/inventory/{item_id}/update-stock/")
def update_stock(item_id: int, quantity: float, db: Session = Depends(get_db)):
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.quantity += quantity
    db.commit()
    return {"message": "Stock updated", "new_quantity": item.quantity}
@router.get("/inventory/low-stock/")
def get_low_stock_items(db: Session = Depends(get_db)):
    items = db.query(InventoryItem).filter(InventoryItem.quantity < InventoryItem.threshold).all()
    return items
