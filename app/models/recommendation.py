from sqlalchemy import Column, String, DateTime, JSON, Float
from sqlalchemy.sql import func
from enum import Enum
import uuid
from app.db.database import Base

class FeedbackType(str, Enum):
    like = "like"
    skip = "skip"
    dislike = "dislike"
    worn = "worn_today"

class OutfitRecommendation(Base):
    __tablename__ = "outfit_recommendations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    item_ids = Column(JSON, default=list)
    item_roles = Column(JSON, default=dict)
    confidence_score = Column(Float, default=0.0)
    weather_comfort_score = Column(Float, default=0.0)
    trend_score = Column(Float, default=0.0)
    mood_match_score = Column(Float, default=0.0)
    context = Column(JSON, default=dict)
    style_explanation = Column(String, nullable=True)
    color_palette = Column(JSON, default=list)
    feedback = Column(String, nullable=True)
    feedback_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())