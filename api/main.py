"""
AstroWorld API — main entry point
Runs on Render free tier. All astrology calculations + AI readings served from here.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from routers import health, chart, reading, compatibility, horoscope
from services.ai_reading import init_knowledge_base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the ChromaDB knowledge base once at startup."""
    print("AstroWorld API starting — loading knowledge base...")
    init_knowledge_base()
    print("Knowledge base ready.")
    yield


app = FastAPI(
    title="AstroWorld API",
    description=(
        "Production-grade Vedic + Western astrology engine. "
        "Birth chart calculations, AI-personalized readings, "
        "compatibility analysis, and daily horoscopes."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chart.router)
app.include_router(reading.router)
app.include_router(compatibility.router)
app.include_router(horoscope.router)


@app.get("/", tags=["Root"])
def root():
    return {
        "service": "AstroWorld API",
        "version": "1.0.0",
        "description": "Vedic + Western Astrology Engine powered by AI",
        "endpoints": {
            "health":        "GET  /health",
            "chart":         "POST /api/chart/calculate",
            "reading":       "POST /api/reading/generate",
            "compatibility": "POST /api/compatibility/calculate",
            "horoscope":     "GET  /api/horoscope/{sign}",
            "docs":          "GET  /docs",
        },
    }
