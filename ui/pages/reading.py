"""AI Reading page."""
import streamlit as st
from app.components.birth_form import render_birth_form
from app.core.api_client import generate_reading

READING_TYPES = {
    "full":      ("🌟", "Full Reading",       "Personality, career, love, health, and spiritual path"),
    "career":    ("💼", "Career & Purpose",   "Professional strengths, ideal work, upcoming opportunities"),
    "love":      ("❤️", "Love & Relationships","Relationship style, what you seek, compatibility patterns"),
    "health":    ("🌿", "Health & Wellbeing", "Health tendencies, mental balance, lifestyle guidance"),
    "spiritual": ("🕉️", "Spiritual Path",     "Dharma, karma, past life themes, spiritual practices"),
}


def render():
    st.markdown("## ✨ AI Personalized Reading")
    st.markdown("<p style='color:#888;'>Your chart analyzed by AI — personalized narrative based on your exact planetary positions.</p>",
                unsafe_allow_html=True)

    with st.expander("📖 How does the AI Reading work?"):
        st.markdown("""
The AI Reading uses a **Retrieval-Augmented Generation (RAG)** pipeline:

1. **Chart Calculation** — Your birth chart is calculated (planetary positions, nakshatra, dasha)
2. **Knowledge Retrieval** — Relevant interpretations are fetched from a curated astrology knowledge base (ChromaDB)
3. **AI Synthesis** — A Groq LLM (Llama 3.1 70B) synthesizes the retrieved context into a personalized narrative specific to your chart
4. **Structured Output** — The reading is organized into clear sections

This is different from generic sun-sign horoscopes — every word is based on your specific chart placements.
""")

    st.divider()

    # Reading type selector
    st.markdown("#### Select Reading Type")
    cols = st.columns(5)
    for i, (rtype, (icon, label, desc)) in enumerate(READING_TYPES.items()):
        with cols[i]:
            selected = st.session_state.get("reading_type", "full") == rtype
            border = "#C9A96E" if selected else "#2A2A4A"
            st.markdown(f"""
<div style='background:#1A1A2E;border:2px solid {border};border-radius:10px;padding:12px;text-align:center;cursor:pointer;'>
  <div style='font-size:1.5rem;'>{icon}</div>
  <div style='color:#C9A96E;font-size:0.85rem;font-weight:bold;margin:4px 0;'>{label}</div>
  <div style='color:#666;font-size:0.75rem;'>{desc}</div>
</div>""", unsafe_allow_html=True)
            if st.button(f"Select", key=f"rt_{rtype}", use_container_width=True):
                st.session_state.reading_type = rtype
                st.rerun()

    reading_type = st.session_state.get("reading_type", "full")
    icon, label, _ = READING_TYPES[reading_type]
    st.markdown(f"<p style='color:#C9A96E;margin:8px 0;'>Selected: {icon} <strong>{label}</strong></p>",
                unsafe_allow_html=True)

    st.divider()
    birth_data = render_birth_form(key_prefix="reading")

    if birth_data:
        with st.spinner(f"Generating your {label}... (this takes 15-30 seconds)"):
            result = generate_reading(birth_data, reading_type)

        if result:
            _display_reading(result)

    elif "reading_result" in st.session_state:
        _display_reading(st.session_state.reading_result)


def _display_reading(result: dict):
    st.session_state.reading_result = result

    st.markdown(f"""
<div style='background:#1A1A2E;border:1px solid #C9A96E33;border-radius:10px;padding:14px;margin:12px 0;'>
  <strong style='color:#C9A96E;font-size:1.1rem;'>✨ Reading for {result['name']}</strong>
  &nbsp;·&nbsp; <span style='color:#888;'>{result['reading_type'].capitalize()} Reading</span>
</div>""", unsafe_allow_html=True)

    # Key placements
    st.markdown("**Key Placements Used:**")
    placements_html = " ".join(
        f"<span class='planet-badge'>{p}</span>"
        for p in result.get("key_placements", [])
    )
    st.markdown(placements_html, unsafe_allow_html=True)

    st.divider()

    # Reading sections
    for section in result.get("sections", []):
        if section["title"] == "SUMMARY":
            continue
        with st.expander(f"📜 {section['title']}", expanded=True):
            st.markdown(
                f"<p style='color:#E8E8F0;line-height:1.8;'>{section['content']}</p>",
                unsafe_allow_html=True)

    # Summary box
    summary = result.get("summary", "")
    if summary:
        st.markdown(f"""
<div style='background:#1A1A2E;border-left:3px solid #C9A96E;padding:16px;border-radius:0 10px 10px 0;margin-top:16px;'>
  <strong style='color:#C9A96E;'>Summary</strong>
  <p style='color:#E8E8F0;margin:8px 0 0;line-height:1.7;'>{summary}</p>
</div>""", unsafe_allow_html=True)
