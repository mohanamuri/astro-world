# AstroWorld 🌙

**AI-Powered Vedic + Western Astrology Platform**

---

## Features

| Feature | Description |
|---|---|
| 🪐 Birth Chart | Full Vedic Kundali (South Indian grid) + Western natal wheel |
| ✨ AI Reading | Personalized narrative reading via RAG + Groq LLM |
| 💫 Compatibility | Vedic Ashtakoot (36 pts) + Western synastry + AI analysis |
| 🔮 Daily Horoscope | AI-generated forecasts for all 12 signs |

## Architecture

```
astro-world/
├── api/          → FastAPI backend (Render)
└── ui/           → Streamlit frontend (Streamlit Cloud)
```

## Tech Stack

kerykeion · FastAPI · Groq (llama-3.1-70b) · ChromaDB · sentence-transformers · matplotlib · Streamlit

## Local Setup

### API
```bash
cd api && pip install -r requirements.txt
# .env → GROQ_API_KEY=your_key
uvicorn main:app --reload
```

### UI
```bash
cd ui && pip install -r requirements.txt
# ui/.streamlit/secrets.toml → API_URL = "http://localhost:8000"
streamlit run main.py
```

## Deployment
- **API** → Render: root dir `api`, start cmd `uvicorn main:app --host 0.0.0.0 --port $PORT`, env var `GROQ_API_KEY`
- **UI** → Streamlit Cloud: root dir `ui`, main file `main.py`, secret `API_URL`

## Branches
- `main` — stable
- `dev` — active development
