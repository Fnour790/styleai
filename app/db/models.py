from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.db.database import Base
import uuid

class WardrobeItem(Base):
    __tablename__ = "wardrobe_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    category = Column(String, nullable=True)
    subcategory = Column(String, nullable=True)
    colors = Column(Text, nullable=True)
    attributes = Column(Text, nullable=True)
    style_tags = Column(Text, nullable=True)
    season = Column(String, nullable=True)
    formality_score = Column(Float, default=0.5)
    warmth_score = Column(Float, default=0.5)
    image_url = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    qdrant_id = Column(String, nullable=True)
    brand = Column(String, nullable=True)
    purchase_price = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    times_worn = Column(Integer, default=0)
    last_worn_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())