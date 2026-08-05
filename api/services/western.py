"""
Western astrology engine.
Calculates major aspects between planets from a kerykeion subject.
Aspects: Conjunction (0°), Sextile (60°), Square (90°), Trine (120°), Opposition (180°)
"""

from kerykeion import AstrologicalSubject
from models.outputs import AspectInfo


# Orb tolerances for each aspect (in degrees)
ASPECTS = {
    "Conjunction": {"angle": 0,   "orb": 8},
    "Sextile":     {"angle": 60,  "orb": 6},
    "Square":      {"angle": 90,  "orb": 7},
    "Trine":       {"angle": 120, "orb": 8},
    "Opposition":  {"angle": 180, "orb": 8},
}

ASPECT_HARMONY = {
    "Conjunction": "Neutral",
    "Sextile":     "Harmonious",
    "Trine":       "Harmonious",
    "Square":      "Challenging",
    "Opposition":  "Challenging",
}

PLANET_KEYS = [
    "sun", "moon", "mercury", "venus", "mars",
    "jupiter", "saturn", "uranus", "neptune", "pluto",
]

PLANET_DISPLAY = {
    "sun": "Sun", "moon": "Moon", "mercury": "Mercury",
    "venus": "Venus", "mars": "Mars", "jupiter": "Jupiter",
    "saturn": "Saturn", "uranus": "Uranus", "neptune": "Neptune",
    "pluto": "Pluto",
}


def _angular_diff(a: float, b: float) -> float:
    """Smallest angle between two ecliptic positions (0–360)."""
    diff = abs(a - b) % 360
    return min(diff, 360 - diff)


def calculate_aspects(subject: AstrologicalSubject) -> list[AspectInfo]:
    """
    Compute all major aspects between the 10 planets.
    Returns only aspects within orb tolerance.
    """
    # Build position map
    positions = {}
    for key in PLANET_KEYS:
        obj = getattr(subject, key, None)
        if obj:
            positions[key] = float(obj.abs_pos)

    aspects: list[AspectInfo] = []
    keys = list(positions.keys())

    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            k1, k2 = keys[i], keys[j]
            diff = _angular_diff(positions[k1], positions[k2])

            for asp_name, asp_data in ASPECTS.items():
                orb = abs(diff - asp_data["angle"])
                if orb <= asp_data["orb"]:
                    aspects.append(AspectInfo(
                        planet1=PLANET_DISPLAY[k1],
                        planet2=PLANET_DISPLAY[k2],
                        aspect_type=asp_name,
                        orb=round(orb, 2),
                        harmony=ASPECT_HARMONY[asp_name],
                    ))
                    break  # one aspect per pair

    # Sort: harmonious first, then by orb tightness
    aspects.sort(key=lambda a: (0 if a.harmony == "Harmonious" else 1, a.orb))
    return aspects


def synastry_aspects(
    planets1: list,
    planets2: list,
) -> list[dict]:
    """
    Cross-chart aspects between two people's planets.
    planets1/2: list of PlanetPosition objects.
    Returns list of dicts with planet1, planet2, aspect_type, harmony, interpretation.
    """
    pos1 = {p.planet: p.degree + (_sign_offset(p.sign)) for p in planets1}
    pos2 = {p.planet: p.degree + (_sign_offset(p.sign)) for p in planets2}

    INTERP = {
        ("Sun",  "Sun",  "Conjunction"):  "Strong identity alignment — you understand each other deeply.",
        ("Sun",  "Moon", "Conjunction"):  "Natural emotional connection — one energises, one nurtures.",
        ("Venus","Mars", "Trine"):        "Effortless attraction and chemistry.",
        ("Venus","Venus","Trine"):        "Shared values and aesthetics — very harmonious.",
        ("Moon", "Moon", "Trine"):        "Emotional intuition — you feel comfortable together.",
        ("Sun",  "Moon", "Opposition"):   "Complementary but sometimes tension between logic and emotion.",
        ("Mars", "Mars", "Square"):       "High energy but risk of conflict — both want to lead.",
        ("Venus","Saturn","Square"):      "Attraction mixed with restriction — requires patience.",
    }

    results = []
    for p1_name, lon1 in pos1.items():
        for p2_name, lon2 in pos2.items():
            diff = _angular_diff(lon1, lon2)
            for asp_name, asp_data in ASPECTS.items():
                orb = abs(diff - asp_data["angle"])
                if orb <= asp_data["orb"]:
                    key = (p1_name, p2_name, asp_name)
                    interp = INTERP.get(key, INTERP.get((p2_name, p1_name, asp_name),
                        f"{p1_name}–{p2_name} {asp_name}: {ASPECT_HARMONY[asp_name].lower()} influence."))
                    results.append({
                        "person1_planet": p1_name,
                        "person2_planet": p2_name,
                        "aspect_type":    asp_name,
                        "harmony":        ASPECT_HARMONY[asp_name],
                        "interpretation": interp,
                    })
                    break

    results.sort(key=lambda x: (0 if x["harmony"] == "Harmonious" else 1))
    return results[:12]   # return top 12 most relevant


def synastry_harmony_score(aspects: list[dict]) -> float:
    """
    Score the overall harmony of synastry aspects 0–100.
    """
    if not aspects:
        return 50.0
    total = sum(10 if a["harmony"] == "Harmonious" else (-5 if a["harmony"] == "Challenging" else 0)
                for a in aspects)
    base = 50 + total
    return round(max(0.0, min(100.0, float(base))), 1)


_SIGN_ORDER = [
    "Ari", "Tau", "Gem", "Can", "Leo", "Vir",
    "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis",
]

def _sign_offset(sign: str) -> float:
    """Convert sign name to absolute ecliptic offset (0–360)."""
    abbr = sign[:3].capitalize()
    try:
        return _SIGN_ORDER.index(abbr) * 30.0
    except ValueError:
        return 0.0
