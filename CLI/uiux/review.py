"""`uiux review` + `uiux polish` — quality engine (§25, §26).

Static, heuristic, honest: every check reports what it inspected and what it
cannot know. Produces .uiux/quality-report.md and .uiux/polish-plan.md.
Accessibility findings are ranked by the priority hierarchy (§4) — a visual
trend never overrides them.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

SRC_EXT = (".tsx", ".jsx", ".ts", ".js", ".vue", ".svelte", ".html")
STYLE_EXT = (".css", ".scss")


def _iter_source(root: Path, limit: int = 400):
    count = 0
    for ext in SRC_EXT + STYLE_EXT:
        for f in root.rglob(f"*{ext}"):
            if any(part in ("node_modules", ".next", "dist", "build", ".uiux")
                   for part in f.parts):
                continue
            yield f
            count += 1
            if count >= limit:
                return


def review(root: Path) -> dict:
    findings: list[dict] = []
    stats = {"files": 0, "a11y": 0, "motion": 0, "responsive": 0,
             "consistency": 0}

    def add(area: str, severity: str, title: str, detail: str, fix: str,
             file: str | None = None) -> None:
        findings.append({"area": area, "severity": severity, "title": title,
                         "detail": detail, "fix": fix, "file": file})
        stats[f"{'a11y' if area == 'accessibility' else area}"] = \
            stats.get(area, 0) + 1

    files = list(_iter_source(root))
    stats["files"] = len(files)
    alt_re = re.compile(r"<img(?![^>]*\balt=)[^>]*>", re.I)
    aria_re = re.compile(r"aria-hidden=[\"']true[\"']", re.I)
    label_re = re.compile(r"<input(?![^>]*(?:aria-label|id=))[^>]*>", re.I)
    click_div = re.compile(r"<div[^>]*onClick", re.I)
    heading_re = re.compile(r"<h([1-6])\b", re.I)
    reduced_re = re.compile(r"prefers-reduced-motion")
    mq_re = re.compile(r"@media[^{]*\(", re.I)
    focus_re = re.compile(r"focus-visible|focus-within|:focus")

    headings: list[tuple[str, int]] = []
    has_reduced, has_mq, has_focus = False, False, False
    css_vars: dict[str, str] = {}
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = str(f.relative_to(root))
        if f.suffix in SRC_EXT:
            for m in alt_re.finditer(text):
                add("accessibility", "high", "Image missing alt attribute",
                    "Decorative or informational images must declare alt=\"\" "
                    "or descriptive text.", 'Add alt="description"', rel)
            for m in click_div.finditer(text):
                add("accessibility", "medium", "onClick on <div>",
                    "Non-semantic click targets are unreachable by keyboard.",
                    "Use <button> or add role=\"button\", tabindex=0 and "
                    "keyboard handling.", rel)
            for m in label_re.finditer(text):
                add("accessibility", "medium",
                    "Input without label association",
                    "Inputs need a <label for>, aria-label, or aria-labelledby.",
                    "Associate a label.", rel)
            for m in heading_re.finditer(text):
                headings.append((rel, int(m.group(1))))
        else:
            if "aria-hidden" in text and aria_re.search(text):
                pass
            css_vars.update({m.group(1).lower(): m.group(2)
                             for m in re.finditer(
                                 r"(--[a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{3,8})",
                                 text)})
        if reduced_re.search(text):
            has_reduced = True
        if mq_re.search(text):
            has_mq = True
        if focus_re.search(text):
            has_focus = True

    # contrast of declared var pairs
    from .dna import contrast
    pairs = [("background", "text"), ("bg", "fg"), ("background", "foreground"),
             ("color-bg", "color-text")]
    for bg_key, fg_key in pairs:
        bg = next((v for k, v in css_vars.items() if k.endswith(bg_key)), None)
        fg = next((v for k, v in css_vars.items() if k.endswith(fg_key)), None)
        if bg and fg and len(bg) >= 7 and len(fg) >= 7:
            try:
                ratio = contrast(bg[:7], fg[:7])
                if ratio < 4.5:
                    add("accessibility", "high",
                        f"Text contrast {ratio:.2f}:1 below 4.5:1",
                        f"--*{bg_key}={bg} vs --*{fg_key}={fg}",
                        "Darken text or lighten background; re-run review")
            except Exception:
                pass

    if not has_reduced:
        add("motion", "high", "No prefers-reduced-motion handling",
            "Choreographed motion without a static fallback excludes users "
            "and burns battery.", "Add a @media (prefers-reduced-motion: "
            "reduce) block that disables transforms/animations.")
    if not has_focus:
        add("accessibility", "medium", "No visible focus styles found",
            "Keyboard users need a clearly visible focus indicator.",
            "Add :focus-visible styles using the accent token.")
    if not has_mq:
        add("responsive", "medium", "No media queries detected",
            "Desktop-first without breakpoints; verify tablet/mobile layouts.",
            "Define mobile/tablet/desktop breakpoints; adapt navigation and "
            "hierarchy, don't just shrink.")
    if headings:
        prev = 0
        for rel, level in headings[:200]:
            if prev and level > prev + 1:
                add("accessibility", "low", "Heading level skips",
                    f"{rel}: h{prev} -> h{level}",
                    "Use a logical heading order (never skip levels).", rel)
                prev = level
                continue
            prev = level

    # severity sort: high > medium > low
    order = {"high": 0, "medium": 1, "low": 2}
    findings.sort(key=lambda x: (order[x["severity"]], x["area"]))
    return {"findings": findings, "stats": stats}


def render_report(root: Path, result: dict) -> Path:
    uiux = root / ".uiux"
    uiux.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Quality Report — {root.name}",
        "",
        f"Reviewed {result['stats']['files']} source/style files with static "
        f"heuristics. Manual review is still required for UX judgement.",
        "",
        "| Area | Count |",
        "|---|---|",
        f"| accessibility | {result['stats'].get('accessibility', 0)} |",
        f"| motion | {result['stats'].get('motion', 0)} |",
        f"| responsive | {result['stats'].get('responsive', 0)} |",
        "",
    ]
    if not result["findings"]:
        lines.append("No static findings. Run manual review checklist in "
                     "ENGINE/quality-engine.md before shipping.")
    for f in result["findings"]:
        lines.append(f"## [{f['severity'].upper()}] {f['area']}: {f['title']}")
        lines.append(f"- {f['detail']}")
        if f.get("file"):
            lines.append(f"- file: `{f['file']}`")
        lines.append(f"- fix: {f['fix']}")
        lines.append("")
    path = uiux / "quality-report.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def polish_plan(root: Path, result: dict) -> Path:
    uiux = root / ".uiux"
    uiux.mkdir(parents=True, exist_ok=True)
    lines = [f"# Polish Plan — {root.name}", "",
             "Prioritized by the UIUX ENGINE priority hierarchy: "
             "accessibility outranks visual polish.", ""]
    high = [f for f in result["findings"] if f["severity"] == "high"]
    medium = [f for f in result["findings"] if f["severity"] == "medium"]
    low = [f for f in result["findings"] if f["severity"] == "low"]
    for tier, label in ((high, "P0 — fix before ship"),
                        (medium, "P1 — fix this iteration"),
                        (low, "P2 — backlog")):
        if not tier:
            continue
        lines.append(f"## {label}")
        for f in tier:
            lines.append(f"- [ ] {f['title']} ({f['area']})"
                         + (f" — {f['file']}" if f.get("file") else ""))
        lines.append("")
    if not result["findings"]:
        lines.append("Nothing flagged statically. Suggested manual polish:")
        lines.append("- Re-run `uiux search` with the task concept and compare "
                     "your layout against 2-3 retrieved references.")
        lines.append("- Walk the keyboard-only path; run a screen reader smoke "
                     "test.")
        lines.append("- Verify 320px and 1440px layouts; check touch targets.")
    path = uiux / "polish-plan.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
