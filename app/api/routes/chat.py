"""
Stylist chat route.

POST /chat   — send a message to the AI stylist, get a response
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import WardrobeItem
from app.ai.stylist import chat_with_stylist
from app.services.weather import get_weather

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    message: str
    history: list[dict] = []   # [{"role": "user", "content": "..."}, ...]


class ChatResponse(BaseModel):
    reply: str
    history: list[dict]


@router.post("", response_model=ChatResponse)
async def stylist_chat(body: ChatMessage, db: Session = Depends(get_db)):
    """
    Multi-turn chat with the AI stylist.

    Send the full conversation history each time — the server is stateless.
    The client maintains history and sends it back on each request.
    """
    user_id = "test-user"
    # Load wardrobe summary
    items = db.query(WardrobeItem).filter(
        WardrobeItem.user_id == user_id,
        WardrobeItem.is_active == True,
    ).limit(30).all()

    wardrobe_summary = [
        {
            "category": i.category,
            "colors": i.colors or [],
            "style_tags": i.style_tags or [],
        }
        for i in items
    ]

    # Get weather (use defaults if fetch fails)
    try:
        weather = await get_weather(48.8566, 2.3522)
        weather_dict = weather.model_dump()
    except Exception:
        weather_dict = {"temperature_c": 20, "condition": "cloudy"}

    user_profile = {"style_archetype": "casual"}

    reply = await chat_with_stylist(
        user_profile=user_profile,
        weather=weather_dict,
        wardrobe_summary=wardrobe_summary,
        conversation_history=body.history,
        user_message=body.message,
    )

    updated_history = body.history + [
        {"role": "user", "content": body.message},
        {"role": "assistant", "content": reply},
    ]

    return ChatResponse(reply=reply, history=updated_history)
