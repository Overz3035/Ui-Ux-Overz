"""Deterministic, descriptive filename generation (build spec §11).

Examples produced:
  dashboard-data-dense-sidebar-table-001.png
  landing-asymmetric-hero-editorial-002.png
  motion-scroll-parallax-card-reveal-002.mp4

The original filename is never lost: it is stored in the index and in the
asset's YAML front-matter / sidecar. Rename targets live only under
REFERENCES/; INBOX originals are never touched.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

_ORDER = {
    "ui_category": ("dashboard", "landing", "table", "mobile", "form",
                    "editorial", "ecommerce", "map_gis", "chat_ai", "social",
                    "three_d_scene", "media_player", "component",
                    "presentation", "misc"),
    "layout": ("asymmetric_editorial", "bento_grid", "sidebar_content",
               "split_screen", "centered_single_column", "card_grid",
               "dense_table", "full_bleed_media", "overlay_hud",
               "stacked_mobile"),
    "style": ("data_dense", "editorial_typographic", "minimal_spacious",
              "dark_ui", "light_ui", "high_contrast", "muted_neutral",
              "vivid_saturated", "monochrome", "gradient_rich", "cinematic",
              "glassmorphism", "brutalist", "neon_cyber",
              "industrial_technical", "organic_soft"),
    "component": ("sidebar", "top_nav", "bottom_nav", "data_table", "chart",
                  "kpi_tile", "card_grid", "hero", "modal", "form_controls",
                  "timeline", "map_canvas", "code_block", "media"),
}
_STYLE_ORDER = {v: i for i, v in enumerate(_ORDER["style"])}


def _slug(word: str) -> str:
    w = unicodedata.normalize("NFKD", word).encode("ascii", "ignore")
    w = re.sub(r"[^a-z0-9]+", "-", w.decode().lower()).strip("-")
    return w


def _pick(ranked: list[str], order: tuple[str, ...]) -> str | None:
    for cand in order:
        if cand in ranked:
            return cand
    return ranked[0] if ranked else None


def _ranked_from(classes: dict[str, list[str]]) -> dict[str, list[str]]:
    """Normalise classifier output into the _ORDER vocabularies, dropping
    'unknown' placeholders so they never reach a filename."""
    clean = lambda items: [t for t in items if t and not t.endswith("_unknown")]  # noqa: E731
    return {
        "ui_category": clean(classes.get("ui_category", [])) or ["ui"],
        "layout": clean(classes.get("layout_pattern", [])),
        "style": sorted(
            clean(classes.get("visual_style", [])),
            key=lambda s: _STYLE_ORDER.get(s, len(_STYLE_ORDER)),
        ),
        "component": clean(classes.get("component_category", [])),
    }


def image_name(classes: dict[str, list[str]], seq: int,
               ext: str) -> str:
    r = _ranked_from(classes)
    parts: list[str] = []
    if r["style"] and r["style"][0] in ("data_dense",):
        # data-density is the most defining trait; it goes first
        parts.append(_slug(r["style"][0]))
    cat = _pick(r["ui_category"], _ORDER["ui_category"])
    if cat and not (parts and parts[0] == "data-dense" and cat == "dashboard"):
        parts.append(_slug(cat))
    for key in ("layout", "style", "component"):
        used = 0
        for cand in r[key]:
            slug = _slug(cand)
            if slug and slug not in parts and used < 2:
                parts.append(slug)
                used += 1
            if used >= 2:
                break
    seen: list[str] = []
    for p in parts:
        if p and p not in seen:
            seen.append(p)
    stem = "-".join(seen[:5]) or "reference"
    return f"{stem}-{seq:03d}{ext}"


def video_name(classes: dict[str, list[str]], seq: int, ext: str) -> str:
    motion = [m for m in (classes.get("motion_category") or ["misc"])
              if not m.endswith("_unknown")] or ["misc"]
    picks: list[str] = []
    lead = _pick(motion, ("scroll", "parallax", "page_transition", "hover",
                          "three_d", "shader", "liquid", "text_animation",
                          "micro_interaction", "navigation", "loading",
                          "background", "cursor", "card", "button", "hero",
                          "misc"))
    if lead:
        picks.append(_slug(lead))
    r = _ranked_from(classes)
    for cand in r["component"][:2]:
        slug = _slug(cand)
        if slug not in picks:
            picks.append(slug)
    style = r["style"][0] if r["style"] else None
    if style and _slug(style) not in picks:
        picks.append(_slug(style))
    seen: list[str] = []
    for p in picks:
        if p and p not in seen:
            seen.append(p)
    stem = "-".join(seen[:4]) or "motion"
    return f"motion-{stem}-{seq:03d}{ext}"


def unique_target(directory: Path, name: str) -> Path:
    """Ensure the generated name does not collide inside REFERENCES/."""
    target = directory / name
    if not target.exists():
        return target
    stem, ext = target.stem, target.suffix
    for i in range(2, 999):
        cand = directory / f"{stem}-{i:02d}{ext}"
        if not cand.exists():
            return cand
    return target  # give up after 997 attempts; caller logs the clash
