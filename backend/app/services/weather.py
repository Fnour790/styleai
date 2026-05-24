"""
Weather service — fetches real-time conditions from Open-Meteo (free, no API key).

Computes a comfort_score (0–100) that the outfit scorer uses to pick
weather-appropriate clothing.
"""

import httpx
import logging
from app.schemas.recommendation import WeatherContext

logger = logging.getLogger(__name__)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# WMO weather condition codes → human-readable string
WMO_CONDITIONS = {
    0: "sunny", 1: "mostly sunny", 2: "partly cloudy", 3: "cloudy",
    45: "foggy", 48: "foggy",
    51: "light drizzle", 53: "drizzle", 55: "heavy drizzle",
    61: "light rain", 63: "rain", 65: "heavy rain",
    71: "light snow", 73: "snow", 75: "heavy snow",
    80: "showers", 81: "showers", 82: "heavy showers",
    95: "thunderstorm", 96: "thunderstorm", 99: "thunderstorm",
}


async def get_weather(lat: float, lon: float) -> WeatherContext:
    """
    Fetch current weather and compute comfort score.

    comfort_score formula:
        - Ideal temp is 20°C. Each degree away costs 2 points.
        - High humidity (>70%) costs up to 10 points.
        - High wind (>20 km/h) costs up to 10 points.
        - Rain probability >50% costs 15 points.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": [
            "temperature_2m",
            "apparent_temperature",
            "relative_humidity_2m",
            "precipitation_probability",
            "wind_speed_10m",
            "weather_code",
        ],
        "wind_speed_unit": "kmh",
        "timezone": "auto",
        "forecast_days": 1,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(OPEN_METEO_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    current = data["current"]

    temp = current["temperature_2m"]
    feels_like = current["apparent_temperature"]
    humidity = current["relative_humidity_2m"]
    rain_prob = current["precipitation_probability"]
    wind = current["wind_speed_10m"]
    wmo = current["weather_code"]
    condition = WMO_CONDITIONS.get(wmo, "cloudy")

    # Comfort score
    score = 100.0
    score -= min(abs(temp - 20) * 2, 40)          # temperature penalty
    if humidity > 70:
        score -= (humidity - 70) / 3               # humidity penalty (max 10)
    if wind > 20:
        score -= min((wind - 20) / 4, 10)          # wind penalty
    if rain_prob > 50:
        score -= 15                                 # rain penalty
    score = max(0.0, min(100.0, score))

    return WeatherContext(
        temperature_c=round(temp, 1),
        feels_like_c=round(feels_like, 1),
        humidity_pct=round(humidity, 1),
        rain_probability_pct=round(rain_prob, 1),
        wind_kmh=round(wind, 1),
        condition=condition,
        comfort_score=round(score, 1),
    )


def weather_item_score(item_attributes: dict, weather: WeatherContext) -> float:
    """
    Score a single wardrobe item's suitability for the current weather.
    Returns 0–1.
    """
    warmth = item_attributes.get("warmth_score", 0.5)
    score = 1.0

    temp = weather.temperature_c

    # Temperature vs warmth alignment
    if temp < 5:
        score *= warmth                            # cold → reward warm items
    elif temp < 15:
        score *= 0.4 + warmth * 0.6               # cool → prefer warmer items
    elif temp < 22:
        score *= 1.0                               # ideal → all items ok
    elif temp < 28:
        score *= 1.0 - warmth * 0.4               # warm → penalize heavy items
    else:
        score *= 1.0 - warmth * 0.7               # hot → strongly penalize heavy items

    # Rain penalties
    if weather.rain_probability_pct > 50:
        fabric = str(item_attributes.get("attributes", {}).get("fabric", "")).lower()
        if any(x in fabric for x in ["suede", "silk", "velvet"]):
            score *= 0.2    # strong penalty for rain-sensitive fabrics
        category = str(item_attributes.get("category", "")).lower()
        if "sandal" in category or "open" in category:
            score *= 0.3

    return round(min(max(score, 0.0), 1.0), 3)
