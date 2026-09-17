"""Pattern extraction: turn indexed references into reusable knowledge
(build spec §15) — "persistent sidebar", "dense data table", "subtle hover
elevation" — never "copy this website".

Patterns come from CONFIG/taxonomy.yaml §design_patterns (requires: facet→
tags). Evidence = assets whose tag set satisfies the requirement map. Each
pattern is written to the patterns table + knowledge graph and exported to
KNOWLEDGE/patterns/ as markdown cards.
"""

from __future__ import annotations

import json

from .config import path_for, taxonomy
from .db import unj

_PATTERN_FACETS = ("ui_category", "component_category", "visual_style",
                   "layout_pattern", "motion_category")


def _asset_tags(rec: dict) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for facet in _PATTERN_FACETS:
        col = facet if facet in rec else None
        if col:
            out[facet] = set(unj(rec[col], []))
    if rec.get("tags"):
        out["flat"] = set(unj(rec["tags"], []))
    return out


def satisfies(required: dict, have: dict[str, set[str]]) -> bool:
    for facet, tags in (required or {}).items():
        pool = have.get(facet, set()) | have.get("flat", set())
        if not pool or not set(tags) & pool:
            return False
    return bool(required)


def run(conn) -> dict:
    rules = taxonomy().get("design_patterns") or {}
    rows = [dict(r) for r in conn.execute("SELECT * FROM assets")]
    recs = []
    for r in rows:
        recs.append({
            "id": r["id"],
            "tags": _asset_tags(r),
        })
    stats = {"patterns": 0, "evidence": 0}
    conn.execute("DELETE FROM pattern_evidence")
    conn.execute("DELETE FROM edges WHERE relation='evidences'")
    for name, rule in rules.items():
        if not isinstance(rule, dict):
            continue
        evidence = [rec["id"] for rec in recs
                    if satisfies(rule.get("requires"), rec["tags"])]
        conn.execute(
            "INSERT INTO patterns(name,principle,use_when,avoid_when,evidence,"
            "facets,updated_at) VALUES(?,?,?,?,?,?,datetime('now')) "
            "ON CONFLICT(name) DO UPDATE SET principle=excluded.principle, "
            "use_when=excluded.use_when, avoid_when=excluded.avoid_when, "
            "evidence=excluded.evidence, facets=excluded.facets",
            (name, rule.get("principle", ""), rule.get("use_when", ""),
             rule.get("avoid_when", ""), len(evidence),
             json.dumps(rule.get("requires", {}))))
        for asset_id in evidence:
            conn.execute(
                "INSERT OR REPLACE INTO pattern_evidence(pattern,asset_id,score) "
                "VALUES(?,?,1.0)", (name, asset_id))
            conn.execute(
                "INSERT OR REPLACE INTO edges(src,dst,relation,weight) "
                "VALUES(?,?, 'evidences', 1.0)",
                (f"pattern:{name}", f"asset:{asset_id}"))
            conn.execute(
                "INSERT OR REPLACE INTO nodes(id,kind,label) VALUES(?,?,?)",
                (f"pattern:{name}", "pattern", name))
        stats["patterns"] += 1
        stats["evidence"] += len(evidence)
    conn.commit()
    write_cards(conn)
    return stats


def write_cards(conn) -> str:
    """Export pattern knowledge as progressive-loadable markdown."""
    out_dir = path_for("knowledge") / "patterns"
    out_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Pattern Library (auto-generated)",
        "",
        "Extracted from the indexed reference library. Each pattern carries",
        "its principle, when to use it, and when to avoid it. Evidence =",
        "number of indexed references that demonstrate the pattern.",
        "",
    ]
    rows = [dict(r) for r in conn.execute(
        "SELECT * FROM patterns ORDER BY evidence DESC, name")]
    for r in rows:
        lines.append(f"## {r['name'].replace('_', ' ').title()}")
        lines.append("")
        lines.append(f"- **Evidence:** {r['evidence']} reference(s)")
        lines.append(f"- **Principle:** {r['principle']}")
        lines.append(f"- **Use when:** {r['use_when']}")
        lines.append(f"- **Avoid when:** {r['avoid_when']}")
        top = [dict(e) for e in conn.execute(
            "SELECT a.generated_name, a.media_type FROM pattern_evidence pe "
            "JOIN assets a ON a.id=pe.asset_id WHERE pe.pattern=? "
            "ORDER BY a.id LIMIT 4", (r["name"],))]
        if top:
            lines.append("- **Examples:** " + ", ".join(
                f"`{t['generated_name'] or t['media_type']}`" for t in top))
        lines.append("")
    path = out_dir / "INDEX.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)
