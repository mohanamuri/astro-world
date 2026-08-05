"""Reusable birth data input form."""
import streamlit as st
from datetime import date


DEMO_PROFILES = {
    "Demo — Vedic (New Delhi)": {
        "name": "Arjun Sharma",
        "date": "1985-03-21",
        "time": "10:30",
        "city": "New Delhi",
        "country": "India",
        "system": "both",
    },
    "Demo — Western (London)": {
        "name": "Sophia Blake",
        "date": "1990-06-15",
        "time": "08:15",
        "city": "London",
        "country": "United Kingdom",
        "system": "both",
    },
    "Demo — Compatibility P1": {
        "name": "Priya Nair",
        "date": "1992-11-05",
        "time": "14:00",
        "city": "Mumbai",
        "country": "India",
        "system": "both",
    },
    "Demo — Compatibility P2": {
        "name": "Rohan Verma",
        "date": "1989-07-19",
        "time": "06:45",
        "city": "Pune",
        "country": "India",
        "system": "both",
    },
}


def render_birth_form(
    key_prefix: str = "main",
    show_system: bool = True,
    show_demo: bool = True,
    button_label: str = "Calculate ✨",
) -> dict | None:
    """
    Renders the birth data input form.
    Returns a dict ready to POST to the API, or None if form not submitted.
    """
    if show_demo:
        demo_options = ["— Enter manually —"] + list(DEMO_PROFILES.keys())
        demo_choice  = st.selectbox("Quick load a demo profile", demo_options,
                                     key=f"{key_prefix}_demo")
        if demo_choice != "— Enter manually —":
            profile = DEMO_PROFILES[demo_choice]
            st.session_state[f"{key_prefix}_prefill"] = profile

    prefill = st.session_state.get(f"{key_prefix}_prefill", {})

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Full Name", value=prefill.get("name", ""),
                              key=f"{key_prefix}_name", placeholder="e.g. Arjun Sharma")
        dob  = st.date_input(
            "Date of Birth",
            value=date.fromisoformat(prefill["date"]) if prefill.get("date") else date(1990, 1, 1),
            min_value=date(1900, 1, 1),
            max_value=date.today(),
            key=f"{key_prefix}_dob",
        )
        city = st.text_input("Birth City", value=prefill.get("city", ""),
                              key=f"{key_prefix}_city", placeholder="e.g. Mumbai")

    with col2:
        tob  = st.time_input(
            "Time of Birth",
            key=f"{key_prefix}_time",
            help="Exact time matters for Ascendant and house calculations.",
        )
        country = st.text_input("Birth Country", value=prefill.get("country", ""),
                                 key=f"{key_prefix}_country", placeholder="e.g. India")
        if show_system:
            system = st.selectbox(
                "Astrology System",
                ["both", "vedic", "western"],
                index=["both", "vedic", "western"].index(prefill.get("system", "both")),
                key=f"{key_prefix}_system",
                format_func=lambda x: {"both": "Both Vedic + Western",
                                        "vedic": "Vedic Only",
                                        "western": "Western Only"}[x],
            )
        else:
            system = "both"

    submitted = st.button(button_label, key=f"{key_prefix}_submit", type="primary",
                           use_container_width=True)

    if submitted:
        if not name or not city or not country:
            st.warning("Please fill in Name, City, and Country.")
            return None
        return {
            "name":    name.strip(),
            "date":    dob.strftime("%Y-%m-%d"),
            "time":    tob.strftime("%H:%M"),
            "city":    city.strip(),
            "country": country.strip(),
            "system":  system,
        }
    return None
