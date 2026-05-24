# StyleAI Backend

AI-powered personal stylist — FastAPI backend.

---

## Quick Start (5 minutes)

### 1. Install dependencies

```bash
pip install uv
uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and add:
#   ANTHROPIC_API_KEY=sk-ant-...   (get from console.anthropic.com)
#   HF_TOKEN=hf_...                (get from huggingface.co/settings/tokens)
```

### 3. Start services (Postgres + Qdrant + Redis)

```bash
docker compose up -d
```

### 4. Run database migrations

```bash
alembic upgrade head
```

### 5. Start the server

```bash
uvicorn app.main:app --reload
```

Open **http://localhost:8000/docs** — you'll see the interactive API.

---

## API Overview

| Method | Endpoint | What it does |
|--------|----------|--------------|
| `GET` | `/health` | Server status |
| `POST` | `/wardrobe/upload` | Upload a clothing photo → AI tags it |
| `GET` | `/wardrobe` | List all your clothing items |
| `PATCH` | `/wardrobe/{id}` | Correct an AI-detected tag |
| `DELETE` | `/wardrobe/{id}` | Remove an item |
| `GET` | `/recommendations/today` | Get today's outfit |
| `POST` | `/recommendations/{id}/feedback` | Like / skip / worn_today |
| `GET` | `/recommendations/history` | Past outfits |
| `POST` | `/chat` | Chat with the AI stylist |

---

## Try it right now (curl)

```bash
# Check the server is running
curl http://localhost:8000/health

# Upload a clothing photo
curl -X POST http://localhost:8000/wardrobe/upload \
  -F "file=@/path/to/your/shirt.jpg"

# Get today's recommendation (after uploading 3+ items)
curl "http://localhost:8000/recommendations/today?occasion=casual"

# Chat with the stylist
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What should I wear to a job interview today?", "history": []}'
```

---

## Project Structure

```
styleai/
├── app/
│   ├── main.py                  # FastAPI app + startup
│   ├── core/
│   │   └── config.py            # Settings from .env
│   ├── db/
│   │   └── database.py          # SQLAlchemy engine + session
│   ├── models/
│   │   ├── user.py              # User table
│   │   ├── wardrobe.py          # WardrobeItem table
│   │   └── recommendation.py    # OutfitRecommendation table
│   ├── schemas/
│   │   ├── wardrobe.py          # Pydantic request/response models
│   │   └── recommendation.py
│   ├── ai/
│   │   ├── clip_tagger.py       # FashionCLIP zero-shot classifier
│   │   ├── color_extractor.py   # Dominant color extraction
│   │   └── stylist.py           # Claude-powered explanation generator
│   └── services/
│       ├── weather.py           # Open-Meteo weather fetcher
│       ├── outfit_scorer.py     # Rule-based outfit combination scorer
│       └── qdrant_service.py    # Vector DB operations
├── migrations/
│   └── 001_initial.py           # Initial DB schema
├── tests/
├── uploads/                     # Clothing photos saved here
├── docker-compose.yml           # Postgres + Qdrant + Redis
├── pyproject.toml               # Dependencies
├── .env.example                 # Config template
└── Makefile                     # Dev shortcuts
```

---

## What happens when you upload a photo

```
Photo uploaded
    → FashionCLIP detects category (shirt, jeans, sneakers…)
    → Zero-shot style tags assigned (casual, minimalist…)
    → Dominant colors extracted (navy, white…)
    → 512-dim embedding computed
    → Item saved to PostgreSQL
    → Embedding stored in Qdrant
    → JSON response returned to client
```

## What happens when you request today's outfit

```
GET /recommendations/today
    → Fetch weather from Open-Meteo (free, no API key)
    → Compute comfort_score
    → Load user's wardrobe from PostgreSQL
    → Score every top × bottom × shoes combination
    → Pick the best combination
    → Call Claude to generate a style explanation
    → Save recommendation + return to client
```

---

## Next Steps (Phase 2)

- [ ] Add JWT authentication (replace the placeholder user)
- [ ] Build the Next.js frontend
- [ ] Add collaborative filtering (ALS matrix factorization)
- [ ] Add trend scraping pipeline
- [ ] Add mood selector to the recommendation request
- [ ] Fine-tune the outfit scorer with user swipe data (RLHF)
