"""
AI Reading Service — RAG + Groq LLM
Builds a ChromaDB knowledge base from knowledge/ markdown files at startup.
Generates personalized astrology readings by:
  1. Retrieving relevant interpretations based on the person's chart
  2. Calling Groq LLM to synthesize a personalized narrative
"""

import os
import re
from pathlib import Path
from typing import Optional

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from models.outputs import ChartResult, ReadingResult, ReadingSection

# ── Module-level state ────────────────────────────────────────────────────────
_knowledge_store: Optional[Chroma] = None
_llm_reading: Optional[ChatGroq] = None
_llm_horoscope: Optional[ChatGroq] = None

KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"


def init_knowledge_base() -> None:
    """
    Called once at API startup (lifespan hook in main.py).
    Loads all knowledge markdown files into ChromaDB.
    """
    global _knowledge_store, _llm_reading, _llm_horoscope

    # Load and chunk knowledge documents
    docs = []
    for md_file in KNOWLEDGE_DIR.glob("*.md"):
        loader = TextLoader(str(md_file), encoding="utf-8")
        docs.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=80,
        separators=["\n## ", "\n---", "\n\n", "\n", " "],
    )
    chunks = splitter.split_documents(docs)

    from langchain_community.embeddings import FakeEmbeddings
    embeddings = FakeEmbeddings(size=384)
    _knowledge_store = Chroma.from_documents(chunks, embeddings)

    groq_key = os.environ.get("GROQ_API_KEY", "")
    _llm_reading   = ChatGroq(model="llama-3.3-70b-versatile",  temperature=0.7, api_key=groq_key)
    _llm_horoscope = ChatGroq(model="llama-3.1-8b-instant",     temperature=0.8, api_key=groq_key)

    print(f"Knowledge base ready — {len(chunks)} chunks from {len(list(KNOWLEDGE_DIR.glob('*.md')))} files.")


def _retrieve(query: str, k: int = 8) -> str:
    """Retrieve k most relevant knowledge chunks and return as a single context string."""
    if _knowledge_store is None:
        return ""
    results = _knowledge_store.similarity_search(query, k=k)
    return "\n\n---\n\n".join(r.page_content for r in results)


def _key_placements(chart: ChartResult) -> list[str]:
    """Extract the most important placements for the retrieval query."""
    placements = [
        f"Sun in {chart.vedic_sun_sign}",
        f"Moon in {chart.vedic_rashi} (Nakshatra: {chart.nakshatra})",
        f"Lagna (Ascendant) in {chart.vedic_lagna}",
        f"Western Sun in {chart.western_sun_sign}",
        f"Western Moon in {chart.western_moon_sign}",
        f"Western Rising in {chart.western_rising}",
        f"Current Dasha: {chart.dasha.mahadasha_lord} Mahadasha",
    ]
    # Add any planets in important houses
    for p in chart.vedic_planets:
        if p.house in (1, 7, 10) and p.planet not in ("Rahu", "Ketu"):
            placements.append(f"{p.planet} in house {p.house} ({p.sign})")
    return placements[:10]


READING_PROMPTS = {
    "full": "Provide a comprehensive reading covering personality, life path, career potential, relationships, health, and spiritual growth.",
    "career": "Focus exclusively on career, professional strengths, ideal work environment, challenges, and upcoming opportunities.",
    "love": "Focus on love life, relationship style, what they seek in a partner, compatibility patterns, and current relationship energy.",
    "health": "Focus on health tendencies, areas that need attention, mental and emotional wellbeing, and lifestyle recommendations.",
    "spiritual": "Focus on spiritual path, karmic lessons, past life themes indicated by Ketu/South Node, dharma (life purpose), and spiritual practices suited to this chart.",
}


def generate_reading(chart: ChartResult, reading_type: str = "full") -> ReadingResult:
    """Generate a personalized astrology reading using RAG + Groq LLM."""
    if _llm_reading is None:
        raise RuntimeError("Knowledge base not initialized. Call init_knowledge_base() first.")

    placements = _key_placements(chart)
    query = " | ".join(placements)
    context = _retrieve(query, k=10)

    focus = READING_PROMPTS.get(reading_type, READING_PROMPTS["full"])

    system_msg = SystemMessage(content="""You are an expert astrologer with deep knowledge of both Vedic (Jyotish) and Western astrology.
You write personalized, insightful readings that are warm, specific, and actionable.
Format your response as clearly labelled sections using this exact structure:

**PERSONALITY & IDENTITY**
[2-3 paragraphs]

**STRENGTHS & GIFTS**
[2-3 paragraphs]

**CHALLENGES & GROWTH AREAS**
[1-2 paragraphs]

**RELATIONSHIPS & LOVE**
[1-2 paragraphs]

**CAREER & PURPOSE**
[1-2 paragraphs]

**CURRENT PHASE (Dasha)**
[1-2 paragraphs about the current planetary period]

**SPIRITUAL PATH**
[1-2 paragraphs]

**SUMMARY**
[2-3 key sentences summary]

Use the astrological context provided. Speak directly to the person using "you" and "your".
Be specific — reference actual placements. Avoid generic horoscope language.
Do NOT include any disclaimers or "this is not professional advice" statements.""")

    human_msg = HumanMessage(content=f"""Name: {chart.birth_info.name}

KEY CHART PLACEMENTS:
{chr(10).join(f"• {p}" for p in placements)}

READING FOCUS: {focus}

ASTROLOGICAL KNOWLEDGE BASE (retrieved context):
{context}

Please write the personalized reading now.""")

    response = _llm_reading.invoke([system_msg, human_msg])
    raw = response.content.strip()

    sections = _parse_sections(raw)
    summary  = next((s.content[:300] for s in sections if s.title == "SUMMARY"), raw[:300])

    return ReadingResult(
        name=chart.birth_info.name,
        reading_type=reading_type,
        key_placements=placements,
        sections=sections,
        summary=summary,
    )


def _parse_sections(text: str) -> list[ReadingSection]:
    """Parse the LLM response into structured ReadingSection objects."""
    sections = []
    pattern = r"\*\*([A-Z &/()]+)\*\*\n([\s\S]*?)(?=\n\*\*[A-Z]|\Z)"
    matches = re.findall(pattern, text)

    if matches:
        for title, content in matches:
            sections.append(ReadingSection(
                title=title.strip(),
                content=content.strip(),
            ))
    else:
        # Fallback: return as single section
        sections.append(ReadingSection(title="YOUR READING", content=text))

    return sections


def generate_horoscope(sign: str, system: str, period: str) -> str:
    """Generate a daily or weekly horoscope for a sign."""
    if _llm_horoscope is None:
        raise RuntimeError("Knowledge base not initialized.")

    from datetime import date
    today = date.today().strftime("%B %d, %Y")

    context = _retrieve(f"{sign} sign traits personality energy", k=4)

    period_text = "today" if period == "today" else "this week"
    system_str  = "Vedic (Moon sign based)" if system == "vedic" else "Western (Sun sign based)"

    system_msg = SystemMessage(content=f"""You are a skilled astrologer writing {period_text}'s horoscope for {sign} ({system_str}).
Write in a warm, encouraging, and specific tone.
Keep it to 3-4 sentences for daily, 5-6 sentences for weekly.
Include: overall energy, what to focus on, what to be mindful of, and one practical tip.
Date context: {today}. Do NOT include disclaimers.""")

    human_msg = HumanMessage(content=f"""Write {period_text}'s horoscope for {sign} ({system_str}).

Sign characteristics context:
{context}

Write the horoscope now:""")

    response = _llm_horoscope.invoke([system_msg, human_msg])
    return response.content.strip()


def generate_compatibility_narrative(
    name1: str,
    name2: str,
    ashtakoot_score: float,
    synastry_aspects: list[dict],
) -> tuple[str, list[str], list[str]]:
    """Generate AI compatibility summary, strengths, and challenges."""
    if _llm_horoscope is None:
        raise RuntimeError("Knowledge base not initialized.")

    harmonious = [a for a in synastry_aspects if a["harmony"] == "Harmonious"]
    challenging = [a for a in synastry_aspects if a["harmony"] == "Challenging"]

    system_msg = SystemMessage(content="""You are an expert astrologer specializing in relationship compatibility.
Write a warm, balanced, and honest compatibility summary.
Return your response in this exact format:

SUMMARY:
[2-3 sentences overall assessment]

STRENGTHS:
• [strength 1]
• [strength 2]
• [strength 3]

CHALLENGES:
• [challenge 1]
• [challenge 2]

Be specific. Reference actual aspects. Speak about the relationship, not the individuals separately.""")

    human_msg = HumanMessage(content=f"""Compatibility analysis for {name1} and {name2}:

VEDIC ASHTAKOOT SCORE: {ashtakoot_score}/36

HARMONIOUS ASPECTS:
{chr(10).join(f"• {a['person1_planet']}–{a['person2_planet']} {a['aspect_type']}: {a['interpretation']}" for a in harmonious[:5])}

CHALLENGING ASPECTS:
{chr(10).join(f"• {a['person1_planet']}–{a['person2_planet']} {a['aspect_type']}: {a['interpretation']}" for a in challenging[:3])}

Write the compatibility analysis:""")

    response = _llm_horoscope.invoke([system_msg, human_msg])
    raw = response.content.strip()

    # Parse
    summary_match    = re.search(r"SUMMARY:\s*([\s\S]*?)(?=STRENGTHS:|$)", raw)
    strengths_match  = re.search(r"STRENGTHS:\s*([\s\S]*?)(?=CHALLENGES:|$)", raw)
    challenges_match = re.search(r"CHALLENGES:\s*([\s\S]*?)$", raw)

    summary    = summary_match.group(1).strip() if summary_match else raw[:200]
    strengths  = [s.strip("• ").strip() for s in (strengths_match.group(1).strip().split("\n") if strengths_match else [])]
    challenges = [s.strip("• ").strip() for s in (challenges_match.group(1).strip().split("\n") if challenges_match else [])]

    strengths  = [s for s in strengths  if s][:3]
    challenges = [s for s in challenges if s][:2]

    return summary, strengths, challenges
