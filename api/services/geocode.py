"""
Geocoding service.
Converts city + country → latitude, longitude, timezone.
Uses geopy Nominatim (free, no API key) + timezonefinder (offline).
"""

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from timezonefinder import TimezoneFinder
from dataclasses import dataclass


_geolocator = Nominatim(user_agent="astroworld_api_v1")
_tf = TimezoneFinder()


@dataclass
class GeoResult:
    city: str
    country: str
    latitude: float
    longitude: float
    timezone: str           # e.g. "Asia/Kolkata"
    display_name: str


class GeocodingError(Exception):
    pass


def geocode_city(city: str, country: str) -> GeoResult:
    """
    Resolve a city + country to coordinates and timezone.
    Raises GeocodingError if the city cannot be found.
    """
    query = f"{city}, {country}"
    try:
        location = _geolocator.geocode(query, timeout=10)
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        raise GeocodingError(f"Geocoding service unavailable: {e}")

    if location is None:
        raise GeocodingError(
            f"Could not find '{query}'. "
            "Try a nearby major city or check the spelling."
        )

    lat = location.latitude
    lon = location.longitude

    tz = _tf.timezone_at(lat=lat, lng=lon)
    if tz is None:
        # Ocean or unmapped area — fall back to UTC
        tz = "UTC"

    return GeoResult(
        city=city,
        country=country,
        latitude=lat,
        longitude=lon,
        timezone=tz,
        display_name=location.address,
    )
