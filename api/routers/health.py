"""Health check router."""
from fastapi import APIRouter

router = APIRouter(tags=["Health"])

@router.get("/health")
def health():
    return {"status": "ok", "service": "AstroWorld API", "version": "1.0.0"}
