"""
Core astrology calculation service.
Wraps kerykeion to produce planetary positions for both:
  - Vedic (sidereal, Lahiri ayanamsa)
  - Western (tropical)

Returns structured PlanetPosition lists ready for the API response.
"""

from datetime import datetime
import pytz
from kerykeion import AstrologicalSubject
from models.outputs import PlanetPosition
from services.geocode import GeoResult


# Planets to include in the chart
PLANETS = [
    "sun", "moon", "mercury", "venus", "mars",
    "jupiter", "saturn", "uranus", "neptune", "pluto",
    "true_north_lunar_node",  # Rahu (North Node) — kerykeion v5+
    "true_south_lunar_node",  # Ketu (South Node) — kerykeion v5+
]

PLANET_DISPLAY = {
    "sun":                    "Sun",
    "moon":                   "Moon",
    "mercury":                "Mercury",
    "venus":                  "Venus",
    "mars":                   "Mars",
    "jupiter":                "Jupiter",
    "saturn":                 "Saturn",
    "uranus":                 "Uranus",
    "neptune":                "Neptune",
    "pluto":                  "Pluto",
    "true_north_lunar_node":  "Rahu",
    "true_south_lunar_node":  "Ketu",
}

_HOUSE_NAME_TO_INT = {
    "First_House": 1,  "Second_House": 2,  "Third_House": 3,
    "Fourth_House": 4, "Fifth_House": 5,   "Sixth_House": 6,
    "Seventh_House": 7,"Eighth_House": 8,  "Ninth_House": 9,
    "Tenth_House": 10, "Eleventh_House": 11,"Twelfth_House": 12,
}


def _house_int(house_val) -> int:
    """Convert kerykeion v5 house string (e.g. 'Eighth_House') to int."""
    if house_val is None:
        return 1
    if isinstance(house_val, int):
        return house_val
    return _HOUSE_NAME_TO_INT.get(str(house_val), 1)


def _make_subject(
    name: str,
    date_str: str,
    time_str: str,
    geo: GeoResult,
    sidereal: bool = False,
) -> AstrologicalSubject:
    """
    Build a kerykeion AstrologicalSubject.
    Converts local birth time to the correct UTC offset using pytz.
    """
    dt_local = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    tz = pytz.timezone(geo.timezone)
    dt_aware = tz.localize(dt_local)

    kwargs = dict(
        name=name,
        year=dt_aware.year,
        month=dt_aware.month,
        day=dt_aware.day,
        hour=dt_aware.hour,
        minute=dt_aware.minute,
        city=geo.city,
        nation=geo.country,
        lng=geo.longitude,
        lat=geo.latitude,
        tz_str=geo.timezone,
    )
    if sidereal:
        kwargs["zodiac_type"] = "Sidereal"
        kwargs["sidereal_mode"] = "LAHIRI"

    return AstrologicalSubject(**kwargs)


def _planet_list(subject: AstrologicalSubject) -> list[PlanetPosition]:
    """Extract PlanetPosition list from a kerykeion subject."""
    positions = []
    for key in PLANETS:
        planet_obj = getattr(subject, key, None)
        if planet_obj is None:
            continue
        positions.append(PlanetPosition(
            planet=PLANET_DISPLAY.get(key, key.capitalize()),
            sign=planet_obj.sign,
            house=_house_int(planet_obj.house),
            degree=round(float(planet_obj.position), 2),
            retrograde=bool(getattr(planet_obj, "retrograde", False)),
        ))
    return positions


def calculate_vedic(
    name: str,
    date_str: str,
    time_str: str,
    geo: GeoResult,
) -> dict:
    """
    Returns Vedic chart data:
      lagna (Ascendant sign), rashi (Moon sign), sun_sign,
      planets list, raw moon longitude for nakshatra calculation.
    """
    subject = _make_subject(name, date_str, time_str, geo, sidereal=True)
    planets = _planet_list(subject)

    moon_obj = subject.moon
    moon_longitude = float(moon_obj.abs_pos)   # 0–360 absolute ecliptic longitude

    return {
        "lagna":          subject.first_house.sign,
        "rashi":          moon_obj.sign,
        "sun_sign":       subject.sun.sign,
        "planets":        planets,
        "moon_longitude": moon_longitude,
    }


def calculate_western(
    name: str,
    date_str: str,
    time_str: str,
    geo: GeoResult,
) -> dict:
    """
    Returns Western chart data:
      sun_sign, moon_sign, rising (Ascendant), planets list.
    """
    subject = _make_subject(name, date_str, time_str, geo, sidereal=False)
    planets = _planet_list(subject)

    return {
        "sun_sign":  subject.sun.sign,
        "moon_sign": subject.moon.sign,
        "rising":    subject.first_house.sign,
        "planets":   planets,
        "subject":   subject,          # passed to western.py for aspect calc
    }
