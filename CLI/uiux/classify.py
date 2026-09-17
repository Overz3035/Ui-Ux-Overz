"""Rule-based local classification using CONFIG/taxonomy.yaml.

Every tag the engine attaches to an asset traces back to a rule in the
taxonomy, so classification stays inspectable and editable without code
changes (knowledge over black boxes). No language model is involved.

Rule fields:
  any / all / none : keyword matchers against filename + OCR text
  when             : numeric predicate over features, e.g. "aspect > 1.4"
  score            : contribution when the rule fires (default 1.0)

A rule fires when (any matches) OR (all match, when `all` is given) OR the
`when` predicate passes. `none` vetoes the rule.
"""

from __future__ import annotations

import re

from .config import taxonomy

_FACETS = (
    "ui_category", "component_category", "visual_style", "layout_pattern",
    "motion_category",
)

_OPS = {
    ">": lambda a, b: a > b,
    "<": lambda a, b: a < b,
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
}

_CLAUSE = re.compile(r"\s*([a-z_]+)\s*(>=|<=|==|!=|>|<)\s*(-?[\d.]+)\s*")
_PCACHE: dict[str, list[tuple[str, str, float]] | None] = {}


def _compile_predicate(expr: str) -> list[tuple[str, str, float]] | None:
    if expr not in _PCACHE:
        parts: list[tuple[str, str, float]] = []
        for clause in expr.split(" and "):
            m = _CLAUSE.fullmatch(clause)
            if not m:
                _PCACHE[expr] = None
                break
            parts.append((m.group(1), m.group(2), float(m.group(3))))
        else:
            _PCACHE[expr] = parts
    return _PCACHE[expr]


def _eval_when(expr: str, feats: dict[str, float]) -> bool:
    parts = _compile_predicate(expr)
    if not parts:
        return False
    for key, op, val in parts:
        actual = feats.get(key)
        if actual is None or not _OPS[op](float(actual), val):
            return False
    return True


def classify(text: str, feats: dict[str, float],
             facet: str) -> list[tuple[str, float]]:
    """Score one taxonomy facet. Returns [(tag, score), ...] sorted desc."""
    rules = taxonomy().get(facet) or {}
    low = text.lower()
    scores: dict[str, float] = {}
    for tag, entries in rules.items():
        if not isinstance(entries, list):
            continue
        total = 0.0
        for rule in entries:
            if not isinstance(rule, dict):
                continue
            if rule.get("none") and any(t in low for t in rule["none"]):
                continue
            fired = False
            if rule.get("any"):
                fired = any(t in low for t in rule["any"])
            elif rule.get("all"):
                fired = all(t in low for t in rule["all"])
            if not fired and rule.get("when"):
                fired = _eval_when(rule["when"], feats)
            if fired:
                total += float(rule.get("score", 1.0))
        if total > 0:
            scores[tag] = round(total, 3)
    return sorted(scores.items(), key=lambda kv: -kv[1])


def classify_asset(text: str, feats: dict[str, float],
                   facets: tuple[str, ...] = _FACETS) -> dict[str, list[str]]:
    """Classify all requested facets, keeping the leader plus ties within
    20% of its score (max 4 per facet). Facets with no evidence map to
    ``<facet>_unknown`` so downstream naming/knowledge stays explicit."""
    out: dict[str, list[str]] = {}
    for facet in facets:
        ranked = classify(text, feats, facet)
        if not ranked:
            out[facet] = [facet.replace("_category", "") + "_unknown"]
            continue
        lead = ranked[0][1]
        out[facet] = [t for t, s in ranked if s >= lead * 0.8][:4]
    return out
