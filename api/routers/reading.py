"""
Reading router.
POST /api/reading/generate → AI personalized reading
"""

from fastapi import APIRouter, HTTPException
from models.inputs import ReadingRequest
from models.outputs import ReadingResult
from routers.chart import calculate_chart
from services.ai_reading import generate_reading

router = APIRouter(prefix="/api/reading", tags=["AI Reading"])


@router.post("/generate", response_model=ReadingResult)
def generate_reading_endpoint(req: ReadingRequest):
    """
    Generate a personalized AI reading.
    Internally calculates the chart, then runs RAG + LLM.
    """
    # Calculate full chart first
    try:
        chart = calculate_chart(req.birth_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chart calculation failed: {e}")

    # Generate reading
    try:
        result = generate_reading(chart, req.reading_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reading generation failed: {e}")

    return result
