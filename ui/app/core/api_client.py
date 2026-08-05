"""
API client — all HTTP calls to astroworld-api (Render).
URL is read from st.secrets["API_URL"] or environment variable.
"""
import os
import requests
import streamlit as st

def _api_url() -> str:
    try:
        return st.secrets["API_URL"].rstrip("/")
    except Exception:
        return os.environ.get("API_URL", "http://localhost:8000").rstrip("/")


def calculate_chart(birth_data: dict) -> dict | None:
    try:
        r = requests.post(f"{_api_url()}/api/chart/calculate", json=birth_data, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Chart calculation failed: {e}")
        return None


def generate_reading(birth_data: dict, reading_type: str = "full") -> dict | None:
    try:
        r = requests.post(
            f"{_api_url()}/api/reading/generate",
            json={"birth_data": birth_data, "reading_type": reading_type},
            timeout=60,
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Reading generation failed: {e}")
        return None


def calculate_compatibility(person1: dict, person2: dict) -> dict | None:
    try:
        r = requests.post(
            f"{_api_url()}/api/compatibility/calculate",
            json={"person1": person1, "person2": person2},
            timeout=60,
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Compatibility calculation failed: {e}")
        return None


def get_horoscope(sign: str, period: str = "today", system: str = "both") -> dict | None:
    try:
        r = requests.get(
            f"{_api_url()}/api/horoscope/{sign}",
            params={"period": period, "system": system},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Horoscope fetch failed: {e}")
        return None


def health_check() -> bool:
    try:
        r = requests.get(f"{_api_url()}/health", timeout=5)
        return r.status_code == 200
    except Exception:
        return False
