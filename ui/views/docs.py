"""Documentation page — Architecture, Tech Stack, API Reference, Pipelines, AI/RAG, Glossary."""
import streamlit as st


def render():
    st.markdown("## 📖 Platform Documentation")
    st.markdown(
        "<p style='color:#888;'>One-place reference — architecture, tech stack, API commands, and pipeline explanations.</p>",
        unsafe_allow_html=True,
    )

    tab_arch, tab_stack, tab_api, tab_pipelines, tab_ai, tab_glossary = st.tabs([
        "🏛️ Architecture",
        "🛠️ Tech Stack",
        "⚡ API & curl",
        "🔄 Pipelines",
        "🤖 AI & RAG",
        "📖 Glossary",
    ])

    with tab_arch:
        _architecture()

    with tab_stack:
        _tech_stack()

    with tab_api:
        _api_reference()

    with tab_pipelines:
        _pipelines()

    with tab_ai:
        _ai_rag()

    with tab_glossary:
        _glossary()


# ─────────────────────────────────────────────────────────────────────────────
# ARCHITECTURE
# ─────────────────────────────────────────────────────────────────────────────
def _architecture():
    st.markdown("### Platform Architecture")
    st.markdown(
        "AstroWorld is a full-stack AI astrology platform. The Streamlit UI and FastAPI backend are "
        "independently deployed. The API handles all heavy computation (chart math, AI inference, geocoding) "
        "while the UI focuses purely on presentation."
    )

    st.markdown("""
```
┌─────────────────────────────────────────────────────────────────────────┐
│                           External Services                             │
│    ┌──────────────────────┐          ┌─────────────────────────────┐    │
│    │   Nominatim (OSM)    │          │   Groq Cloud API            │    │
│    │   Geocoding + TZ     │          │   llama-3.3-70b-versatile   │    │
│    │   (free, no key)     │          │   llama-3.1-8b-instant      │    │
│    └──────────────────────┘          └─────────────────────────────┘    │
└────────────────┬─────────────────────────────┬───────────────────────────┘
                 │ HTTP                         │ HTTPS / LangChain
    ┌────────────▼─────────────┐   REST    ┌───▼────────────────────────┐
    │  Streamlit Cloud         │ ◄────────► │  Render (Free Tier)        │
    │  (streamlit.app)         │           │  FastAPI + Uvicorn          │
    │                          │           │                             │
    │  ┌────────────────────┐  │           │  ┌─────────────────────┐   │
    │  │  Streamlit UI      │  │           │  │  API Routers (5)    │   │
    │  │  5 Feature Pages   │  │           │  │  /chart /reading    │   │
    │  │  + Docs Page       │  │           │  │  /compat /horoscope │   │
    │  └────────────────────┘  │           │  │  /health            │   │
    │                          │           │  └─────────────────────┘   │
    └──────────────────────────┘           │                             │
                                           │  ┌─────────────────────┐   │
                                           │  │  Services Layer      │   │
                                           │  │  astro_calc.py       │   │
                                           │  │  vedic.py            │   │
                                           │  │  western.py          │   │
                                           │  │  ai_reading.py       │   │
                                           │  │  geocode.py          │   │
                                           │  │  chart_renderer.py   │   │
                                           │  └─────────────────────┘   │
                                           │                             │
                                           │  ┌─────────────────────┐   │
                                           │  │  ChromaDB (in-mem)  │   │
                                           │  │  Knowledge Base      │   │
                                           │  │  ~30 MD chunks       │   │
                                           │  └─────────────────────┘   │
                                           └─────────────────────────────┘
```
""")

    st.markdown("### Key Design Decisions")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
<div style='background:#1A1A2E;border:1px solid #C9A96E44;border-radius:10px;padding:16px;height:140px;'>
  <div style='color:#C9A96E;font-weight:700;margin-bottom:8px;'>Decoupled UI + API</div>
  <div style='color:#B0B8D0;font-size:0.85rem;line-height:1.6;'>
    UI is a thin HTTP client — all astro math and AI live in the API.
    Either can be replaced or scaled independently.
  </div>
</div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
<div style='background:#1A1A2E;border:1px solid #7B6CF644;border-radius:10px;padding:16px;height:140px;'>
  <div style='color:#A89CF0;font-weight:700;margin-bottom:8px;'>Lazy LLM Init</div>
  <div style='color:#B0B8D0;font-size:0.85rem;line-height:1.6;'>
    LLMs initialize on first request, not at startup.
    Prevents cold-start crashes if GROQ_API_KEY is missing.
  </div>
</div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
<div style='background:#1A1A2E;border:1px solid #5CAE8044;border-radius:10px;padding:16px;height:140px;'>
  <div style='color:#5CAE80;font-weight:700;margin-bottom:8px;'>Session State Forms</div>
  <div style='color:#B0B8D0;font-size:0.85rem;line-height:1.6;'>
    Multi-person forms persist data in <code>st.session_state</code> to
    survive Streamlit's single-render-cycle limitation.
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown("""
<div style='background:#1A1A2E;border:1px solid #C9A96E44;border-radius:10px;padding:16px;height:140px;'>
  <div style='color:#C9A96E;font-weight:700;margin-bottom:8px;'>Sidereal + Tropical</div>
  <div style='color:#B0B8D0;font-size:0.85rem;line-height:1.6;'>
    Same kerykeion engine produces both Vedic (Lahiri sidereal) and Western
    (tropical) charts from one birth data input.
  </div>
</div>""", unsafe_allow_html=True)
    with col5:
        st.markdown("""
<div style='background:#1A1A2E;border:1px solid #7B6CF644;border-radius:10px;padding:16px;height:140px;'>
  <div style='color:#A89CF0;font-weight:700;margin-bottom:8px;'>RAG for Readings</div>
  <div style='color:#B0B8D0;font-size:0.85rem;line-height:1.6;'>
    ChromaDB retrieves relevant astrological knowledge at inference time,
    grounding LLM responses in curated content.
  </div>
</div>""", unsafe_allow_html=True)
    with col6:
        st.markdown("""
<div style='background:#1A1A2E;border:1px solid #5CAE8044;border-radius:10px;padding:16px;height:140px;'>
  <div style='color:#5CAE80;font-weight:700;margin-bottom:8px;'>Free Tier Optimised</div>
  <div style='color:#B0B8D0;font-size:0.85rem;line-height:1.6;'>
    No GPU, no paid DB. In-memory ChromaDB + FakeEmbeddings +
    Groq's free-tier LLM API keeps hosting cost at $0.
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Deployment")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
| Component | Platform | URL |
|---|---|---|
| Streamlit UI | Streamlit Cloud | `*.streamlit.app` |
| FastAPI Backend | Render Free Tier | `astro-world-740v.onrender.com` |
""")
    with c2:
        st.markdown("""
| Config | Value |
|---|---|
| Python version | 3.12 (pinned via `.python-version`) |
| API timeout | 90 s (cold-start buffer) |
| CORS | `allow_origins=["*"]` |
| API docs | `/docs` (Swagger UI) |
""")


# ─────────────────────────────────────────────────────────────────────────────
# TECH STACK
# ─────────────────────────────────────────────────────────────────────────────
def _tech_stack():
    st.markdown("### Tech Stack")

    st.markdown("#### 🖥️ Frontend — Streamlit UI")
    st.markdown("""
| Library | Version | Role |
|---|---|---|
| `streamlit` | 1.40.0 | App framework, routing, session state, UI widgets |
| `requests` | latest | HTTP client for API calls |
| Python | 3.12 | Runtime (pinned via `ui/.python-version`) |
""")

    st.markdown("#### ⚙️ Backend — FastAPI")
    st.markdown("""
| Library | Version | Role |
|---|---|---|
| `fastapi` | latest | REST API framework, Pydantic validation, OpenAPI docs |
| `uvicorn` | latest | ASGI server |
| `pydantic` | v2 | Request/response schema validation |
| `python-dotenv` | latest | Environment variable loading |
| `pytz` | latest | Timezone-aware datetime localisation |
""")

    st.markdown("#### 🔭 Astrology Engine")
    st.markdown("""
| Library | Version | Role |
|---|---|---|
| `kerykeion` | v5 | Swiss Ephemeris wrapper — planetary positions, houses, aspects |
| `pyswisseph` | latest | Underlying ephemeris engine (C library via kerykeion) |
| `matplotlib` | latest | Chart image rendering (South Indian grid + Western wheel) |
""")

    st.markdown("#### 🤖 AI / LLM / RAG")
    st.markdown("""
| Library | Version | Role |
|---|---|---|
| `langchain-groq` | latest | LangChain integration for Groq Cloud LLMs |
| `langchain-community` | latest | `TextLoader`, `FakeEmbeddings` |
| `langchain-chroma` | latest | ChromaDB vector store integration |
| `langchain-text-splitters` | latest | `RecursiveCharacterTextSplitter` for knowledge chunking |
| `chromadb` | latest | In-memory vector database for RAG |
""")

    st.markdown("#### 🌍 Geocoding")
    st.markdown("""
| Library | Version | Role |
|---|---|---|
| `geopy` | latest | Nominatim (OpenStreetMap) geocoding — city → lat/lng/timezone |
| `timezonefinder` | latest | Lat/lng → IANA timezone string |
""")

    st.markdown("#### 🤖 LLM Models (Groq Cloud)")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
<div style='background:#1A1A2E;border:1px solid #C9A96E44;border-radius:10px;padding:16px;'>
  <div style='color:#C9A96E;font-weight:700;font-size:0.95rem;'>llama-3.3-70b-versatile</div>
  <div style='color:#888;font-size:0.78rem;margin:4px 0 10px;'>Used for: AI Readings</div>
  <div style='color:#B0B8D0;font-size:0.85rem;line-height:1.6;'>
    70B parameter model. Deep, nuanced, multi-section personalized readings.
    Temperature: 0.7 — balanced creativity + accuracy.
  </div>
</div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
<div style='background:#1A1A2E;border:1px solid #7B6CF644;border-radius:10px;padding:16px;'>
  <div style='color:#A89CF0;font-weight:700;font-size:0.95rem;'>llama-3.1-8b-instant</div>
  <div style='color:#888;font-size:0.78rem;margin:4px 0 10px;'>Used for: Horoscopes + Compatibility</div>
  <div style='color:#B0B8D0;font-size:0.85rem;line-height:1.6;'>
    8B parameter model. Faster inference for shorter outputs.
    Temperature: 0.8 — more creative/varied tone for daily content.
  </div>
</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# API REFERENCE
# ─────────────────────────────────────────────────────────────────────────────
def _api_reference():
    st.markdown("### API Reference")
    st.markdown(
        "Base URL: `https://astro-world-740v.onrender.com`  |  "
        "[Interactive Swagger Docs →](https://astro-world-740v.onrender.com/docs)"
    )

    st.divider()

    # Health
    with st.expander("**GET /health** — Health check"):
        st.markdown("Returns API status and uptime.")
        st.code("curl https://astro-world-740v.onrender.com/health", language="bash")
        st.code("""{
  "status": "ok",
  "knowledge_base": "loaded"
}""", language="json")

    # Chart
    with st.expander("**POST /api/chart/calculate** — Birth chart calculation"):
        st.markdown("Calculates Vedic + Western birth chart from birth data.")
        st.markdown("**Request body:**")
        st.code("""{
  "name": "Arjun Sharma",
  "date": "1985-03-21",
  "time": "10:30",
  "city": "New Delhi",
  "country": "India",
  "system": "both"
}""", language="json")
        st.markdown("**`system` values:** `both` · `vedic` · `western`")
        st.markdown("**curl:**")
        st.code("""curl -X POST https://astro-world-740v.onrender.com/api/chart/calculate \\
  -H "Content-Type: application/json" \\
  -d '{"name":"Arjun Sharma","date":"1985-03-21","time":"10:30","city":"New Delhi","country":"India","system":"both"}'""", language="bash")
        st.markdown("**Response fields:**")
        st.code("""{
  "birth_info":         { "name", "date", "time", "city", "country", "latitude", "longitude", "timezone", "utc_offset" },
  "vedic_lagna":        "Taurus",
  "vedic_rashi":        "Capricorn",
  "vedic_sun_sign":     "Pisces",
  "nakshatra":          "Uttara Ashadha",
  "nakshatra_pada":     2,
  "nakshatra_lord":     "Sun",
  "dasha":              { "mahadasha_lord", "mahadasha_end", "antardasha_lord", "antardasha_end" },
  "vedic_planets":      [{ "planet", "sign", "house", "degree", "retrograde" }, ...],
  "vedic_chart_image":  "<base64 PNG>",
  "western_sun_sign":   "Aries",
  "western_moon_sign":  "Capricorn",
  "western_rising":     "Gemini",
  "western_planets":    [...],
  "aspects":            [{ "planet1", "planet2", "aspect_type", "orb", "harmony" }, ...],
  "western_chart_image":"<base64 PNG>"
}""", language="json")

    # Reading
    with st.expander("**POST /api/reading/generate** — AI personalized reading"):
        st.markdown("Generates a RAG-augmented LLM reading for the given chart.")
        st.markdown("**Request body:**")
        st.code("""{
  "birth_data": {
    "name": "Arjun Sharma",
    "date": "1985-03-21",
    "time": "10:30",
    "city": "New Delhi",
    "country": "India",
    "system": "both"
  },
  "reading_type": "full"
}""", language="json")
        st.markdown("**`reading_type` values:** `full` · `career` · `love` · `health` · `spiritual`")
        st.markdown("**curl:**")
        st.code("""curl -X POST https://astro-world-740v.onrender.com/api/reading/generate \\
  -H "Content-Type: application/json" \\
  -d '{"birth_data":{"name":"Arjun Sharma","date":"1985-03-21","time":"10:30","city":"New Delhi","country":"India","system":"both"},"reading_type":"full"}'""", language="bash")
        st.markdown("**Response fields:**")
        st.code("""{
  "name":           "Arjun Sharma",
  "reading_type":   "full",
  "key_placements": ["Sun in Pisces", "Moon in Uttara Ashadha", ...],
  "sections": [
    { "title": "PERSONALITY & IDENTITY", "content": "..." },
    { "title": "STRENGTHS & GIFTS",      "content": "..." },
    { "title": "CAREER & PURPOSE",       "content": "..." },
    ...
  ],
  "summary": "..."
}""", language="json")

    # Compatibility
    with st.expander("**POST /api/compatibility/calculate** — Compatibility analysis"):
        st.markdown("Runs Vedic Ashtakoot + Western synastry + AI narrative for two people.")
        st.markdown("**Request body:**")
        st.code("""{
  "person1": { "name": "Priya Nair", "date": "1992-11-05", "time": "14:00", "city": "Mumbai", "country": "India", "system": "both" },
  "person2": { "name": "Rohan Verma", "date": "1989-07-19", "time": "06:45", "city": "Pune",   "country": "India", "system": "both" }
}""", language="json")
        st.markdown("**curl:**")
        st.code("""curl -X POST https://astro-world-740v.onrender.com/api/compatibility/calculate \\
  -H "Content-Type: application/json" \\
  -d '{"person1":{"name":"Priya Nair","date":"1992-11-05","time":"14:00","city":"Mumbai","country":"India","system":"both"},"person2":{"name":"Rohan Verma","date":"1989-07-19","time":"06:45","city":"Pune","country":"India","system":"both"}}'""", language="bash")
        st.markdown("**Response fields:**")
        st.code("""{
  "person1_name":           "Priya Nair",
  "person2_name":           "Rohan Verma",
  "ashtakoot_total":        28.0,
  "ashtakoot_percentage":   77.8,
  "ashtakoot_verdict":      "Excellent",
  "ashtakoot_factors": [
    { "factor": "Nadi", "max_points": 8, "scored": 8.0, "result": "Compatible" },
    ...
  ],
  "mangal_dosha_p1":        false,
  "mangal_dosha_p2":        false,
  "synastry_aspects":       [{ "person1_planet", "person2_planet", "aspect_type", "harmony", "interpretation" }, ...],
  "synastry_harmony_score": 72.0,
  "ai_summary":             "...",
  "ai_strengths":           ["Strong emotional bond", ...],
  "ai_challenges":          ["Different life rhythms", ...]
}""", language="json")

    # Horoscope
    with st.expander("**GET /api/horoscope/{sign}** — Daily / weekly horoscope"):
        st.markdown("Generates an AI horoscope for a zodiac sign.")
        st.markdown("**Path param:** `sign` — e.g. `Aries`, `Taurus`, `Gemini` ...  \n"
                    "**Query params:** `period` (`today` | `week`), `system` (`vedic` | `western` | `both`)")
        st.markdown("**curl:**")
        st.code("""curl "https://astro-world-740v.onrender.com/api/horoscope/Aries?period=today&system=western\"""", language="bash")
        st.code("""{
  "sign":                  "Aries",
  "system":                "western",
  "period":                "today",
  "date":                  "2026-08-06",
  "prediction":            "Today's energy favours bold decisions...",
  "lucky_number":          7,
  "lucky_color":           "Red",
  "lucky_day":             "Tuesday",
  "energy_level":          "High",
  "planetary_influences":  ["Mars trine Sun", "Venus sextile Jupiter"]
}""", language="json")


# ─────────────────────────────────────────────────────────────────────────────
# PIPELINES
# ─────────────────────────────────────────────────────────────────────────────
def _pipelines():
    st.markdown("### Data & Inference Pipelines")

    st.markdown("#### 🪐 Birth Chart Pipeline")
    st.code("""User Input (name, date, time, city, country)
    │
    ▼
[geocode.py] Nominatim OSM → lat, lng, timezone (IANA)
    │
    ▼
[astro_calc.py] kerykeion AstrologicalSubject
    ├── Sidereal (Lahiri)  → Vedic planets, lagna, rashi, moon_longitude
    └── Tropical           → Western planets, sun/moon/rising, aspects
    │
    ▼
[vedic.py]    nakshatra + pada + lord (from moon_longitude 0–360°)
              Vimshottari Dasha (mahadasha + antardasha)
[western.py]  natal aspects (Conjunction/Trine/Square/Opposition/Sextile)
[chart_renderer.py] matplotlib → base64 PNG images
    │
    ▼
ChartResult (Pydantic) → JSON response""", language="text")

    st.divider()

    st.markdown("#### ✨ AI Reading Pipeline (RAG)")
    st.code("""Birth data  →  [Birth Chart Pipeline]  →  ChartResult
    │
    ▼
[ai_reading.py] _key_placements()
    Extract top-10 placements as query string:
    "Sun in Pisces | Moon in Capricorn (Uttara Ashadha) | Lagna in Taurus | ..."
    │
    ▼
[ChromaDB] similarity_search(query, k=10)
    Returns 10 most relevant chunks from knowledge/*.md files
    (FakeEmbeddings — keyword-proximity based, no GPU needed)
    │
    ▼
[Groq LLM] llama-3.3-70b-versatile  (temp=0.7)
    SystemMessage: structured 8-section format prompt
    HumanMessage:  name + placements + reading_focus + retrieved_context
    │
    ▼
[_parse_sections()] regex split on **SECTION TITLE** markers
    │
    ▼
ReadingResult (sections[], summary, key_placements) → JSON""", language="text")

    st.divider()

    st.markdown("#### 💫 Compatibility Pipeline")
    st.code("""Person1 birth data ─┐
                       ├─ [Birth Chart Pipeline × 2] → chart1, chart2
Person2 birth data ─┘
    │
    ▼
[vedic.py] ashtakoot_score(moon_lon1, moon_lon2)
    8 factors: Varna, Vashya, Tara, Yoni, Graha Maitri, Gana, Bhakut, Nadi
    Scores summed → total/36 → verdict (Excellent/Good/Average/Poor)

[vedic.py] has_mangal_dosha(planets)
    Mars in houses 1, 2, 4, 7, 8, 12 → True/False
    │
    ▼
[western.py] synastry_aspects(planets1, planets2)
    Cross-chart aspect calculation for all planet pairs
    orb thresholds: ±8° Conjunction/Opposition/Trine, ±6° Square, ±4° Sextile

[western.py] synastry_harmony_score(aspects)
    Harmonious: +10 pts | Neutral: +5 | Challenging: -3
    Clamped 0–100
    │
    ▼
[ai_reading.py] generate_compatibility_narrative()
    Groq llama-3.1-8b-instant (temp=0.8)
    Input: ashtakoot_score, top harmonious/challenging aspects
    Output: SUMMARY + STRENGTHS (3) + CHALLENGES (2)
    │
    ▼
CompatibilityResult → JSON""", language="text")

    st.divider()

    st.markdown("#### 🔮 Daily Horoscope Pipeline")
    st.code("""GET /api/horoscope/{sign}?period=today&system=western
    │
    ▼
[ChromaDB] similarity_search("{sign} sign traits personality energy", k=4)
    Retrieves 4 relevant chunks about the sign's characteristics
    │
    ▼
[Groq LLM] llama-3.1-8b-instant (temp=0.8)
    SystemMessage: "Write {period}'s horoscope for {sign} ({system})"
    HumanMessage:  sign context + date
    Output: 3-4 sentences (daily) or 5-6 sentences (weekly)
    │
    ▼
[horoscope.py router]
    lucky_number   = hash(sign + date) % 9 + 1
    lucky_color    = deterministic map from sign
    lucky_day      = sign ruling-planet day map
    energy_level   = derived from lunar phase approximation
    │
    ▼
HoroscopeResult → JSON""", language="text")


# ─────────────────────────────────────────────────────────────────────────────
# AI & RAG
# ─────────────────────────────────────────────────────────────────────────────
def _ai_rag():
    st.markdown("### AI & RAG System")

    st.markdown("#### Knowledge Base Construction")
    st.markdown("""
At API startup (`lifespan` hook in `main.py`), **`init_knowledge_base()`** runs once:

1. Loads all `*.md` files from `api/knowledge/`
2. Splits with `RecursiveCharacterTextSplitter` — chunk size 600 chars, overlap 80 chars, splitting on `## `, `---`, `\\n\\n`
3. Creates a **ChromaDB** collection using **FakeEmbeddings** (size=384)

FakeEmbeddings produce deterministic pseudo-random vectors. Because Groq's LLMs are strong reasoners,
the retrieval step mainly serves as context injection rather than semantic ranking — and keyword proximity
is sufficient for the structured astrological knowledge base.
""")

    st.markdown("#### RAG Retrieval Strategy")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
<div style='background:#1A1A2E;border:1px solid #C9A96E44;border-radius:10px;padding:16px;'>
  <div style='color:#C9A96E;font-weight:700;margin-bottom:8px;'>Reading queries (k=10)</div>
  <div style='color:#B0B8D0;font-size:0.85rem;line-height:1.6;'>
    Query = top-10 chart placements joined by <code> | </code><br><br>
    e.g. <em>"Sun in Pisces | Moon in Capricorn (Uttara Ashadha) |
    Lagna in Taurus | Current Dasha: Venus Mahadasha"</em>
  </div>
</div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
<div style='background:#1A1A2E;border:1px solid #7B6CF644;border-radius:10px;padding:16px;'>
  <div style='color:#A89CF0;font-weight:700;margin-bottom:8px;'>Horoscope queries (k=4)</div>
  <div style='color:#B0B8D0;font-size:0.85rem;line-height:1.6;'>
    Query = <code>"{sign} sign traits personality energy"</code><br><br>
    Fewer chunks because the prompt is shorter and the
    LLM adds creative content from its own weights.
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Prompt Architecture")
    st.markdown("""
| Endpoint | Model | Temp | System prompt strategy |
|---|---|---|---|
| `/reading/generate` | llama-3.3-70b-versatile | 0.7 | 8-section structured format, speaks directly to person using "you/your", no disclaimers |
| `/horoscope/{sign}` | llama-3.1-8b-instant | 0.8 | Short-form: date context, tone guide, length constraint (3-4 / 5-6 sentences) |
| `/compatibility/calculate` | llama-3.1-8b-instant | 0.8 | SUMMARY / STRENGTHS / CHALLENGES format, relationship-focused (not individual) |
""")

    st.markdown("#### Why Groq?")
    st.markdown("""
- **Speed** — sub-2s inference on 8B model, ~5s on 70B. Crucial for Render free tier where cold starts already add 30-60s.
- **Cost** — generous free tier. No GPU required on the server.
- **LangChain integration** — `langchain-groq` provides `ChatGroq` which slots directly into the existing LangChain chain.
- **Model quality** — Llama 3.3 70B produces readings comparable to GPT-4o for structured text generation tasks.
""")

    st.markdown("#### Limitations & Future Improvements")
    st.markdown("""
| Current | Improvement |
|---|---|
| FakeEmbeddings (no semantic search) | Replace with `sentence-transformers` or Groq embedding API |
| In-memory ChromaDB (lost on restart) | Persist to disk or use Pinecone/Qdrant |
| No caching of LLM responses | Add Redis or Streamlit `@st.cache_data` for repeated queries |
| Single knowledge base for all queries | Domain-specific collections (Vedic, Western, Compatibility) |
""")


# ─────────────────────────────────────────────────────────────────────────────
# GLOSSARY
# ─────────────────────────────────────────────────────────────────────────────
def _glossary():
    st.markdown("### Glossary")

    tab_vedic, tab_western, tab_tech = st.tabs(["🕉️ Vedic Terms", "⭕ Western Terms", "💻 Tech Terms"])

    with tab_vedic:
        st.markdown("""
| Term | Meaning |
|---|---|
| **Lagna** | Ascendant — the zodiac sign rising on the eastern horizon at birth. Sets the house system. |
| **Rashi** | Moon sign in Vedic astrology (sidereal). More important than Sun sign in Jyotish. |
| **Nakshatra** | Lunar mansion — 27 divisions of the ecliptic (~13.2° each). More granular than the 12 signs. |
| **Pada** | Quarter of a nakshatra — each nakshatra has 4 padas of ~3.3° each. |
| **Ayanamsa** | The angular difference between the tropical and sidereal zodiacs (~23.9° currently). Lahiri is the standard. |
| **Dasha** | Planetary period system. Vimshottari Dasha divides life into 120-year cycles ruled by each planet. |
| **Mahadasha** | Major planetary period (e.g., Venus Mahadasha = 20 years). |
| **Antardasha** | Sub-period within a Mahadasha. Adds another layer of planetary influence. |
| **Ashtakoot** | 8-factor compatibility matching system. Maximum 36 points. |
| **Nadi** | Most important Ashtakoot factor (8 pts). Governs health, genetics, and children. |
| **Bhakut** | Second most important (7 pts). Governs emotional and financial compatibility. |
| **Mangal Dosha** | Mars in houses 1, 2, 4, 7, 8, or 12. Traditionally indicates friction in marriage. Cancelled if both partners have it. |
| **Rahu** | North Lunar Node. Karmic future direction; desires and ambitions. |
| **Ketu** | South Lunar Node. Karmic past; spirituality and detachment. |
| **Gana** | Nature category: Deva (divine), Manav (human), Rakshasa (demon). |
""")

    with tab_western:
        st.markdown("""
| Term | Meaning |
|---|---|
| **Ascendant / Rising** | The zodiac sign on the eastern horizon at birth. Governs appearance and first impressions. |
| **Tropical zodiac** | Zodiac aligned to the seasons (vernal equinox = 0° Aries). Used in Western astrology. |
| **Aspect** | Angular relationship between two planets. Key aspects: Conjunction (0°), Opposition (180°), Trine (120°), Square (90°), Sextile (60°). |
| **Orb** | Allowed deviation from an exact aspect angle. Wider orb = stronger consideration. |
| **Conjunction** | 0° — planets merge energy. Very powerful, can be harmonious or challenging depending on planets involved. |
| **Trine** | 120° — natural flow and harmony. Most beneficial aspect. |
| **Sextile** | 60° — opportunity and cooperation. Gentle harmonious aspect. |
| **Square** | 90° — tension and challenge. Drives action but creates friction. |
| **Opposition** | 180° — polarity and awareness. Can create balance or conflict. |
| **Synastry** | Comparing two birth charts to assess relationship compatibility through inter-chart aspects. |
| **Natal chart** | The birth chart — snapshot of planetary positions at the moment of birth. |
| **House** | 12 divisions of the chart wheel, each governing a life area (identity, money, communication, home...). |
| **Retrograde** | Apparent backward motion of a planet as seen from Earth. Indicates internalization of that planet's energy. |
""")

    with tab_tech:
        st.markdown("""
| Term | Meaning |
|---|---|
| **RAG** | Retrieval-Augmented Generation — retrieving relevant documents from a knowledge base before calling the LLM, to ground responses in curated facts. |
| **ChromaDB** | Open-source in-memory vector database used to store and search knowledge chunks. |
| **FakeEmbeddings** | Deterministic pseudo-random embedding vectors. No semantic meaning but allows ChromaDB to function without a real embedding model. |
| **Embedding** | A numerical vector representation of text. Semantically similar texts have vectors close together in embedding space. |
| **Chunk** | A segment of a longer document produced by a text splitter, sized to fit within LLM context limits. |
| **kerykeion** | Python library wrapping the Swiss Ephemeris for astrological calculations. V5 changed house attributes from `int` to named strings like `"Eighth_House"`. |
| **Swiss Ephemeris** | High-precision planetary position calculation library used by most professional astrology software. |
| **Sidereal** | Zodiac system fixed to actual star positions. Differs from tropical by the ayanamsa (~23.9°). Used in Vedic astrology. |
| **Tropical** | Zodiac system fixed to Earth's seasons. Used in Western astrology. |
| **Lahiri** | Most widely used ayanamsa in Indian Vedic astrology. Also called Chitrapaksha. |
| **Vimshottari** | The most common Dasha system — 120-year cycle with 9 planetary sub-periods based on Moon's nakshatra at birth. |
| **Lifespan hook** | FastAPI's `@asynccontextmanager lifespan` function — runs setup code once at startup before serving requests. |
| **Lazy initialization** | Deferring object creation (e.g., LLM client) until first use, avoiding startup crashes from missing credentials. |
| **Session state** | Streamlit's `st.session_state` dict — persists data across reruns within a single user session. |
| **Cold start** | Render free tier spins down after 15 min inactivity. First request after that triggers a cold start (~30–60s delay). |
""")
