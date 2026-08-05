"""
Horoscope router.
GET /api/horoscope/{sign}?period=today&system=vedic
"""

import random
from datetime import date
from fastapi import APIRouter, Query
from models.outputs import HoroscopeResult
from services.ai_reading import generate_horoscope

router = APIRouter(prefix="/api/horoscope", tags=["Horoscope"])

LUCKY_COLORS = ["Royal Blue", "Golden Yellow", "Emerald Green", "Deep Red",
                "Silver White", "Violet", "Coral Orange", "Pearl White",
                "Midnight Blue", "Saffron", "Turquoise", "Rose Pink"]

LUCKY_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

ENERGY_LEVELS = ["High", "Medium", "Low"]

# Planetary influences by sign (simplified)
SIGN_PLANETS = {
    "Aries": ["Mars", "Sun"], "Taurus": ["Venus", "Moon"],
    "Gemini": ["Mercury", "Rahu"], "Cancer": ["Moon", "Jupiter"],
    "Leo": ["Sun", "Jupiter"], "Virgo": ["Mercury", "Saturn"],
    "Libra": ["Venus", "Saturn"], "Scorpio": ["Mars", "Ketu"],
    "Sagittarius": ["Jupiter", "Sun"], "Capricorn": ["Saturn", "Mars"],
    "Aquarius": ["Saturn", "Rahu"], "Pisces": ["Jupiter", "Venus"],
}

VALID_SIGNS = list(SIGN_PLANETS.keys())


@router.get("/{sign}", response_model=HoroscopeResult)
def get_horoscope(
    sign: str,
    period: str = Query("today", pattern="^(today|week)$"),
    system: str = Query("both", pattern="^(vedic|western|both)$"),
):
    """
    Get today's or weekly horoscope for a zodiac sign.
    sign: Aries, Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpio,
          Sagittarius, Capricorn, Aquarius, Pisces
    """
    sign_clean = sign.strip().capitalize()
    if sign_clean not in VALID_SIGNS:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=422,
            detail=f"Invalid sign '{sign}'. Valid signs: {', '.join(VALID_SIGNS)}"
        )

    # AI-generated prediction
    try:
        prediction = generate_horoscope(sign_clean, system, period)
    except Exception:
        prediction = (
            f"The stars are aligned for {sign_clean} {period}. "
            "Trust your instincts and stay focused on what matters most to you."
        )

    # Deterministic "lucky" elements (seeded by sign + date for consistency)
    seed = hash(f"{sign_clean}{date.today().isoformat()}") % 1000
    rng  = random.Random(seed)

    planets = SIGN_PLANETS.get(sign_clean, ["Jupiter", "Sun"])

    return HoroscopeResult(
        sign=sign_clean,
        system=system,
        period=period,
        date=date.today().isoformat(),
        prediction=prediction,
        lucky_number=rng.randint(1, 9),
        lucky_color=rng.choice(LUCKY_COLORS),
        lucky_day=rng.choice(LUCKY_DAYS),
        energy_level=rng.choice(ENERGY_LEVELS),
        planetary_influences=planets,
    )
