from sqlalchemy import Column, String, DateTime, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)

    # Style profile
    style_archetype = Column(String, nullable=True)   # e.g. "minimalist", "streetwear"
    body_type = Column(String, nullable=True)          # e.g. "athletic", "pear"
    skin_tone = Column(String, nullable=True)          # e.g. "warm_medium"
    gender_expression = Column(String, nullable=True)

    # Location (for weather)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    city = Column(String, nullable=True)

    # User preferences stored as JSON
    preferences = Column(JSON, default=dict)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    wardrobe_items = relationship("WardrobeItem", back_populates="user", cascade="all, delete")
    recommendations = relationship("OutfitRecommendation", back_populates="user", cascade="all, delete")

    def __repr__(self):
        return f"<User {self.email}>"
