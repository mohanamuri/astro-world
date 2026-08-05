"""
Chart calculation router.
POST /api/chart/calculate → full Vedic + Western birth chart
"""

from fastapi import APIRouter, HTTPException
from models.inputs import BirthData
from models.outputs import ChartResult, BirthInfo
from services.geocode import geocode_city, GeocodingError
from services.astro_calc import calculate_vedic, calculate_western
from services.vedic import get_nakshatra, calculate_dasha
from services.western import calculate_aspects
from services.chart_renderer import render_south_indian_chart, render_western_wheel
import pytz

router = APIRouter(prefix="/api/chart", tags=["Birth Chart"])


@router.post("/calculate", response_model=ChartResult)
def calculate_chart(data: BirthData):
    """
    Calculate a complete birth chart (Vedic + Western).
    Returns planetary positions, nakshatra, dasha, and chart images.
    """
    # 1. Geocode
    try:
        geo = geocode_city(data.city, data.country)
    except GeocodingError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # 2. Vedic chart
    try:
        vedic = calculate_vedic(data.name, data.date, data.time, geo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vedic calculation error: {e}")

    # 3. Nakshatra + Dasha
    nakshatra, pada, nak_lord = get_nakshatra(vedic["moon_longitude"])
    dasha = calculate_dasha(vedic["moon_longitude"], data.date)

    # 4. Western chart
    try:
        western = calculate_western(data.name, data.date, data.time, geo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Western calculation error: {e}")

    aspects = calculate_aspects(western["subject"])

    # 5. Render charts
    vedic_img   = render_south_indian_chart(vedic["planets"], vedic["lagna"])
    western_img = render_western_wheel(western["planets"], aspects)

    # 6. Timezone display
    tz = pytz.timezone(geo.timezone)
    from datetime import datetime
    dt = datetime.strptime(f"{data.date} {data.time}", "%Y-%m-%d %H:%M")
    dt_aware = tz.localize(dt)
    utc_offset = dt_aware.strftime("%z")

    return ChartResult(
        birth_info=BirthInfo(
            name=data.name,
            date=data.date,
            time=data.time,
            city=data.city,
            country=data.country,
            latitude=geo.latitude,
            longitude=geo.longitude,
            timezone=geo.timezone,
            utc_offset=utc_offset,
        ),
        vedic_lagna=vedic["lagna"],
        vedic_rashi=vedic["rashi"],
        vedic_sun_sign=vedic["sun_sign"],
        vedic_planets=vedic["planets"],
        nakshatra=nakshatra,
        nakshatra_pada=pada,
        nakshatra_lord=nak_lord,
        dasha=dasha,
        vedic_chart_image=vedic_img,
        western_sun_sign=western["sun_sign"],
        western_moon_sign=western["moon_sign"],
        western_rising=western["rising"],
        western_planets=western["planets"],
        aspects=aspects,
        western_chart_image=western_img,
    )
