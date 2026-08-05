"""
Vedic astrology engine — custom calculations.
  - Nakshatra (27 lunar mansions) from Moon longitude
  - Vimshottari Dasha (120-year planetary period system)
  - Ashtakoot compatibility (36-point matching)
  - Mangal Dosha detection
"""

from datetime import date, timedelta
from dataclasses import dataclass
from models.outputs import DashaInfo, AshtakootFactor


# ── Nakshatra data ─────────────────────────────────────────────────────────────

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars",
    "Rahu", "Jupiter", "Saturn", "Mercury", "Ketu",
    "Venus", "Sun", "Moon", "Mars", "Rahu",
    "Jupiter", "Saturn", "Mercury", "Ketu", "Venus",
    "Sun", "Moon", "Mars", "Rahu", "Jupiter",
    "Saturn", "Mercury",
]


def get_nakshatra(moon_longitude: float) -> tuple[str, int, str]:
    """
    Returns (nakshatra_name, pada_1_to_4, ruling_lord)
    from the Moon's absolute longitude (0–360 degrees).
    """
    each_nakshatra = 360 / 27          # 13.333...°
    each_pada      = each_nakshatra / 4

    idx  = int(moon_longitude / each_nakshatra) % 27
    pada = int((moon_longitude % each_nakshatra) / each_pada) + 1

    return NAKSHATRAS[idx], min(pada, 4), NAKSHATRA_LORDS[idx]


# ── Vimshottari Dasha ──────────────────────────────────────────────────────────

DASHA_SEQUENCE = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS    = [7,      20,      6,     10,     7,      18,     16,        19,       17]
DASHA_TOTAL    = 120


def calculate_dasha(moon_longitude: float, birth_date_str: str) -> DashaInfo:
    """
    Calculate the current Mahadasha and Antardasha.
    Based on the Moon's nakshatra at birth.
    """
    from datetime import datetime
    birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
    today      = date.today()

    each_nak   = 360 / 27
    idx        = int(moon_longitude / each_nak) % 27
    lord       = NAKSHATRA_LORDS[idx]
    lord_idx   = DASHA_SEQUENCE.index(lord)

    # How far into the current nakshatra is the Moon?
    fraction_elapsed = (moon_longitude % each_nak) / each_nak
    # Remaining years in the starting dasha at birth
    starting_years_remaining = DASHA_YEARS[lord_idx] * (1 - fraction_elapsed)

    # Walk dashas forward from birth until we pass today
    cursor = birth_date
    dasha_start_idx = lord_idx
    elapsed_years   = starting_years_remaining

    # First dasha: partial
    first_end = _add_years(birth_date, starting_years_remaining)
    if today <= first_end:
        maha_lord     = DASHA_SEQUENCE[lord_idx]
        maha_end      = first_end
        remaining_days = (first_end - birth_date).days
    else:
        cursor = first_end
        idx2   = (lord_idx + 1) % 9
        while True:
            end = _add_years(cursor, DASHA_YEARS[idx2])
            if today <= end:
                maha_lord = DASHA_SEQUENCE[idx2]
                maha_end  = end
                break
            cursor = end
            idx2   = (idx2 + 1) % 9

    # Antardasha within the current Mahadasha
    maha_idx     = DASHA_SEQUENCE.index(maha_lord)
    maha_years   = DASHA_YEARS[maha_idx]
    maha_start   = _add_years(maha_end, -maha_years)

    sub_cursor = maha_start
    for i in range(9):
        sub_idx   = (maha_idx + i) % 9
        sub_lord  = DASHA_SEQUENCE[sub_idx]
        sub_years = (DASHA_YEARS[maha_idx] * DASHA_YEARS[sub_idx]) / DASHA_TOTAL
        sub_end   = _add_years(sub_cursor, sub_years)
        if today <= sub_end:
            antar_lord = sub_lord
            antar_end  = sub_end
            break
        sub_cursor = sub_end
    else:
        antar_lord = DASHA_SEQUENCE[(maha_idx + 8) % 9]
        antar_end  = maha_end

    return DashaInfo(
        mahadasha_lord   = maha_lord,
        mahadasha_end    = maha_end.strftime("%b %Y"),
        antardasha_lord  = antar_lord,
        antardasha_end   = antar_end.strftime("%b %Y"),
    )


def _add_years(d: date, years: float) -> date:
    """Add fractional years to a date."""
    days = int(years * 365.25)
    return d + timedelta(days=days)


# ── Ashtakoot Compatibility ────────────────────────────────────────────────────

# Nakshatra group tables (0-indexed)
VARNA   = [3,2,1,4,4,1,2,3,1,1,2,3,4,1,2,3,4,1,1,2,3,4,1,2,3,4,2]
VASHYA  = [2,4,3,5,5,1,5,5,4,1,1,1,5,5,1,3,3,4,1,1,1,5,5,1,1,5,5]
GANA    = [1,2,1,1,1,2,1,1,2,2,2,1,1,2,1,2,1,2,2,2,1,1,2,2,1,1,1]  # 1=Deva,2=Manav,3=Rakshasa
NADI    = [1,2,3,1,2,3,1,2,3,1,2,3,1,2,3,1,2,3,1,2,3,1,2,3,1,2,3]  # 1=Aadi,2=Madhya,3=Antya
YONI    = [1,2,1,3,4,5,6,7,8,1,2,3,4,5,6,7,8,1,2,3,4,5,6,7,8,1,2]

GANA_COMPAT = {(1,1):6,(1,2):5,(1,3):1,(2,1):6,(2,2):6,(2,3):0,(3,1):0,(3,2):3,(3,3):6}


def _nakshatra_index(moon_longitude: float) -> int:
    return int(moon_longitude / (360 / 27)) % 27


def ashtakoot_score(moon_lon1: float, moon_lon2: float) -> tuple[float, list[AshtakootFactor]]:
    """
    Calculate Ashtakoot compatibility score (max 36 points).
    Returns (total_score, list_of_factor_details).
    """
    n1 = _nakshatra_index(moon_lon1)
    n2 = _nakshatra_index(moon_lon2)

    factors: list[AshtakootFactor] = []
    total = 0.0

    # 1. Varna (1 point)
    v1, v2 = VARNA[n1], VARNA[n2]
    varna_score = 1.0 if v2 >= v1 else 0.0
    total += varna_score
    factors.append(AshtakootFactor(
        factor="Varna", max_points=1, scored=varna_score,
        result="Compatible" if varna_score == 1 else "Challenging"))

    # 2. Vashya (2 points)
    vy1, vy2 = VASHYA[n1], VASHYA[n2]
    vashya_score = 2.0 if vy1 == vy2 else (1.0 if abs(vy1 - vy2) <= 1 else 0.0)
    total += vashya_score
    factors.append(AshtakootFactor(
        factor="Vashya", max_points=2, scored=vashya_score,
        result="Compatible" if vashya_score >= 1.5 else ("Neutral" if vashya_score == 1 else "Challenging")))

    # 3. Tara (3 points) — based on nakshatra distance
    diff = (n2 - n1) % 27
    tara_group = (diff % 9) + 1
    tara_score = 3.0 if tara_group in (1, 3, 5, 7) else (1.5 if tara_group in (2, 6) else 0.0)
    total += tara_score
    factors.append(AshtakootFactor(
        factor="Tara", max_points=3, scored=tara_score,
        result="Compatible" if tara_score >= 2 else ("Neutral" if tara_score == 1.5 else "Challenging")))

    # 4. Yoni (4 points) — animal compatibility
    y1, y2 = YONI[n1], YONI[n2]
    yoni_score = 4.0 if y1 == y2 else (3.0 if abs(y1 - y2) == 1 else (2.0 if abs(y1 - y2) <= 3 else 1.0))
    total += yoni_score
    factors.append(AshtakootFactor(
        factor="Yoni", max_points=4, scored=yoni_score,
        result="Compatible" if yoni_score >= 3 else ("Neutral" if yoni_score == 2 else "Challenging")))

    # 5. Graha Maitri (5 points) — planetary friendship
    lords1_idx = NAKSHATRA_LORDS.index(NAKSHATRA_LORDS[n1]) % 9
    lords2_idx = NAKSHATRA_LORDS.index(NAKSHATRA_LORDS[n2]) % 9
    gm_score = 5.0 if lords1_idx == lords2_idx else (4.0 if abs(lords1_idx - lords2_idx) <= 1 else 3.0)
    total += gm_score
    factors.append(AshtakootFactor(
        factor="Graha Maitri", max_points=5, scored=gm_score,
        result="Compatible" if gm_score >= 4 else "Neutral"))

    # 6. Gana (6 points)
    g1, g2 = GANA[n1], GANA[n2]
    gana_score = float(GANA_COMPAT.get((g1, g2), 3))
    total += gana_score
    factors.append(AshtakootFactor(
        factor="Gana", max_points=6, scored=gana_score,
        result="Compatible" if gana_score >= 5 else ("Neutral" if gana_score == 3 else "Challenging")))

    # 7. Bhakut (7 points) — Moon sign relationship
    rashi_diff = abs(n1 // 2 - n2 // 2) % 12 + 1
    bad_bhakut = rashi_diff in (6, 8, 12)
    bhakut_score = 0.0 if bad_bhakut else 7.0
    total += bhakut_score
    factors.append(AshtakootFactor(
        factor="Bhakut", max_points=7, scored=bhakut_score,
        result="Challenging" if bad_bhakut else "Compatible"))

    # 8. Nadi (8 points) — most important factor
    nd1, nd2 = NADI[n1], NADI[n2]
    nadi_score = 0.0 if nd1 == nd2 else 8.0
    total += nadi_score
    factors.append(AshtakootFactor(
        factor="Nadi", max_points=8, scored=nadi_score,
        result="Challenging (Nadi Dosha)" if nd1 == nd2 else "Compatible"))

    return round(total, 1), factors


def has_mangal_dosha(planets: list) -> bool:
    """
    Mangal Dosha: Mars in houses 1, 2, 4, 7, 8, or 12.
    planets: list of PlanetPosition objects
    """
    dosha_houses = {1, 2, 4, 7, 8, 12}
    for p in planets:
        if p.planet == "Mars" and p.house in dosha_houses:
            return True
    return False
