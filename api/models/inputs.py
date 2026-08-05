"""Input models for all AstroWorld API endpoints."""

from pydantic import BaseModel, field_validator
from typing import Literal


class BirthData(BaseModel):
    """Core input for any birth-chart-based feature."""
    name: str
    date: str          # "YYYY-MM-DD"
    time: str          # "HH:MM"  (24-hour)
    city: str
    country: str
    system: Literal["vedic", "western", "both"] = "both"

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        from datetime import datetime
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("date must be YYYY-MM-DD")
        return v

    @field_validator("time")
    @classmethod
    def validate_time(cls, v: str) -> str:
        from datetime import datetime
        try:
            datetime.strptime(v, "%H:%M")
        except ValueError:
            raise ValueError("time must be HH:MM (24-hour)")
        return v


class ReadingRequest(BaseModel):
    birth_data: BirthData
    reading_type: Literal["full", "career", "love", "health", "spiritual"] = "full"


class CompatibilityRequest(BaseModel):
    person1: BirthData
    person2: BirthData
