# 🎨 StyleAI — AI Personal Stylist

> Your AI-powered fashion assistant built with FastAPI + FashionCLIP + Claude + Next.js
> Built in Tunisia 🇹🇳 — A fashion marketplace for the future

---

## 📁 Project Structure

```
styleai/
├── backend/          ← Python API (FastAPI + AI)
│   ├── app/
│   │   ├── ai/           ← FashionCLIP + Claude stylist
│   │   ├── api/          ← API routes (wardrobe, chat, recommendations)
│   │   ├── db/           ← Database models + connection
│   │   ├── schemas/      ← Data validation
│   │   ├── services/     ← Weather, Qdrant
│   │   └── main.py       ← App entry point
│   ├── migrations/       ← Database migrations
│   ├── tests/            ← Backend tests
│   ├── pyproject.toml    ← Python dependencies
│   └── .env.example      ← Environment variables template
└── frontend/         ← Next.js app (React + Tailwind)
    ├── app/
    │   ├── page.js       ← Home page
    │   ├── chat/         ← AI stylist chat
    │   └── wardrobe/     ← Upload + view clothes
    └── package.json
```

---

## ⚙️ Requirements

| Tool | Version | Download |
|------|---------|----------|
| Python | 3.14+ | [python.org](https://python.org) |
| Node.js | 24+ | [nodejs.org](https://nodejs.org) |
| Git | any | [git-scm.com](https://git-scm.com) |

---

## 🚀 Installation & Setup

### 1. Clone the project
```powershell
git clone https://github.com/Fnour790/styleai.git
cd styleai
```

### 2. Backend Setup
```powershell
cd backend

# Install uv (Python package manager)
pip install uv

# Install all dependencies
python -m uv sync

# Copy environment file and add your API key
copy .env.example .env
notepad .env
```

### 2. Frontend Setup
```powershell
cd frontend
npm install
```

---

## ▶️ Running the App

You need **2 terminals open at the same time**.

### Terminal 1 — Backend
```powershell
cd C:\Users\MSI\Downloads\styleai
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

Wait until you see:
```
FashionCLIP loaded ✓
StyleAI ready ✓
Application startup complete.
```

### Terminal 2 — Frontend
```powershell
cd C:\Users\MSI\Desktop\styleai\frontend
npm run dev
```

Wait until you see:
```
Ready on http://localhost:3000
```

---

## 🌐 Open in Browser

| Page | URL |
|------|-----|
| 🏠 Home | http://localhost:3000 |
| 👗 Wardrobe | http://localhost:3000/wardrobe |
| 💬 AI Chat | http://localhost:3000/chat |
| 📖 API Docs | http://localhost:8000/docs |

---

## 🤖 Features

### 👗 Wardrobe
- Upload photos of your clothes
- AI automatically detects: category, colors, style tags, season
- Powered by **FashionCLIP** (patrickjohncyh/fashion-clip)

### 💬 AI Stylist Chat
- Chat with your personal AI stylist
- Get outfit recommendations based on your wardrobe
- Powered by **Claude Haiku** (Anthropic)

### 🌤️ Weather-aware
- Outfit suggestions adapted to today's weather
- Uses Open-Meteo (free, no API key needed)

---

## 🔧 Troubleshooting

### PowerShell blocks .venv activation
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Backend can't find modules
Make sure you activated the virtual environment first:
```powershell
.\.venv\Scripts\Activate.ps1
```
You should see `(styleai-backend)` at the start of your terminal line.

### Frontend can't connect to backend
Make sure the backend is running on port 8000 before starting the frontend.

### FashionCLIP takes too long to load
First load downloads ~600MB model — this is normal! After first load it's instant.

---

## 🗄️ Database

The app uses **SQLite** (no installation needed). The database file `styleai.db` is created automatically on first run.

To reset the database:
```powershell
python -c "from app.db.database import engine; from app.db import models; models.Base.metadata.drop_all(engine); models.Base.metadata.create_all(engine); print('DB reset!')"
```

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python) |
| AI Vision | FashionCLIP |
| AI Chat | Claude Haiku (Anthropic) |
| Database | SQLite + SQLAlchemy |
| Frontend | Next.js 15 + React |
| Styling | Tailwind CSS |
| Package Manager | uv (Python), npm (JS) |

---

## 🚀 Deployment (Coming Soon)

| Service | Platform |
|---------|----------|
| Backend | Railway |
| Frontend | Vercel |

---

## 👩‍💻 Author

**Nour Faker** — CS Student, Tunisia 🇹🇳

Built as a learning project to explore AI + full-stack web development.

---

## 📄 License

MIT License — free to use and modify.
