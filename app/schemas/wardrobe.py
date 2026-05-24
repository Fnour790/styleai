from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ColorInfo(BaseModel):
    hex: str
    name: str
    pct: float

class WardrobeItemCreate(BaseModel):
    category: str
    subcategory: Optional[str] = None
    colors: list[ColorInfo] = []
    attributes: dict = {}
    style_tags: list[str] = []
    season: list[str] = []
    formality_score: float = 0.5
    warmth_score: float = 0.5
    image_url: str
    brand: Optional[str] = None
    notes: Optional[str] = None

class WardrobeItemUpdate(BaseModel):
    category: Optional[str] = None
    brand: Optional[str] = None
    notes: Optional[str] = None
    style_tags: Optional[list[str]] = None
    is_active: Optional[bool] = None

class WardrobeItemResponse(BaseModel):
    id: str
    category: str
    subcategory: Optional[str] = None
    colors: Optional[list] = []
    attributes: Optional[dict] = {}
    style_tags: Optional[list] = []
    season: Optional[list] = []
    formality_score: float = 0.5
    warmth_score: float = 0.5
    image_url: str
    brand: Optional[str] = None
    times_worn: int = 0
    last_worn_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

class WardrobeUploadResponse(BaseModel):
    item: WardrobeItemResponse
    ai_confidence: float
    message: str