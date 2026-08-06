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
    "docs":          ("📖", "Documentation"),
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
    elif page == "docs":
        from views.docs import render
    else:
        from views.home import render

    render()


AUTHOR_CARD_HTML = """
<div style='
    position:fixed;
    top:56px;
    right:16px;
    z-index:9999;
    background:linear-gradient(145deg,#1E1E35,#14142A);
    border:1px solid #3A3A6A;
    border-radius:16px;
    padding:14px 18px;
    display:flex;
    align-items:center;
    gap:14px;
    box-shadow:0 6px 30px rgba(0,0,0,0.55), 0 0 0 1px rgba(201,169,110,0.12);
    min-width:220px;
'>
  <div style='
      width:50px;height:50px;
      background:linear-gradient(135deg,#7B6CF6,#C9A96E);
      border-radius:50%;
      display:flex;align-items:center;justify-content:center;
      font-weight:800;font-size:0.95rem;color:#fff;
      flex-shrink:0;
      box-shadow:0 2px 12px rgba(123,108,246,0.45);
      letter-spacing:0.5px;
  '>MRA</div>
  <div>
    <div style='color:#F0F0FF;font-weight:700;font-size:0.95rem;line-height:1.3;letter-spacing:0.2px;'>Mohan Raju Amuri</div>
    <div style='color:#9090B0;font-size:0.78rem;margin-bottom:7px;font-style:italic;'>AI Engineering Lead</div>
    <div style='display:flex;gap:12px;'>
      <a href='https://linkedin.com/in/mohanamuri555' target='_blank'
         style='color:#5CAE80;font-size:0.8rem;text-decoration:none;font-weight:700;
                background:rgba(92,174,128,0.1);padding:2px 8px;border-radius:6px;
                border:1px solid rgba(92,174,128,0.25);'>
         LinkedIn ↗
      </a>
      <a href='https://github.com/mohanamuri/astro-world' target='_blank'
         style='color:#A89CF0;font-size:0.8rem;text-decoration:none;font-weight:700;
                background:rgba(123,108,246,0.1);padding:2px 8px;border-radius:6px;
                border:1px solid rgba(123,108,246,0.25);'>
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
