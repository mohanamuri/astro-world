"""Birth Chart page — Vedic + Western charts."""
import base64
import streamlit as st
from app.components.birth_form import render_birth_form
from app.core.api_client import calculate_chart


def render():
    st.markdown("## 🪐 Birth Chart")
    st.markdown("<p style='color:#888;'>Enter your birth details to get your complete Vedic Kundali and Western natal chart.</p>",
                unsafe_allow_html=True)

    # Concept expander
    with st.expander("📖 What is a Birth Chart?"):
        st.markdown("""
A **birth chart** (also called natal chart or Kundali) is a map of the sky at the exact moment of your birth.
It shows the positions of the Sun, Moon, and all planets across the 12 zodiac signs and 12 houses.

**Vedic Birth Chart (Kundali):**
- Uses the **sidereal zodiac** (actual star positions, Lahiri Ayanamsa correction)
- South Indian grid style: signs are fixed in cells, planets placed in their sign
- Shows **Lagna** (Ascendant), **Rashi** (Moon sign), **Nakshatra** (lunar mansion), and **Vimshottari Dasha** (current planetary period)

**Western Natal Chart:**
- Uses the **tropical zodiac** (based on seasons, not star positions)
- Circular wheel with 12 houses; planets shown on the wheel
- Emphasizes **aspects** — angular relationships between planets showing how energies interact

**Why the signs differ between systems:**
Vedic and Western charts often show different signs for the same planet because of the ~23° ayanamsa offset between tropical and sidereal zodiacs.
""")

    st.divider()
    birth_data = render_birth_form(key_prefix="chart")

    if birth_data:
        with st.spinner("Calculating your birth chart..."):
            result = calculate_chart(birth_data)

        if result:
            _display_chart(result)

    # Show cached result
    elif "chart_result" in st.session_state:
        _display_chart(st.session_state.chart_result)


def _display_chart(result: dict):
    st.session_state.chart_result = result
    info = result["birth_info"]

    # Summary row
    st.markdown(f"""
<div style='background:#1A1A2E;border:1px solid #C9A96E33;border-radius:10px;padding:14px;margin:12px 0;'>
  <strong style='color:#C9A96E;font-size:1.1rem;'>{info['name']}</strong>
  &nbsp;·&nbsp; <span style='color:#B0B8D0;'>{info['date']} at {info['time']}</span>
  &nbsp;·&nbsp; <span style='color:#888;'>{info['city']}, {info['country']}</span>
  &nbsp;·&nbsp; <span style='color:#555;font-size:0.85rem;'>{info['timezone']} (UTC{info['utc_offset']})</span>
</div>""", unsafe_allow_html=True)

    tab_vedic, tab_western = st.tabs(["🕉️  Vedic (Kundali)", "⭕  Western (Natal Wheel)"])

    with tab_vedic:
        _vedic_tab(result)

    with tab_western:
        _western_tab(result)


def _vedic_tab(r: dict):
    col1, col2 = st.columns([1, 1])

    with col1:
        # Key placements
        st.markdown("#### Key Placements")
        metrics = [
            ("Lagna (Ascendant)", r["vedic_lagna"]),
            ("Rashi (Moon Sign)", r["vedic_rashi"]),
            ("Sun Sign",          r["vedic_sun_sign"]),
            ("Nakshatra",         f"{r['nakshatra']} Pada {r['nakshatra_pada']}"),
            ("Nakshatra Lord",    r["nakshatra_lord"]),
            ("Mahadasha",         r["dasha"]["mahadasha_lord"]),
            ("Dasha Ends",        r["dasha"]["mahadasha_end"]),
            ("Antardasha",        r["dasha"]["antardasha_lord"]),
        ]
        for label, value in metrics:
            c1, c2 = st.columns([2, 2])
            c1.markdown(f"<span style='color:#888;font-size:0.85rem;'>{label}</span>", unsafe_allow_html=True)
            c2.markdown(f"<strong style='color:#C9A96E;'>{value}</strong>", unsafe_allow_html=True)

    with col2:
        # Chart image
        if r.get("vedic_chart_image"):
            img_data = base64.b64decode(r["vedic_chart_image"])
            st.image(img_data, use_column_width=True)

    st.divider()

    # Planet table
    st.markdown("#### Planetary Positions (Vedic)")
    planets = r.get("vedic_planets", [])
    if planets:
        rows = ""
        for p in planets:
            retro = " ℞" if p.get("retrograde") else ""
            rows += f"<tr><td>{p['planet']}{retro}</td><td>{p['sign']}</td><td>House {p['house']}</td><td>{p['degree']:.1f}°</td></tr>"

        st.markdown(f"""
<table style='width:100%;border-collapse:collapse;font-size:0.88rem;'>
<thead><tr style='color:#C9A96E;border-bottom:1px solid #2A2A4A;'>
<th style='text-align:left;padding:6px;'>Planet</th>
<th style='text-align:left;padding:6px;'>Sign (Rashi)</th>
<th style='text-align:left;padding:6px;'>House</th>
<th style='text-align:left;padding:6px;'>Degree</th>
</tr></thead><tbody style='color:#E8E8F0;'>
{rows}
</tbody></table>""", unsafe_allow_html=True)


def _western_tab(r: dict):
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### Key Placements")
        metrics = [
            ("Sun Sign",  r["western_sun_sign"]),
            ("Moon Sign", r["western_moon_sign"]),
            ("Rising",    r["western_rising"]),
        ]
        for label, value in metrics:
            c1, c2 = st.columns([2, 2])
            c1.markdown(f"<span style='color:#888;font-size:0.85rem;'>{label}</span>", unsafe_allow_html=True)
            c2.markdown(f"<strong style='color:#C9A96E;'>{value}</strong>", unsafe_allow_html=True)

        st.markdown("#### Aspects")
        aspects = r.get("aspects", [])[:8]
        for asp in aspects:
            color = "#5CAE80" if asp["harmony"] == "Harmonious" else ("#E05C5C" if asp["harmony"] == "Challenging" else "#B0B8D0")
            st.markdown(
                f"<span style='color:{color};font-size:0.85rem;'>● {asp['planet1']} {asp['aspect_type']} {asp['planet2']} ({asp['orb']:.1f}°)</span>",
                unsafe_allow_html=True)

    with col2:
        if r.get("western_chart_image"):
            img_data = base64.b64decode(r["western_chart_image"])
            st.image(img_data, use_column_width=True)
