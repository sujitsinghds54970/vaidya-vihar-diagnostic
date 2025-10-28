from sqlalchemy import Column, Integer, String, Float
from app.utils.database import Base

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)  # e.g. "Lab Supply", "Admin"
    unit = Column(String, nullable=False)     # e.g. "ml", "pieces"
    quantity = Column(Float, default=0.0)
    threshold = Column(Float, default=0.0)     # Alert if quantity < threshold