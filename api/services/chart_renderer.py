"""
Chart rendering service.
Produces base64-encoded PNG images for:
  1. South Indian Vedic Kundali (fixed sign grid, 4x4)
  2. Western circular natal wheel

Both are rendered with matplotlib using the dark cosmic theme.
"""

import base64
import io
import math
import matplotlib
matplotlib.use("Agg")   # non-interactive backend for server
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from models.outputs import PlanetPosition, AspectInfo


# ── Theme colours ──────────────────────────────────────────────────────────────
BG      = "#0D0D1A"
CARD    = "#1A1A2E"
GOLD    = "#C9A96E"
SILVER  = "#B0B8D0"
WHITE   = "#E8E8F0"
ACCENT  = "#7B6CF6"
RED     = "#E05C5C"
GREEN   = "#5CAE80"

# Planet symbols (Unicode)
PLANET_SYMBOLS = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂",
    "Jupiter": "♃", "Saturn": "♄", "Uranus": "⛢", "Neptune": "♆", "Pluto": "♇",
    "Rahu": "☊", "Ketu": "☋",
}

# Sign abbreviations for South Indian grid (fixed positions)
SIGN_ABBR = [
    "Ari", "Tau", "Gem", "Can",
    "Leo", "Vir", "Lib", "Sco",
    "Sag", "Cap", "Aqu", "Pis",
]

# South Indian grid: row, col for each sign (0-indexed, 4×4 outer ring)
# Signs are fixed in cells; houses rotate based on Lagna
SOUTH_GRID_POS = {
    "Pis": (0, 0), "Ari": (0, 1), "Tau": (0, 2), "Gem": (0, 3),
    "Aqu": (1, 0),                                "Can": (1, 3),
    "Cap": (2, 0),                                "Leo": (2, 3),
    "Sag": (3, 0), "Sco": (3, 1), "Lib": (3, 2), "Vir": (3, 3),
}


def _fig_to_b64(fig) -> str:
    """Convert a matplotlib Figure to a base64-encoded PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    buf.seek(0)
    data = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return data


def render_south_indian_chart(planets: list[PlanetPosition], lagna_sign: str) -> str:
    """
    South Indian Kundali — fixed 4×4 grid.
    Signs are fixed in cells; planets placed in their sign cell.
    Lagna sign is marked with 'L'.
    """
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_facecolor(BG)
    fig.patch.set_facecolor(BG)
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_aspect("equal")
    ax.axis("off")

    # Title
    ax.text(2, 4.3, "Vedic Birth Chart (South Indian)",
            color=GOLD, ha="center", va="bottom", fontsize=11, fontweight="bold")

    # Group planets by sign
    sign_planets: dict[str, list[str]] = {}
    for p in planets:
        abbr = p.sign[:3].capitalize()
        sym  = PLANET_SYMBOLS.get(p.planet, p.planet[:2])
        retro = "ᴿ" if p.retrograde else ""
        sign_planets.setdefault(abbr, []).append(f"{sym}{retro}")

    # Draw all 12 outer cells + center 2×2 (blank/title area)
    for sign_full, (row, col) in SOUTH_GRID_POS.items():
        abbr = sign_full[:3]
        x, y = col, 3 - row   # matplotlib y=0 is bottom

        # Draw cell box
        rect = FancyBboxPatch(
            (x + 0.03, y + 0.03), 0.94, 0.94,
            boxstyle="round,pad=0.02",
            linewidth=1.0,
            edgecolor=GOLD if abbr == lagna_sign[:3].capitalize() else SILVER,
            facecolor=CARD,
        )
        ax.add_patch(rect)

        # Sign label (top-left of cell)
        is_lagna = abbr == lagna_sign[:3].capitalize()
        label = f"{abbr}" + (" ©" if is_lagna else "")
        ax.text(x + 0.08, y + 0.88, label,
                color=GOLD if is_lagna else SILVER,
                ha="left", va="top", fontsize=7.5, fontweight="bold")

        # Planet symbols
        plist = sign_planets.get(abbr, [])
        if plist:
            ax.text(x + 0.5, y + 0.45, "  ".join(plist),
                    color=WHITE, ha="center", va="center", fontsize=8.5)

    # Center 2×2 — chart name / blank
    for r in range(1, 3):
        for c in range(1, 3):
            rect = FancyBboxPatch(
                (c + 0.03, (3 - r) + 0.03), 0.94, 0.94,
                boxstyle="round,pad=0.02",
                linewidth=0.5, edgecolor=ACCENT, facecolor=BG,
            )
            ax.add_patch(rect)

    ax.text(2, 2, "♈\nKundali", color=ACCENT,
            ha="center", va="center", fontsize=10, alpha=0.5)

    return _fig_to_b64(fig)


def render_western_wheel(planets: list[PlanetPosition], aspects: list[AspectInfo]) -> str:
    """
    Western circular natal wheel.
    Houses represented as 30° segments; planets placed on the wheel.
    Key aspects drawn as lines inside the wheel.
    """
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_facecolor(BG)
    fig.patch.set_facecolor(BG)
    ax.set_xlim(-1.6, 1.6)
    ax.set_ylim(-1.6, 1.6)
    ax.set_aspect("equal")
    ax.axis("off")

    ax.set_title("Western Natal Chart", color=GOLD, fontsize=11, fontweight="bold", pad=8)

    # Outer circle
    outer = plt.Circle((0, 0), 1.4, color=CARD, ec=GOLD, lw=1.5, zorder=1)
    inner = plt.Circle((0, 0), 1.0, color=BG,   ec=SILVER, lw=0.8, zorder=2)
    hub   = plt.Circle((0, 0), 0.35, color=CARD, ec=ACCENT, lw=0.8, zorder=3)
    ax.add_patch(outer)
    ax.add_patch(inner)
    ax.add_patch(hub)

    # 12 house dividers (30° each, starting from Aries = 0°)
    for h in range(12):
        angle = math.radians(h * 30)
        ax.plot([1.0 * math.cos(angle), 1.4 * math.cos(angle)],
                [1.0 * math.sin(angle), 1.4 * math.sin(angle)],
                color=SILVER, lw=0.5, alpha=0.6, zorder=2)
        # Sign label in outer ring
        mid_angle = math.radians(h * 30 + 15)
        ax.text(1.22 * math.cos(mid_angle), 1.22 * math.sin(mid_angle),
                SIGN_ABBR[h], color=GOLD, ha="center", va="center",
                fontsize=7, fontweight="bold")

    # Planet positions
    planet_positions_rad: dict[str, float] = {}
    for p in planets:
        sign_idx = next(
            (i for i, s in enumerate(["Ari","Tau","Gem","Can","Leo","Vir",
                                       "Lib","Sco","Sag","Cap","Aqu","Pis"])
             if s == p.sign[:3].capitalize()), 0)
        angle_deg = sign_idx * 30 + p.degree
        angle_rad = math.radians(angle_deg)
        planet_positions_rad[p.planet] = angle_rad

        r = 1.12
        sym = PLANET_SYMBOLS.get(p.planet, p.planet[:2])
        ax.text(r * math.cos(angle_rad), r * math.sin(angle_rad),
                sym, color=WHITE, ha="center", va="center", fontsize=10, zorder=5)
        # Dot on inner circle edge
        ax.plot(1.0 * math.cos(angle_rad), 1.0 * math.sin(angle_rad),
                "o", color=ACCENT, ms=3, zorder=4)

    # Aspect lines inside the wheel
    ASPECT_COLORS = {
        "Trine": GREEN, "Sextile": GREEN,
        "Square": RED,  "Opposition": RED,
        "Conjunction": ACCENT,
    }
    for asp in aspects[:8]:   # draw top 8 aspects only
        a1 = planet_positions_rad.get(asp.planet1)
        a2 = planet_positions_rad.get(asp.planet2)
        if a1 is not None and a2 is not None:
            col = ASPECT_COLORS.get(asp.aspect_type, SILVER)
            ax.plot([0.9 * math.cos(a1), 0.9 * math.cos(a2)],
                    [0.9 * math.sin(a1), 0.9 * math.sin(a2)],
                    color=col, lw=0.8, alpha=0.6, zorder=3)

    # Hub label
    ax.text(0, 0, "☉", color=GOLD, ha="center", va="center", fontsize=16, zorder=6)

    return _fig_to_b64(fig)
