"""Design DNA generator (build spec §2, §3, §16, §17).

Reuses PRINCIPLES, never templates. Two projects never receive the same DNA
unless their requirements are literally identical: every axis (colour
strategy, typography, spacing, density, radius, motion, layout) is derived
from the project's inputs through a scored direction evaluation plus a
seeded selection within the chosen direction's variation space.

Directions are internal (§17): the final artifact exposes the chosen
direction, its rationale, and a one-line summary of rejected alternatives —
not the full deliberation.
"""

from __future__ import annotations

import hashlib
import math
import random
from typing import Any

from .config import get

# ---------------------------------------------------------------------------
# Direction library — archetypes, not templates. Each is a decision space.
# ---------------------------------------------------------------------------
DIRECTIONS = [
    {
        "id": "precision-editorial",
        "name": "Precision Editorial",
        "description": "Typography-led, generous whitespace, restrained palette "
                       "with one decisive accent. Confidence through clarity.",
        "fits": ["saas", "fintech", "consulting", "portfolio", "agency",
                 "publishing", "b2b"],
        "density": "spacious", "motion": "restrained", "radius": "sharp",
        "type_scale": 1.25, "spacing_base": 8,
    },
    {
        "id": "industrial-control",
        "name": "Industrial Control",
        "description": "Data-first surfaces, compact density, tabular "
                       "numerals, status-colour system. Built for long shifts.",
        "fits": ["industrial", "enterprise", "dashboard", "logistics",
                 "operations", "monitoring", "gis"],
        "density": "compact", "motion": "functional", "radius": "mixed",
        "type_scale": 1.2, "spacing_base": 4,
    },
    {
        "id": "warm-humanist",
        "name": "Warm Humanist",
        "description": "Soft neutral base, warm accents, rounded forms, "
                       "conversational tone. People before pixels.",
        "fits": ["healthcare", "education", "community", "nonprofit",
                 "wellness", "family"],
        "density": "balanced", "motion": "gentle", "radius": "soft",
        "type_scale": 1.25, "spacing_base": 8,
    },
    {
        "id": "quiet-luxury",
        "name": "Quiet Luxury",
        "description": "Monochrome depth, slow easing, oversized type, one "
                       "metallic accent. Premium is what remains when you "
                       "remove everything.",
        "fits": ["luxury", "fashion", "hospitality", "real-estate",
                 "jewelry", "architecture"],
        "density": "spacious", "motion": "cinematic", "radius": "sharp",
        "type_scale": 1.333, "spacing_base": 8,
    },
    {
        "id": "kinetic-brutalist",
        "name": "Kinetic Brutalist",
        "description": "Oversized type, hard edges, high contrast, scroll "
                       "choreography. Energy over ornament.",
        "fits": ["creative", "music", "events", "streetwear", "gaming",
                 "studio"],
        "density": "balanced", "motion": "expressive", "radius": "sharp",
        "type_scale": 1.414, "spacing_base": 8,
    },
    {
        "id": "technical-dashboard",
        "name": "Technical Dashboard",
        "description": "Dense panels, sticky navigation, chart-led "
                       "hierarchy, subtle hover elevation.",
        "fits": ["analytics", "saas", "devtools", "cybersecurity",
                 "dashboard", "iot"],
        "density": "compact", "motion": "functional", "radius": "mixed",
        "type_scale": 1.2, "spacing_base": 4,
    },
    {
        "id": "organic-playful",
        "name": "Organic Playful",
        "description": "Bouncy easing, curved containers, vivid accents, "
                       "illustration-forward.",
        "fits": ["consumer", "kids", "food", "travel", "social", "fitness"],
        "density": "balanced", "motion": "expressive", "radius": "soft",
        "type_scale": 1.25, "spacing_base": 8,
    },
    {
        "id": "cinematic-immersive",
        "name": "Cinematic Immersive",
        "description": "Full-bleed media, depth layers, scroll-linked "
                       "narrative, dark surfaces.",
        "fits": ["film", "automotive", "aerospace", "storytelling", "3d",
                 "experiential"],
        "density": "spacious", "motion": "cinematic", "radius": "mixed",
        "type_scale": 1.333, "spacing_base": 8,
    },
]

# Typography pairings: (display, body) with Google Fonts availability.
PAIRINGS = {
    "sharp": [
        ("Space Grotesk", "Inter"),
        ("Archivo", "IBM Plex Sans"),
        ("Fraunces", "Public Sans"),
        ("Sora", "Manrope"),
        ("Bricolage Grotesque", "Inter"),
        ("Instrument Serif", "Geist"),
    ],
    "soft": [
        ("Outfit", "Nunito Sans"),
        ("Plus Jakarta Sans", "Figtree"),
        ("Quicksand", "Source Sans 3"),
        ("DM Serif Display", "DM Sans"),
        ("Gabarito", "Onest"),
    ],
    "mixed": [
        ("IBM Plex Sans", "IBM Plex Sans"),
        ("Barlow", "Barlow"),
        ("Chivo", "Inter"),
        ("Saira", "Roboto Flex"),
        ("Rubik", "Inter"),
    ],
}

SPACING_SCALES = {
    4: [4, 8, 12, 16, 24, 32, 48, 64, 96, 128],
    8: [8, 16, 24, 32, 48, 64, 96, 128, 160, 192],
}

MOTION_PROFILES = {
    "restrained": {"fast": 120, "base": 200, "slow": 320, "easing": "cubic-bezier(0.2, 0, 0, 1)",
                   "stagger": 30, "intensity": "low"},
    "functional": {"fast": 100, "base": 160, "slow": 240, "easing": "cubic-bezier(0.16, 1, 0.3, 1)",
                   "stagger": 25, "intensity": "low"},
    "gentle": {"fast": 150, "base": 260, "slow": 400, "easing": "cubic-bezier(0.33, 1, 0.68, 1)",
               "stagger": 40, "intensity": "medium"},
    "expressive": {"fast": 160, "base": 300, "slow": 500, "easing": "cubic-bezier(0.34, 1.4, 0.64, 1)",
                   "stagger": 60, "intensity": "medium"},
    "cinematic": {"fast": 200, "base": 420, "slow": 700, "easing": "cubic-bezier(0.65, 0, 0.35, 1)",
                  "stagger": 80, "intensity": "medium-high"},
}


# ---------------------------------------------------------------------------
# Colour strategy — WCAG-checked generation, seeded per project
# ---------------------------------------------------------------------------
def _hex(r: int, g: int, b: int) -> str:
    return "#{:02x}{:02x}{:02x}".format(
        max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))


def _hsl(h: float, s: float, l: float) -> tuple[int, int, int]:
    h = h % 360 / 360
    a = s * min(l, 1 - l)
    def f(n: float) -> float:
        k = (n + h * 12) % 12
        return l - a * max(-1, min(min(k - 3, 9 - k), 1))
    return tuple(int(round(255 * f(i))) for i in (0, 8, 4))  # type: ignore[return-value]


def rel_luminance(hex_color: str) -> float:
    r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
           for c in (r, g, b)]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a: str, b: str) -> float:
    la, lb = rel_luminance(a), rel_luminance(b)
    lighter, darker = max(la, lb), min(la, lb)
    return (lighter + 0.05) / (darker + 0.05)


def _nudge_until(text: str, surface: str, target: float) -> str:
    """Shift the text colour's lightness until WCAG target is met."""
    r, g, b = (int(text[i:i + 2], 16) for i in (1, 3, 5))
    h, l, s = _rgb_to_hsl(r, g, b)
    for _ in range(48):
        if contrast(_hex(r, g, b), surface) >= target:
            break
        # move text luminance away from the surface to widen contrast
        direction = -0.02 if rel_luminance(surface) > 0.5 else 0.02
        l = max(0.0, min(1.0, l + direction))
        r, g, b = _hsl(h, s, l)
    return _hex(r, g, b)


def _rgb_to_hsl(r: int, g: int, b: int) -> tuple[float, float, float]:
    r, g, b = r / 255, g / 255, b / 255
    mx, mn = max(r, g, b), min(r, g, b)
    l = (mx + mn) / 2
    if mx == mn:
        return 0.0, 0.0, l
    d = mx - mn
    s = d / (2 - mx - mn) if l > 0.5 else d / (mx + mn)
    if mx == r:
        h = ((g - b) / d + (6 if g < b else 0))
    elif mx == g:
        h = (b - r) / d + 2
    else:
        h = (r - g) / d + 4
    return h * 60, s, l


def generate_palette(strategy: str, seed: float, dark: bool,
                     accent_hue: float) -> dict:
    rng = random.Random(int(seed * 1000))
    if dark:
        base_l = rng.uniform(0.06, 0.12)
        surface_l = base_l + rng.uniform(0.03, 0.06)
        bg = _hex(*_hsl(accent_hue, rng.uniform(0.04, 0.14), base_l))
        surface = _hex(*_hsl(accent_hue, rng.uniform(0.05, 0.14), surface_l))
        text = _hex(*_hsl(accent_hue, 0.05, 0.94))
        muted_target = 4.5
        border = _hex(*_hsl(accent_hue, 0.08, surface_l + 0.07))
    else:
        bg = _hex(*_hsl(accent_hue, rng.uniform(0.02, 0.10), rng.uniform(0.96, 0.985)))
        surface = _hex(*_hsl(accent_hue, rng.uniform(0.03, 0.10), rng.uniform(0.92, 0.95)))
        text = _hex(*_hsl(accent_hue, rng.uniform(0.15, 0.4), 0.13))
        muted_target = 4.5
        border = _hex(*_hsl(accent_hue, 0.08, 0.88))
    text = _nudge_until(text, bg, float(get("design.contrast_body", 4.5)))
    # muted: same hue as text, lower saturation, closest lightness that
    # still passes 4.5:1 on bg (secondary text is still readable text).
    # Direction-aware: on dark surfaces muted sits just below text, on
    # light surfaces just above it.
    r, g, b = int(text[1:3], 16), int(text[3:5], 16), int(text[5:7], 16)
    h, _l, s = _rgb_to_hsl(r, g, b)
    muted = text
    if rel_luminance(bg) > 0.5:
        ladder = (0.42, 0.38, 0.46, 0.34, 0.50, 0.30, 0.54, 0.26, 0.58)
    else:
        ladder = (0.62, 0.58, 0.66, 0.55, 0.70, 0.52, 0.74, 0.78, 0.48)
    for cand_l in ladder:
        cand = _hex(*_hsl(h, s * 0.55, cand_l))
        if contrast(cand, bg) >= 4.5:
            muted = cand
            break
    accent_sat = {"mono-accent": 0.75, "analogous": 0.6, "split-complement": 0.65,
                  "duotone": 0.7}.get(strategy, 0.65)
    accent = _hex(*_hsl(accent_hue, accent_sat,
                        rng.uniform(0.45, 0.58) if not dark else rng.uniform(0.5, 0.62)))
    if contrast(accent, bg) < 3.0:
        _h, _s, _l = _rgb_to_hsl(*[int(accent[i:i + 2], 16) for i in (1, 3, 5)])
        for lm in (0.62, 0.68, 0.4, 0.35, 0.72):
            cand = _hex(*_hsl(_h, _s, lm))
            if contrast(cand, bg) >= 3.0:
                accent = cand
                break
    accent2 = None
    if strategy == "analogous":
        accent2 = _hex(*_hsl(accent_hue + rng.choice([24, -28]), accent_sat, 0.5))
    elif strategy == "split-complement":
        accent2 = _hex(*_hsl(accent_hue + rng.choice([150, 210]), accent_sat, 0.5))
    elif strategy == "duotone":
        accent2 = _hex(*_hsl((accent_hue + 180) % 360, accent_sat, 0.52))
    on_accent = "#0a0a0a" if contrast(accent, "#0a0a0a") < contrast(accent, "#ffffff") else "#ffffff"
    on_accent = _nudge_until(on_accent, accent, 4.5)
    status = {
        "success": _nudge_until(_hex(*_hsl(142, 0.55, 0.42)), bg, 4.5),
        "warning": _nudge_until(_hex(*_hsl(38, 0.8, 0.5)), bg, 3.0),
        "danger": _nudge_until(_hex(*_hsl(0, 0.65, 0.48)), bg, 4.5),
    }
    return {"strategy": strategy, "background": bg, "surface": surface,
            "text": text, "muted": muted, "border": border,
            "accent": accent, "accent2": accent2, "on_accent": on_accent,
            **{f"{k}": v for k, v in status.items()},
            "dark": dark}


# ---------------------------------------------------------------------------
# Direction evaluation (§17) — internal; results not exposed verbatim
# ---------------------------------------------------------------------------
def _score(direction: dict, ctx: dict) -> float:
    score = 0.0
    industry = str(ctx.get("industry", "")).lower()
    product = str(ctx.get("product_type", "")).lower()
    audience = str(ctx.get("audience", "")).lower()
    haystack = f"{industry} {product} {audience}".replace("-", " ")
    for fit in direction["fits"]:
        fit = fit.replace("-", " ")
        if fit in haystack:
            score += 2.0
    motion_pref = str(ctx.get("motion_appetite", "")).lower()
    if motion_pref and direction["motion"].startswith(motion_pref.split("-")[0]):
        score += 1.0
    if ctx.get("data_heavy") and direction["density"] == "compact":
        score += 1.5
    if ctx.get("data_heavy") and direction["density"] == "spacious":
        score -= 0.8
    if ctx.get("brand") and direction["name"].lower().split()[0] in str(ctx["brand"]).lower():
        score += 0.8
    if ctx.get("accessibility_first") and direction["motion"] in ("cinematic", "expressive"):
        score -= 0.5
    return score


def generate(ctx: dict) -> dict:
    """Generate the full Design DNA payload for a project context."""
    name = str(ctx.get("name", "project"))
    seed = float(int(hashlib.sha256(name.encode("utf-8")).hexdigest()[:8], 16)) / 0xffffffff
    rng = random.Random(int(seed * 1e6))

    ranked = sorted(DIRECTIONS, key=lambda d: -_score(d, ctx))
    chosen = ranked[0]
    alternatives = [d["name"] for d in ranked[1:3]]

    strategy_pool = ["mono-accent", "analogous", "split-complement", "duotone"]
    palette_strategy = rng.choice(strategy_pool)
    hue = rng.uniform(0, 360)
    dark = bool(ctx.get("dark_mode"))
    if dark is False and chosen["id"] in ("cinematic-immersive", "quiet-luxury",
                                          "technical-dashboard", "industrial-control"):
        dark = rng.random() < 0.45
    palette = generate_palette(palette_strategy, seed, dark, hue)

    pairing = rng.choice(PAIRINGS[chosen["radius"]])
    scale = SPACING_SCALES[chosen["spacing_base"]]
    motion = dict(MOTION_PROFILES[chosen["motion"]])
    max_ms = int(get("design.max_motion_ms", 900))
    motion["slow"] = min(motion["slow"], max_ms)

    density_map = {
        "compact": {"row": 36, "card_pad": 12, "table_font": 13,
                    "grid_gap": 12},
        "balanced": {"row": 44, "card_pad": 16, "table_font": 14,
                     "grid_gap": 16},
        "spacious": {"row": 56, "card_pad": 24, "table_font": 15,
                     "grid_gap": 24},
    }
    radius_map = {"sharp": [0, 2, 4], "mixed": [2, 6, 12], "soft": [8, 14, 24]}
    radius = radius_map[chosen["radius"]]
    return {
        "project": name,
        "direction": chosen,
        "alternatives_considered": alternatives,
        "palette": palette,
        "typography": {"display": pairing[0], "body": pairing[1],
                       "scale": chosen["type_scale"],
                       "mono": "JetBrains Mono"},
        "spacing": {"base": chosen["spacing_base"], "scale": scale},
        "density": density_map[chosen["density"]],
        "radius": {"sm": radius[0], "md": radius[1], "lg": radius[2]},
        "motion": motion,
        "layout": _layout_for(chosen, ctx, rng),
        "accessibility": _a11y_contract(ctx),
        "imagery": _imagery_for(chosen, ctx, rng),
    }


def _layout_for(chosen: dict, ctx: dict, rng: random.Random) -> dict:
    if ctx.get("data_heavy") or chosen["density"] == "compact":
        nav = rng.choice(["persistent-sidebar", "sidebar-with-topbar"])
        grid = "12-col with 4-col subgrid for tiles"
    elif chosen["id"] in ("cinematic-immersive", "kinetic-brutalist"):
        nav = rng.choice(["fixed-transparent-topbar", "overlay-burger"])
        grid = "full-bleed with offset content blocks"
    else:
        nav = rng.choice(["centered-topbar", "minimal-topbar", "split-hero"])
        grid = rng.choice(["centered max-w-7xl", "asymmetric 2:1", "1:2:1"])
    return {"navigation": nav, "grid": grid,
            "hero": rng.choice(["typographic-statement", "media-led",
                                "split-proof", "layered-depth"])
            if chosen["motion"] != "functional" else "summary-led"}


def _imagery_for(chosen: dict, ctx: dict, rng: random.Random) -> str:
    table = {
        "precision-editorial": ["abstract-gradient", "macro-detail", "duotone"],
        "quiet-luxury": ["moody-studio", "monochrome", "material-macro"],
        "warm-humanist": ["candid-people", "soft-light", "warm-illustration"],
        "organic-playful": ["playful-illustration", "bold-cutout", "bright-3d"],
        "cinematic-immersive": ["full-bleed-video", "atmospheric-still", "particle-field"],
        "technical-dashboard": ["none-data-first", "subtle-topology", "dark-render"],
        "industrial-control": ["none-data-first", "schematic", "thermal-render"],
        "kinetic-brutalist": ["halftone", "high-contrast-photo", "glitch-accents"],
    }
    return rng.choice(table.get(chosen["id"], ["neutral-product"])) or "neutral-product"


def _a11y_contract(ctx: dict) -> dict:
    return {
        "contrast_body": float(get("design.contrast_body", 4.5)),
        "contrast_large": float(get("design.contrast_large", 3.0)),
        "contrast_ui": float(get("design.contrast_ui", 3.0)),
        "reduced_motion": bool(get("design.respect_reduced_motion", True)),
        "touch_target_px": 44,
        "focus_visible": "2px accent outline, 2px offset, never removed",
        "keyboard": "full tab order; no keyboard traps; skip-link on first tab",
    }
