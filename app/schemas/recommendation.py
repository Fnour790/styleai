from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime
from app.models.recommendation import FeedbackType


class WeatherContext(BaseModel):
    temperature_c: float
    feels_like_c: float
    humidity_pct: float
    rain_probability_pct: float
    wind_kmh: float
    condition: str           # "sunny", "cloudy", "rainy"
    comfort_score: float     # 0–100


class OutfitItem(BaseModel):
    item_id: str
    role: str                # "top", "bottom", "footwear", "outerwear", "accessory"
    category: str
    image_url: str
    colors: list[dict]


class RecommendationResponse(BaseModel):
    id: UUID4
    items: list[OutfitItem]
    confidence_score: float
    weather_comfort_score: float
    trend_score: float
    style_explanation: str
    color_palette: list[str]
    context: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedbackRequest(BaseModel):
    feedback: FeedbackType


class RecommendationRequest(BaseModel):
    occasion: Optional[str] = "casual"   # "casual", "work", "date", "formal", "sport"
    mood: Optional[str] = None            # "happy", "tired", "confident", "cozy"
    override_weather: Optional[dict] = None
