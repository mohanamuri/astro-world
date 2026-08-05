"""
Compatibility router.
POST /api/compatibility/calculate → Ashtakoot + Synastry + AI narrative
"""

from fastapi import APIRouter, HTTPException
from models.inputs import CompatibilityRequest
from models.outputs import CompatibilityResult, SynastryAspect
from routers.chart import calculate_chart
from services.vedic import ashtakoot_score, has_mangal_dosha, get_nakshatra
from services.western import synastry_aspects, synastry_harmony_score
from services.ai_reading import generate_compatibility_narrative

router = APIRouter(prefix="/api/compatibility", tags=["Compatibility"])


def _verdict(score: float) -> str:
    if score >= 27:  return "Excellent"
    if score >= 21:  return "Good"
    if score >= 15:  return "Average"
    return "Poor"


@router.post("/calculate", response_model=CompatibilityResult)
def calculate_compatibility(req: CompatibilityRequest):
    """
    Full compatibility analysis:
    - Vedic Ashtakoot (36-point matching)
    - Western synastry aspects
    - Mangal Dosha check
    - AI narrative
    """
    # Calculate both charts
    try:
        chart1 = calculate_chart(req.person1)
        chart2 = calculate_chart(req.person2)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chart calculation failed: {e}")

    # Ashtakoot
    moon_lon1 = next(
        (p.degree + _sign_offset(p.sign) for p in chart1.vedic_planets if p.planet == "Moon"), 0.0
    )
    moon_lon2 = next(
        (p.degree + _sign_offset(p.sign) for p in chart2.vedic_planets if p.planet == "Moon"), 0.0
    )

    total_score, factors = ashtakoot_score(moon_lon1, moon_lon2)
    mangal1 = has_mangal_dosha(chart1.vedic_planets)
    mangal2 = has_mangal_dosha(chart2.vedic_planets)

    # Western synastry
    syn_raw   = synastry_aspects(chart1.western_planets, chart2.western_planets)
    syn_score = synastry_harmony_score(syn_raw)
    syn_objs  = [SynastryAspect(**a) for a in syn_raw]

    # AI narrative
    try:
        summary, strengths, challenges = generate_compatibility_narrative(
            req.person1.name, req.person2.name, total_score, syn_raw
        )
    except Exception:
        summary    = f"Ashtakoot score: {total_score}/36. {_verdict(total_score)} compatibility."
        strengths  = ["Shared values", "Complementary energies"]
        challenges = ["Differing communication styles"]

    return CompatibilityResult(
        person1_name=req.person1.name,
        person2_name=req.person2.name,
        ashtakoot_total=total_score,
        ashtakoot_percentage=round(total_score / 36 * 100, 1),
        ashtakoot_verdict=_verdict(total_score),
        ashtakoot_factors=factors,
        mangal_dosha_p1=mangal1,
        mangal_dosha_p2=mangal2,
        synastry_aspects=syn_objs,
        synastry_harmony_score=syn_score,
        ai_summary=summary,
        ai_strengths=strengths,
        ai_challenges=challenges,
    )


_SIGN_ORDER = ["Ari","Tau","Gem","Can","Leo","Vir","Lib","Sco","Sag","Cap","Aqu","Pis"]

def _sign_offset(sign: str) -> float:
    abbr = sign[:3].capitalize()
    try:
        return _SIGN_ORDER.index(abbr) * 30.0
    except ValueError:
        return 0.0
