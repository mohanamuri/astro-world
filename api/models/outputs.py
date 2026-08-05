"""Output models for all AstroWorld API endpoints."""

from pydantic import BaseModel
from typing import Optional


class PlanetPosition(BaseModel):
    planet: str
    sign: str
    house: int
    degree: float
    retrograde: bool = False


class AspectInfo(BaseModel):
    planet1: str
    planet2: str
    aspect_type: str        # "Conjunction", "Trine", "Square", "Opposition", "Sextile"
    orb: float
    harmony: str            # "Harmonious", "Challenging", "Neutral"


class DashaInfo(BaseModel):
    mahadasha_lord: str
    mahadasha_end: str
    antardasha_lord: str
    antardasha_end: str


class BirthInfo(BaseModel):
    name: str
    date: str
    time: str
    city: str
    country: str
    latitude: float
    longitude: float
    timezone: str
    utc_offset: str


class ChartResult(BaseModel):
    birth_info: BirthInfo

    # Vedic
    vedic_lagna: str
    vedic_rashi: str                       # Moon sign
    vedic_sun_sign: str
    vedic_planets: list[PlanetPosition]
    nakshatra: str
    nakshatra_pada: int
    nakshatra_lord: str
    dasha: DashaInfo
    vedic_chart_image: str                 # base64 PNG — South Indian grid

    # Western
    western_sun_sign: str
    western_moon_sign: str
    western_rising: str
    western_planets: list[PlanetPosition]
    aspects: list[AspectInfo]
    western_chart_image: str               # base64 PNG — circular wheel


class ReadingSection(BaseModel):
    title: str
    content: str


class ReadingResult(BaseModel):
    name: str
    reading_type: str
    key_placements: list[str]              # e.g. ["Sun in Aries", "Moon in Rohini"]
    sections: list[ReadingSection]
    summary: str


class AshtakootFactor(BaseModel):
    factor: str
    max_points: int
    scored: float
    result: str                            # "Compatible", "Neutral", "Challenging"


class SynastryAspect(BaseModel):
    person1_planet: str
    person2_planet: str
    aspect_type: str
    harmony: str
    interpretation: str


class CompatibilityResult(BaseModel):
    person1_name: str
    person2_name: str

    # Vedic Ashtakoot
    ashtakoot_total: float                 # out of 36
    ashtakoot_percentage: float
    ashtakoot_verdict: str                 # "Excellent", "Good", "Average", "Poor"
    ashtakoot_factors: list[AshtakootFactor]
    mangal_dosha_p1: bool
    mangal_dosha_p2: bool

    # Western Synastry
    synastry_aspects: list[SynastryAspect]
    synastry_harmony_score: float          # 0-100

    # AI narrative
    ai_summary: str
    ai_strengths: list[str]
    ai_challenges: list[str]


class HoroscopeResult(BaseModel):
    sign: str
    system: str
    period: str                            # "today", "week"
    date: str
    prediction: str
    lucky_number: int
    lucky_color: str
    lucky_day: str
    energy_level: str                      # "High", "Medium", "Low"
    planetary_influences: list[str]
