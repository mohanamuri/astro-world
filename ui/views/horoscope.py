"""Daily / Weekly Horoscope page."""
import streamlit as st
from app.core.api_client import get_horoscope

SIGNS = [
    ("♈", "Aries"), ("♉", "Taurus"), ("♊", "Gemini"), ("♋", "Cancer"),
    ("♌", "Leo"),   ("♍", "Virgo"),  ("♎", "Libra"),  ("♏", "Scorpio"),
    ("♐", "Sagittarius"), ("♑", "Capricorn"), ("♒", "Aquarius"), ("♓", "Pisces"),
]

SIGN_DATES = {
    "Aries": "Mar 21 – Apr 19", "Taurus": "Apr 20 – May 20",
    "Gemini": "May 21 – Jun 20", "Cancer": "Jun 21 – Jul 22",
    "Leo": "Jul 23 – Aug 22", "Virgo": "Aug 23 – Sep 22",
    "Libra": "Sep 23 – Oct 22", "Scorpio": "Oct 23 – Nov 21",
    "Sagittarius": "Nov 22 – Dec 21", "Capricorn": "Dec 22 – Jan 19",
    "Aquarius": "Jan 20 – Feb 18", "Pisces": "Feb 19 – Mar 20",
}


def render():
    st.markdown("## 🔮 Daily Horoscope")
    st.markdown("<p style='color:#888;'>AI-generated daily and weekly forecasts for all 12 signs. No birth details needed.</p>",
                unsafe_allow_html=True)

    with st.expander("📖 Vedic vs Western — which sign should I use?"):
        st.markdown("""
**Western Sun Sign:** Based on your date of birth. What most people know as their "star sign". Good for personality and general forecasts.

**Vedic Moon Sign (Rashi):** Based on the Moon's position in your birth chart. In Vedic astrology, the Moon sign is considered more important than the Sun sign for daily life predictions because the Moon changes signs every 2.5 days and reflects your mind and emotions.

**Recommendation:** If you know your Vedic Moon sign (Rashi), use it for Vedic horoscopes. Otherwise, use your Western Sun sign.
""")

    st.divider()

    # Sign grid
    st.markdown("#### Select Your Sign")
    cols = st.columns(6)
    for i, (emoji, sign) in enumerate(SIGNS):
        with cols[i % 6]:
            selected = st.session_state.get("horo_sign") == sign
            border = "#C9A96E" if selected else "#2A2A4A"
            dates = SIGN_DATES.get(sign, "")
            st.markdown(f"""
<div style='background:#1A1A2E;border:2px solid {border};border-radius:10px;padding:10px;text-align:center;margin-bottom:8px;'>
  <div style='font-size:1.6rem;'>{emoji}</div>
  <div style='color:#C9A96E;font-size:0.85rem;font-weight:bold;'>{sign}</div>
  <div style='color:#555;font-size:0.7rem;'>{dates}</div>
</div>""", unsafe_allow_html=True)
            if st.button("Select", key=f"horo_sign_{sign}", use_container_width=True):
                st.session_state.horo_sign = sign
                st.rerun()

    st.divider()

    selected_sign = st.session_state.get("horo_sign")
    if not selected_sign:
        st.info("Select a sign above to get your horoscope.")
        return

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"**Selected:** {dict(SIGNS).get(selected_sign, '')} {selected_sign}")
    with col2:
        period = st.selectbox("Period", ["today", "week"], key="horo_period",
                               format_func=lambda x: "Today" if x == "today" else "This Week")
    with col3:
        system = st.selectbox("System", ["both", "vedic", "western"], key="horo_system",
                               format_func=lambda x: {"both":"Both","vedic":"Vedic (Moon)","western":"Western (Sun)"}[x])

    if st.button("Get Forecast 🔮", key="horo_get_btn", type="primary"):
        with st.spinner(f"Reading the stars for {selected_sign}..."):
            result = get_horoscope(selected_sign, period, system)
        if result:
            st.session_state.horo_result = result

    result = st.session_state.get("horo_result")
    if result and result.get("sign") == selected_sign:
        _display_horoscope(result)


def _display_horoscope(r: dict):
    emoji = next((e for e, s in SIGNS if s == r["sign"]), "⭐")
    energy_color = {"High": "#5CAE80", "Medium": "#C9A96E", "Low": "#E05C5C"}.get(r["energy_level"], "#888")

    st.markdown(f"""
<div style='background:#1A1A2E;border:1px solid #C9A96E33;border-radius:14px;padding:22px;margin:12px 0;'>
  <h3 style='color:#C9A96E;margin:0 0 4px;'>{emoji} {r['sign']} — {r['period'].capitalize()}</h3>
  <p style='color:#555;font-size:0.82rem;margin:0 0 16px;'>{r['date']} · {r['system'].capitalize()}</p>
  <p style='color:#E8E8F0;line-height:1.8;font-size:1rem;'>{r['prediction']}</p>
  <hr style='border-color:#2A2A4A;margin:16px 0;'>
  <div style='display:flex;gap:24px;flex-wrap:wrap;'>
    <span style='color:#888;'>🔢 Lucky Number: <strong style='color:#C9A96E;'>{r['lucky_number']}</strong></span>
    <span style='color:#888;'>🎨 Lucky Color: <strong style='color:#C9A96E;'>{r['lucky_color']}</strong></span>
    <span style='color:#888;'>📅 Lucky Day: <strong style='color:#C9A96E;'>{r['lucky_day']}</strong></span>
    <span style='color:#888;'>⚡ Energy: <strong style='color:{energy_color};'>{r['energy_level']}</strong></span>
  </div>
  <div style='margin-top:12px;'>
    <span style='color:#888;font-size:0.85rem;'>Planetary influences: </span>
    {''.join(f"<span class='planet-badge'>{p}</span>" for p in r.get('planetary_influences', []))}
  </div>
</div>""", unsafe_allow_html=True)
