"""`uiux init` — project context detection + Design DNA bootstrap (§27).

Inspects an existing project (framework, styling, tokens, components),
writes a .uiux/ context folder, and connects the project to the engine's
index. Existing project files are never overwritten: if a design-dna.md
already exists the fresh proposal is written as design-dna.proposed.md.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from . import dna, search
from .config import get
from .db import connect, j

TOKEN_HINTS = ("--color", "--font", "--space", "--radius", "--bg", "--text",
               "--accent", "--primary")


def detect(root: Path) -> dict:
    ctx: dict = {"root": str(root), "name": root.name}
    pkg = root / "package.json"
    deps: dict[str, str] = {}
    if pkg.is_file():
        try:
            # utf-8-sig tolerates editors/shells that emit a BOM
            data = json.loads(pkg.read_text(encoding="utf-8-sig"))
            deps = {**data.get("dependencies", {}),
                    **data.get("devDependencies", {})}
            ctx["name"] = data.get("name") or root.name
        except json.JSONDecodeError:
            pass
    def has(*names: str) -> bool:
        return any(n in deps for n in names)
    frameworks = []
    if has("next"): frameworks.append("next")
    if has("nuxt"): frameworks.append("nuxt")
    if has("@remix-run/react"): frameworks.append("remix")
    if has("astro"): frameworks.append("astro")
    if has("react") or has("react-dom"): frameworks.append("react")
    if has("vue"): frameworks.append("vue")
    if has("svelte"): frameworks.append("svelte")
    if has("@angular/core"): frameworks.append("angular")
    ctx["framework"] = frameworks or ["unknown"]
    libs = []
    if has("framer-motion", "motion"): libs.append("framer-motion")
    if has("gsap"): libs.append("gsap")
    if has("three"): libs.append("three")
    if has("@react-three/fiber"): libs.append("react-three-fiber")
    if has("lenis"): libs.append("lenis")
    if has("tailwindcss"): libs.append("tailwind")
    ctx["libraries"] = libs
    ctx["styling"] = ("tailwind" if has("tailwindcss") else
                      "css-vars" if _has_css_vars(root) else "unknown")
    ctx["tokens"] = _find_tokens(root)
    ctx["components"] = _find_components(root)
    ctx["data_heavy"] = _looks_data_heavy(root)
    return ctx


def _has_css_vars(root: Path) -> bool:
    for css in list(root.glob("src/**/*.css"))[:20] + list(root.glob("**/*.css"))[:20]:
        try:
            if "--" in css.read_text(encoding="utf-8", errors="ignore")[:8000]:
                return True
        except OSError:
            continue
    return False


def _find_tokens(root: Path) -> list[str]:
    found = []
    patterns = ["tailwind.config.*", "**/tokens.json", "**/design-tokens*",
                "**/theme.*"]
    for pat in patterns:
        found += [str(p) for p in list(root.glob(pat))[:8]
                  if p.is_file() and "node_modules" not in str(p)]
    return sorted(set(found))[:10]


def _find_components(root: Path) -> list[str]:
    hits = []
    for base in ("src/components", "components", "app/components", "lib/components"):
        d = root / base
        if d.is_dir():
            hits.append(base)
    return hits


def _looks_data_heavy(root: Path) -> bool:
    markers = ("table", "chart", "grid", "dashboard", "recharts",
               "@tanstack/react-table", "d3", "visx")
    for base in ("src", "app", "components", "pages"):
        d = root / base
        if not d.is_dir():
            continue
        try:
            for f in list(d.rglob("*.tsx"))[:40] + list(d.rglob("*.jsx"))[:40]:
                try:
                    head = f.read_text(encoding="utf-8", errors="ignore")[:4000].lower()
                except OSError:
                    continue
                if any(m in head for m in markers):
                    return True
        except OSError:
            continue
    return False


def guess_industry(ctx: dict) -> str:
    name = ctx.get("name", "").lower()
    table = {
        "fintech": ["bank", "pay", "fin", "invest", "trade"],
        "healthcare": ["health", "med", "care", "clinic"],
        "devtools": ["dev", "code", "api", "stack"],
        "analytics": ["analyt", "metric", "insight", "data"],
        "education": ["edu", "learn", "school", "academy"],
        "commerce": ["shop", "store", "cart", "commerce"],
    }
    for industry, keys in table.items():
        if any(k in name for k in keys):
            return industry
    return "unknown"


def init_project(root: Path, answers: dict | None = None) -> dict:
    answers = answers or {}
    ctx = detect(root)
    ctx["industry"] = answers.get("industry") or guess_industry(ctx)
    ctx["audience"] = answers.get("audience", "unknown")
    ctx["product_type"] = answers.get("product_type", ctx["framework"][0])
    ctx["dark_mode"] = answers.get("dark_mode")
    ctx["motion_appetite"] = answers.get("motion_appetite", "medium")
    ctx["accessibility_first"] = answers.get("accessibility_first", True)
    ctx["brand"] = answers.get("brand", "")

    uiux_dir = root / str(get("project.context_dir", ".uiux"))
    uiux_dir.mkdir(parents=True, exist_ok=True)
    never_overwrite = bool(get("project.never_overwrite", True))
    # Derived artifacts always refresh (context detection, token exports);
    # human-facing files (design-dna.md, README.md) respect never_overwrite.
    refreshed: list[str] = []

    written: list[str] = []
    context_path = uiux_dir / "context.json"
    context_path.write_text(json.dumps(ctx, indent=2), encoding="utf-8")
    written.append(str(context_path))
    refreshed.append("context.json")

    dna_payload = dna.generate(ctx)
    md = render_dna_md(dna_payload)
    dna_path = uiux_dir / "design-dna.md"
    if dna_path.exists():
        existing = dna_path.read_text(encoding="utf-8")
        if existing == md:
            written.append(str(dna_path))
        elif never_overwrite:
            dna_path = uiux_dir / "design-dna.proposed.md"
            if not (dna_path.exists() and
                    dna_path.read_text(encoding="utf-8") == md):
                dna_path.write_text(md, encoding="utf-8")
            written.append(str(dna_path))
        else:
            dna_path.write_text(md, encoding="utf-8")
            written.append(str(dna_path))
    else:
        dna_path.write_text(md, encoding="utf-8")
        written.append(str(dna_path))
    if dna_path.name == "design-dna.md":
        refreshed.append("design-dna.md")

    tokens_path = uiux_dir / "tokens.json"
    tokens_path.write_text(json.dumps(_tokens(dna_payload), indent=2),
                           encoding="utf-8")
    written.append(str(tokens_path))
    refreshed.append("tokens.json")
    motion_path = uiux_dir / "motion.json"
    motion_path.write_text(json.dumps(dna_payload["motion"], indent=2),
                           encoding="utf-8")
    written.append(str(motion_path))
    refreshed.append("motion.json")

    # register in the engine index
    try:
        conn = connect()
        conn.execute(
            "INSERT INTO projects(id,name,root,framework,styling,industry,"
            "dna_path) VALUES(?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET "
            "framework=excluded.framework, dna_path=excluded.dna_path, "
            "updated_at=datetime('now')",
            (ctx["name"], ctx["name"], str(root), j(ctx["framework"]),
             ctx["styling"], ctx["industry"], str(dna_path)))
        conn.commit()
        conn.close()
    except Exception:
        pass

    # a short agent-facing README so any future session knows the contract
    readme = uiux_dir / "README.md"
    if not (never_overwrite and readme.exists()):
        readme.write_text(_uiux_readme(), encoding="utf-8")
        written.append(str(readme))
    return {"context": ctx, "dna": dna_payload, "written": written,
            "refreshed": refreshed}


def _tokens(payload: dict) -> dict:
    p = payload["palette"]
    return {
        "color": {k: p[k] for k in ("background", "surface", "text", "muted",
                                    "border", "accent", "on_accent", "success",
                                    "warning", "danger")
                  if p.get(k)},
        "font": {"display": payload["typography"]["display"],
                 "body": payload["typography"]["body"],
                 "mono": payload["typography"]["mono"]},
        "space": payload["spacing"]["scale"],
        "radius": payload["radius"],
        "motion": payload["motion"],
        "density": payload["density"],
    }


def render_dna_md(payload: dict) -> str:
    d = payload["direction"]
    p = payload["palette"]
    t = payload["typography"]
    m = payload["motion"]
    a = payload["accessibility"]
    lines = [
        f"# Design DNA — {payload['project']}",
        "",
        f"> Generated by UIUX ENGINE. Unique to this project: direction,",
        f"> palette, type, spacing and motion were derived from the project",
        f"> requirements — not copied from a template.",
        "",
        "## Product Identity",
        f"- **Direction:** {d['name']} — {d['description']}",
        f"- **Alternatives considered:** "
        f"{', '.join(payload['alternatives_considered'])} (rejected on fit)",
        "",
        "## Audience & Industry",
        "- Recorded in .uiux/context.json; tune the direction if it changes.",
        "",
        "## Visual Direction",
        f"- Density: **{d['density']}**; motion: **{d['motion']}**; "
        f"radius family: **{d['radius']}**",
        f"- Layout: navigation **{payload['layout']['navigation']}**, grid "
        f"**{payload['layout']['grid']}**, hero **{payload['layout']['hero']}**",
        f"- Imagery: {payload['imagery']}",
        "",
        "## Color Strategy",
        f"- Strategy: **{p['strategy']}** ({'dark' if p['dark'] else 'light'} surface system)",
        "",
        "| Token | Value | Role |",
        "|---|---|---|",
        f"| background | `{p['background']}` | page base |",
        f"| surface | `{p['surface']}` | cards, panels |",
        f"| text | `{p['text']}` | body copy (WCAG-checked) |",
        f"| muted | `{p['muted']}` | secondary text (4.5:1) |",
        f"| border | `{p['border']}` | hairlines, dividers |",
        f"| accent | `{p['accent']}` | primary actions, focus |",
    ]
    if p.get("accent2"):
        lines.append(f"| accent-2 | `{p['accent2']}` | secondary emphasis |")
    lines += [
        f"| on-accent | `{p['on_accent']}` | text on accent (4.5:1) |",
        f"| success | `{p['success']}` | positive states |",
        f"| warning | `{p['warning']}` | caution states |",
        f"| danger | `{p['danger']}` | destructive states |",
        "",
        "## Typography",
        f"- Display: **{t['display']}** / Body: **{t['body']}** / Mono: {t['mono']}",
        f"- Type scale ratio: {t['scale']} (modular scale, clamp() for fluid)",
        f"- Numerals: tabular-nums in data contexts",
        "",
        "## Spacing & Density",
        f"- Base unit: {payload['spacing']['base']}px; scale: {payload['spacing']['scale']}",
        f"- Row height {payload['density']['row']}px, card padding "
        f"{payload['density']['card_pad']}px, grid gap {payload['density']['grid_gap']}px",
        "",
        "## Motion",
        f"- Fast {m['fast']}ms / base {m['base']}ms / slow {m['slow']}ms, "
        f"stagger {m['stagger']}ms",
        f"- Signature easing: `{m['easing']}`",
        f"- Intensity: {m['intensity']} — motion confirms, never decorates",
        "",
        "## Accessibility Contract",
        f"- Body text ≥ {a['contrast_body']}:1, large text ≥ {a['contrast_large']}:1, "
        f"UI ≥ {a['contrast_ui']}:1",
        f"- Touch targets ≥ {a['touch_target_px']}px; visible focus on every "
        f"interactive element",
        f"- prefers-reduced-motion: every choreographed effect has a static "
        f"equivalent",
        "",
        "## Things to Avoid",
        "- Reaching for a template: this DNA defines the decisions, not a page.",
        "- Decorative motion on task surfaces; it costs users time and battery.",
        "- Low-contrast greys on tinted backgrounds (WCAG is a floor, not a goal).",
        "- Adding a second accent colour without retiring the first.",
        "",
    ]
    return "\n".join(lines)


def _uiux_readme() -> str:
    return """# .uiux — project design context

This folder connects the project to the UIUX ENGINE.

- `context.json`     detected framework/tokens/components (machine-readable)
- `design-dna.md`    the project's Design DNA — the single source of truth
                     for visual decisions
- `tokens.json`      the DNA as design tokens
- `motion.json`      motion tokens

## Agent contract

1. Read `design-dna.md` before any UI work. Never contradict it silently.
2. Existing project design system outranks the DNA (priority 6 > 9).
3. Need reference ideas? Run `uiux search "<concept>"` from the engine —
   do NOT load the reference library into context.
4. Accessibility overrides visual trends (priority 4).
"""


def status(conn) -> dict:
    from .db import counts
    return counts(conn)


def search_references(q: str, limit: int = 6) -> list[dict]:
    return search.search(q, limit=limit)
