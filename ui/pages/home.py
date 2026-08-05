"""Home page — landing + quick horoscope."""
import streamlit as st
from app.core.api_client import get_horoscope, health_check

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
         "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

SIGN_EMOJIS = {
    "Aries":"♈","Taurus":"♉","Gemini":"♊","Cancer":"♋","Leo":"♌","Virgo":"♍",
    "Libra":"♎","Scorpio":"♏","Sagittarius":"♐","Capricorn":"♑","Aquarius":"♒","Pisces":"♓",
}


def render():
    # Hero
    st.markdown("""
<div style='text-align:center;padding:20px 0 10px;'>
  <h1 style='font-size:2.8rem;color:#C9A96E;margin-bottom:6px;'>🌙 AstroWorld</h1>
  <p style='font-size:1.1rem;color:#B0B8D0;'>AI-Powered Vedic + Western Astrology</p>
  <p style='color:#888;font-size:0.9rem;'>Birth Charts · AI Readings · Compatibility · Daily Horoscope</p>
</div>
""", unsafe_allow_html=True)

    st.divider()

    # Feature cards
    c1, c2, c3, c4 = st.columns(4)
    for col, icon, title, desc in [
        (c1, "🪐", "Birth Chart",    "Full Vedic Kundali + Western wheel with all planetary positions"),
        (c2, "✨", "AI Reading",     "Personalized narrative reading powered by RAG + Groq AI"),
        (c3, "💫", "Compatibility",  "Vedic Ashtakoot (36 pts) + Western synastry + AI analysis"),
        (c4, "🔮", "Daily Horoscope","Today's and weekly forecast for all 12 signs"),
    ]:
        with col:
            st.markdown(f"""
<div style='background:#1A1A2E;border:1px solid #2A2A4A;border-radius:12px;padding:16px;text-align:center;'>
  <div style='font-size:2rem;'>{icon}</div>
  <h4 style='color:#C9A96E;margin:8px 0 4px;'>{title}</h4>
  <p style='color:#888;font-size:0.82rem;margin:0;'>{desc}</p>
</div>""", unsafe_allow_html=True)

    st.divider()

    # Quick horoscope
    st.markdown("### 🔮 Quick Horoscope — No Birth Data Needed")

    col_sign, col_period, col_sys = st.columns([2, 1, 1])
    with col_sign:
        sign = st.selectbox("Select Your Sign", SIGNS, key="home_sign")
    with col_period:
        period = st.selectbox("Period", ["today", "week"], key="home_period",
                               format_func=lambda x: "Today" if x == "today" else "This Week")
    with col_sys:
        system = st.selectbox("System", ["both", "vedic", "western"], key="home_system",
                               format_func=lambda x: {"both":"Both","vedic":"Vedic","western":"Western"}[x])

    if st.button("Get Horoscope 🔮", key="home_horo_btn", type="primary"):
        with st.spinner(f"Reading the stars for {sign}..."):
            data = get_horoscope(sign, period, system)
        if data:
            emoji = SIGN_EMOJIS.get(sign, "⭐")
            st.markdown(f"""
<div style='background:#1A1A2E;border:1px solid #C9A96E33;border-radius:12px;padding:20px;margin-top:12px;'>
  <h3 style='color:#C9A96E;'>{emoji} {data['sign']} — {data['period'].capitalize()}</h3>
  <p style='color:#E8E8F0;line-height:1.7;'>{data['prediction']}</p>
  <hr style='border-color:#2A2A4A;margin:12px 0;'>
  <div style='display:flex;gap:20px;flex-wrap:wrap;'>
    <span style='color:#888;'>🔢 Lucky Number: <strong style='color:#C9A96E'>{data['lucky_number']}</strong></span>
    <span style='color:#888;'>🎨 Lucky Color: <strong style='color:#C9A96E'>{data['lucky_color']}</strong></span>
    <span style='color:#888;'>📅 Lucky Day: <strong style='color:#C9A96E'>{data['lucky_day']}</strong></span>
    <span style='color:#888;'>⚡ Energy: <strong style='color:#C9A96E'>{data['energy_level']}</strong></span>
  </div>
</div>""", unsafe_allow_html=True)

    st.divider()

    # What is AstroWorld
    with st.expander("ℹ️ What is AstroWorld?"):
        st.markdown("""
**AstroWorld** combines two astrology systems — Vedic (Jyotish) and Western — with modern AI to deliver personalized, production-grade astrological insights.

**Vedic Astrology (Jyotish):**
Uses the sidereal zodiac (actual star positions), emphasizing the Moon sign (Rashi), Ascendant (Lagna), Nakshatras (27 lunar mansions), and Vimshottari Dashas (planetary period system).

**Western Astrology:**
Uses the tropical zodiac, focusing on Sun sign, personality archetypes, and planetary aspects between chart positions.

**AI Layer:**
A RAG pipeline retrieves relevant astrological interpretations from a curated knowledge base, then a Groq LLM synthesizes them into a personalized narrative specific to your chart.

**Built with:** kerykeion · FastAPI · Groq · ChromaDB · Streamlit
""")
