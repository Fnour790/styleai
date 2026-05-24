"""
Claude-powered stylist assistant.
"""

import anthropic
import logging
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

SYSTEM_PROMPT = """You are StyleAI, a confident and warm personal stylist assistant.

Your job is to explain WHY a specific outfit works — not just what it is.
You consider weather, occasion, color harmony, and the user's personal style.

Guidelines:
- Be specific and personal, not generic ("this navy blazer" not "the top")
- Mention 1–2 concrete style reasons (color theory, layering logic, occasion fit)
- Keep it to 2–3 sentences — punchy, not a lecture
- Sound like a knowledgeable friend, not a fashion robot
- If weather is challenging (rain, heat, cold), acknowledge how the outfit addresses it
- End with one confidence-boosting sentence

Never use: "stunning", "fabulous", "amazing", "perfect". Keep it real.
"""


async def generate_style_explanation(
    user_profile: dict,
    weather: dict,
    occasion: str,
    outfit_items: list[dict],
    mood: str | None = None,
) -> str:
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    items_text = "\n".join(
        f"- {item.get('category', 'item')} "
        f"(colors: {', '.join(c.get('name', '') for c in item.get('colors', [])[:2])})"
        for item in outfit_items
    )

    weather_text = (
        f"{weather.get('temperature_c', '?')}°C, "
        f"{weather.get('condition', 'unknown')}, "
        f"humidity {weather.get('humidity_pct', '?')}%, "
        f"rain probability {weather.get('rain_probability_pct', '?')}%"
    )

    style = user_profile.get("style_archetype", "undefined")
    mood_line = f"User's current mood: {mood}" if mood else ""

    user_message = f"""Explain this outfit choice for the user.

User style: {style}
Occasion: {occasion}
Weather: {weather_text}
{mood_line}

Outfit items:
{items_text}

Write a 2–3 sentence explanation of why this outfit works today."""

    try:
        message = await client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=200,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        return message.content[0].text.strip()
    except Exception as e:
        logger.error(f"Claude API error: {e}")
        return "This outfit is well-suited for today's conditions and occasion."


async def chat_with_stylist(
    user_profile: dict,
    weather: dict,
    wardrobe_summary: list[dict],
    conversation_history: list[dict],
    user_message: str,
) -> str:
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    wardrobe_text = "\n".join(
        f"- {i.get('category')} "
        f"({', '.join(c.get('name', '') for c in i.get('colors', [])[:2])})"
        for i in wardrobe_summary[:20]
    )

    system = f"""{SYSTEM_PROMPT}

Current context:
- User style archetype: {user_profile.get('style_archetype', 'not set')}
- Today's weather: {weather.get('temperature_c', '?')}°C, {weather.get('condition', 'unknown')}
- User's wardrobe (sample):
{wardrobe_text}

Answer the user's styling question using only their actual wardrobe items.
If they ask about something not in their wardrobe, suggest the closest item they have."""

    messages = conversation_history + [{"role": "user", "content": user_message}]

    try:
        response = await client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=400,
            system=system,
            messages=messages,
        )
        return response.content[0].text.strip()
    except Exception as e:
        logger.error(f"Claude chat error: {e}")
        return "Sorry, I'm having trouble connecting right now. Try again in a moment."