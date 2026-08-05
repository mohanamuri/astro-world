"""
Main Streamlit app — router and layout.
"""
import streamlit as st
from app.theme.styles import apply_theme


def initialize():
    st.set_page_config(
        page_title="AstroWorld — AI Astrology",
        page_icon="🌙",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    if "page" not in st.session_state:
        st.session_state.page = "home"


PAGES = {
    "home":          ("🏠", "Home"),
    "birth_chart":   ("🪐", "Birth Chart"),
    "reading":       ("✨", "AI Reading"),
    "compatibility": ("💫", "Compatibility"),
    "horoscope":     ("🔮", "Daily Horoscope"),
}


def render_sidebar():
    with st.sidebar:
        st.markdown(
            "<h2 style='color:#C9A96E;margin-bottom:4px;'>🌙 AstroWorld</h2>"
            "<p style='color:#888;font-size:0.8rem;margin-top:0;'>AI-Powered Vedic + Western Astrology</p>",
            unsafe_allow_html=True,
        )
        st.divider()

        for key, (icon, label) in PAGES.items():
            active = st.session_state.page == key
            btn_type = "primary" if active else "secondary"
            if st.button(f"{icon}  {label}", key=f"nav_{key}",
                         use_container_width=True, type=btn_type):
                st.session_state.page = key
                st.rerun()

        st.divider()
        st.markdown(
            "<p style='color:#555;font-size:0.75rem;text-align:center;'>"
            "AstroWorld v1.0<br>Vedic · Western · AI</p>",
            unsafe_allow_html=True,
        )


def route():
    page = st.session_state.page

    if page == "home":
        from views.home import render
    elif page == "birth_chart":
        from views.birth_chart import render
    elif page == "reading":
        from views.reading import render
    elif page == "compatibility":
        from views.compatibility import render
    elif page == "horoscope":
        from views.horoscope import render
    else:
        from views.home import render

    render()


AUTHOR_CARD_HTML = """
<div style='
    position:fixed;
    top:60px;
    right:12px;
    z-index:9999;
    background:#1A1A2E;
    border:1px solid #2A2A4A;
    border-radius:12px;
    padding:10px 14px;
    display:flex;
    align-items:center;
    gap:12px;
    box-shadow:0 4px 20px rgba(0,0,0,0.4);
'>
  <div style='
      width:38px;height:38px;
      background:linear-gradient(135deg,#7B6CF6,#C9A96E);
      border-radius:50%;
      display:flex;align-items:center;justify-content:center;
      font-weight:700;font-size:0.8rem;color:#fff;
      flex-shrink:0;
  '>MRA</div>
  <div>
    <div style='color:#E8E8F0;font-weight:700;font-size:0.85rem;line-height:1.2;'>Mohan Raju Amuri</div>
    <div style='color:#888;font-size:0.72rem;margin-bottom:5px;'>AI Engineering Lead</div>
    <div style='display:flex;gap:10px;'>
      <a href='https://linkedin.com/in/mohanamuri555' target='_blank'
         style='color:#5CAE80;font-size:0.75rem;text-decoration:none;font-weight:600;'>
         LinkedIn ↗
      </a>
      <a href='https://github.com/mohanamuri/astro-world' target='_blank'
         style='color:#7B6CF6;font-size:0.75rem;text-decoration:none;font-weight:600;'>
         GitHub ↗
      </a>
    </div>
  </div>
</div>
"""


def render_author_card():
    st.markdown(AUTHOR_CARD_HTML, unsafe_allow_html=True)


def main():
    initialize()
    apply_theme()
    render_author_card()
    render_sidebar()
    route()
