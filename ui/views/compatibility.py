"""Compatibility page — Vedic Ashtakoot + Western Synastry."""
import streamlit as st
from app.components.birth_form import render_birth_form
from app.core.api_client import calculate_compatibility


def render():
    st.markdown("## 💫 Compatibility Analysis")
    st.markdown("<p style='color:#888;'>Vedic Ashtakoot (36-point matching) + Western synastry + AI relationship analysis.</p>",
                unsafe_allow_html=True)

    with st.expander("📖 How is compatibility calculated?"):
        st.markdown("""
**Vedic Ashtakoot (8-factor matching, max 36 points):**
1. **Varna (1 pt)** — Spiritual compatibility and temperament
2. **Vashya (2 pts)** — Mutual attraction and control
3. **Tara (3 pts)** — Birth star compatibility and destiny
4. **Yoni (4 pts)** — Physical and sexual compatibility
5. **Graha Maitri (5 pts)** — Mental compatibility (planetary friendship)
6. **Gana (6 pts)** — Nature compatibility (Deva/Manav/Rakshasa)
7. **Bhakut (7 pts)** — Emotional and financial compatibility
8. **Nadi (8 pts)** — Health, genes, and children (most important factor)

Score interpretation: 27+ = Excellent · 21-26 = Good · 15-20 = Average · Below 15 = Challenging

**Western Synastry:**
Analyzes angular relationships (aspects) between one person's planets and the other person's planets.
Harmonious aspects (Trine, Sextile) = natural flow. Challenging aspects (Square, Opposition) = growth through tension.

**Mangal Dosha:**
Mars in houses 1, 2, 4, 7, 8, or 12 creates Mangal Dosha. Traditional belief: can cause friction in marriage. If both partners have it, the effect is cancelled.
""")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 👤 Person 1")
        p1_submitted = render_birth_form(key_prefix="compat_p1", show_system=False, show_demo=True, button_label="Confirm Person 1 ✅")
        if p1_submitted:
            st.session_state.compat_p1_data = p1_submitted

    with col2:
        st.markdown("#### 👤 Person 2")
        p2_submitted = render_birth_form(key_prefix="compat_p2", show_system=False, show_demo=False, button_label="Confirm Person 2 ✅")
        if p2_submitted:
            st.session_state.compat_p2_data = p2_submitted

    p1 = st.session_state.get("compat_p1_data")
    p2 = st.session_state.get("compat_p2_data")

    # Status indicators
    c1, c2 = st.columns(2)
    with c1:
        if p1:
            st.success(f"✅ Person 1 set: **{p1['name']}**")
        else:
            st.info("Fill Person 1 details and click Calculate")
    with c2:
        if p2:
            st.success(f"✅ Person 2 set: **{p2['name']}**")
        else:
            st.info("Fill Person 2 details and click Calculate")

    # Analyze button — only active when both persons are set
    if p1 and p2:
        if st.button("💫 Analyze Compatibility", type="primary", use_container_width=True):
            with st.spinner("Analyzing compatibility..."):
                result = calculate_compatibility(p1, p2)
            if result:
                _display_result(result)
    elif "compat_result" in st.session_state and not (p1 and p2):
        pass  # stale result cleared when inputs change

    if "compat_result" in st.session_state and p1 and p2:
        _display_result(st.session_state.compat_result)


def _display_result(r: dict):
    st.session_state.compat_result = r

    st.divider()
    st.markdown(f"""
<div style='background:#1A1A2E;border:1px solid #C9A96E33;border-radius:10px;padding:14px;margin:12px 0;'>
  <strong style='color:#C9A96E;font-size:1.1rem;'>💫 {r['person1_name']} + {r['person2_name']}</strong>
</div>""", unsafe_allow_html=True)

    tab_vedic, tab_western, tab_ai = st.tabs(["🕉️ Vedic Ashtakoot", "⭕ Western Synastry", "✨ AI Analysis"])

    with tab_vedic:
        _vedic_compat(r)

    with tab_western:
        _western_compat(r)

    with tab_ai:
        _ai_analysis(r)


def _vedic_compat(r: dict):
    score = r["ashtakoot_total"]
    pct   = r["ashtakoot_percentage"]
    verdict = r["ashtakoot_verdict"]
    color_map = {"Excellent": "#5CAE80", "Good": "#C9A96E", "Average": "#B0B8D0", "Poor": "#E05C5C"}
    color = color_map.get(verdict, "#B0B8D0")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"""
<div style='background:#1A1A2E;border:2px solid {color};border-radius:14px;padding:20px;text-align:center;'>
  <div style='font-size:2.5rem;font-weight:bold;color:{color};'>{score}/36</div>
  <div style='color:#888;font-size:0.9rem;'>{pct}%</div>
  <div style='color:{color};font-size:1.1rem;font-weight:bold;margin-top:8px;'>{verdict}</div>
</div>""", unsafe_allow_html=True)

        # Mangal Dosha
        st.markdown("<br>", unsafe_allow_html=True)
        m1 = r.get("mangal_dosha_p1", False)
        m2 = r.get("mangal_dosha_p2", False)
        st.markdown(f"**Mangal Dosha:**")
        st.markdown(f"- {r['person1_name']}: {'⚠️ Yes' if m1 else '✅ No'}")
        st.markdown(f"- {r['person2_name']}: {'⚠️ Yes' if m2 else '✅ No'}")
        if m1 and m2:
            st.success("Both have Mangal Dosha — effect is cancelled.")

    with col2:
        st.markdown("**Ashtakoot Factor Breakdown**")
        for f in r.get("ashtakoot_factors", []):
            result_color = {"Compatible": "#5CAE80", "Neutral": "#C9A96E", "Challenging": "#E05C5C"}.get(f["result"], "#888")
            bar_pct = int(f["scored"] / f["max_points"] * 100) if f["max_points"] else 0
            st.markdown(f"""
<div style='margin-bottom:10px;'>
  <div style='display:flex;justify-content:space-between;margin-bottom:3px;'>
    <span style='color:#B0B8D0;font-size:0.85rem;'>{f['factor']}</span>
    <span style='color:{result_color};font-size:0.82rem;'>{f['scored']}/{f['max_points']} — {f['result']}</span>
  </div>
  <div class='score-bar-bg'><div class='score-bar-fill' style='width:{bar_pct}%;background:{"#5CAE80" if bar_pct >= 60 else "#E05C5C"};'></div></div>
</div>""", unsafe_allow_html=True)


def _western_compat(r: dict):
    syn_score = r.get("synastry_harmony_score", 50)
    color = "#5CAE80" if syn_score >= 65 else ("#C9A96E" if syn_score >= 40 else "#E05C5C")

    st.metric("Synastry Harmony Score", f"{syn_score}/100",
              delta="Harmonious" if syn_score >= 65 else ("Balanced" if syn_score >= 40 else "Challenging"))

    st.markdown("**Planet Connections**")
    for asp in r.get("synastry_aspects", []):
        harmony_color = "#5CAE80" if asp["harmony"] == "Harmonious" else ("#E05C5C" if asp["harmony"] == "Challenging" else "#888")
        st.markdown(f"""
<div style='background:#1A1A2E;border-left:3px solid {harmony_color};padding:10px 14px;margin:6px 0;border-radius:0 8px 8px 0;'>
  <strong style='color:{harmony_color};font-size:0.85rem;'>{asp['person1_planet']} {asp['aspect_type']} {asp['person2_planet']}</strong>
  <p style='color:#B0B8D0;font-size:0.82rem;margin:3px 0 0;'>{asp.get('interpretation','')}</p>
</div>""", unsafe_allow_html=True)


def _ai_analysis(r: dict):
    summary = r.get("ai_summary", "")
    if summary:
        st.markdown(f"""
<div style='background:#1A1A2E;border-left:3px solid #C9A96E;padding:16px;border-radius:0 10px 10px 0;margin-bottom:16px;'>
  <strong style='color:#C9A96E;'>Overall Assessment</strong>
  <p style='color:#E8E8F0;margin:8px 0 0;line-height:1.8;'>{summary}</p>
</div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**💚 Strengths**")
        for s in r.get("ai_strengths", []):
            st.markdown(f"✅ {s}")
    with col2:
        st.markdown("**⚠️ Challenges**")
        for c in r.get("ai_challenges", []):
            st.markdown(f"🔸 {c}")
