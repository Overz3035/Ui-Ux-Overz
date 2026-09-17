"""Hybrid semantic search (build spec §14, §29).

Score = w_lexical * lexical_tag_match
      + w_concept * concept_expansion_match
      + w_visual * visual_descriptor_similarity (images/videos)

Only compact metadata + prebuilt vectors are touched — the reference media
never reaches the language model, and only the top-N context pack is emitted.
"""

from __future__ import annotations

import json

import numpy as np

from . import embed
from .config import get
from .db import connect, unj, row_to_asset


def _candidate_rows(conn) -> dict[int, dict]:
    return {int(r["id"]): row_to_asset(r) for r in conn.execute(
        "SELECT * FROM assets WHERE duplicate_of IS NULL")}


def search(q: str, limit: int | None = None, media: str | None = None) -> list[dict]:
    conn = connect()
    try:
        return search_conn(conn, q, limit, media)
    finally:
        conn.close()


def search_conn(conn, q: str, limit: int | None = None,
                media: str | None = None) -> list[dict]:
    limit = limit or int(get("search.default_limit", 12))
    w_lex = float(get("search.weight_lexical", 0.55))
    w_con = float(get("search.weight_concept", 0.25))
    w_vis = float(get("search.weight_visual", 0.20))

    rows = _candidate_rows(conn)
    if media in ("image", "video"):
        rows = {i: r for i, r in rows.items() if r["media_type"] == media}
    if not rows:
        return []

    # --- lexical + concept scores from the asset_tags table ----------------
    lex = np.zeros(len(rows), dtype=np.float32)
    con = np.zeros(len(rows), dtype=np.float32)
    ids = list(rows.keys())
    id_pos = {aid: i for i, aid in enumerate(ids)}

    q_low = q.lower()
    from .classify import classify_asset  # reuse predicate machinery lazily
    feats = {}
    for tag_row in conn.execute(
            "SELECT t.asset_id, t.tag FROM asset_tags t"):
        aid = int(tag_row["asset_id"])
        i = id_pos.get(aid)
        if i is None:
            continue
        tag = tag_row["tag"]
        if tag and tag in q_low:
            lex[i] += 1.0
    # concept expansion
    cons = (embed.concepts().get("concepts") or {})
    wanted: dict[str, float] = {}
    tokens = q_low.replace("-", " ").replace("_", " ").split()
    for name, entry in cons.items():
        aliases = [name] + list(entry.get("aliases") or [])
        if any(a in tokens or a == q_low for a in aliases):
            wanted[name] = 1.0
            for t, w in (entry.get("expands_to") or {}).items():
                wanted[t] = max(wanted.get(t, 0.0), float(w))
    if wanted:
        for tag_row in conn.execute(
                "SELECT t.asset_id, t.tag FROM asset_tags t"):
            aid = int(tag_row["asset_id"])
            i = id_pos.get(aid)
            if i is None:
                continue
            tag = tag_row["tag"]
            if tag in wanted:
                con[i] += float(wanted[tag])
    # lexical vectors as a second opinion (vocabulary-indexed cosine)
    qvec = embed.lexical_vector(q)

    max_lex = float(lex.max()) or 1.0
    max_con = float(con.max()) or 1.0
    lex /= max_lex
    con /= max_con

    # --- visual similarity --------------------------------------------------
    vis = np.zeros(len(rows), dtype=np.float32)
    loaded = embed._load("visual")
    if loaded and w_vis > 0:
        v_ids, v_mat = loaded
        pos = {aid: i for i, aid in enumerate(v_ids)}
        qf = _query_feature_vector(q, conn)
        if qf is not None:
            for i, aid in enumerate(ids):
                j = pos.get(aid)
                if j is not None and j < v_mat.shape[0]:
                    v = v_mat[j][:len(qf)]
                    denom = max(float(np.linalg.norm(v)) * float(np.linalg.norm(qf)), 1e-8)
                    vis[i] = float(np.dot(v, qf) / denom)
        vis = np.clip(vis - 0.55, 0.0, None) / max(0.45, 1.0)

    scores = w_lex * lex + w_con * con + w_vis * vis
    order = np.argsort(-scores)[:limit]
    out: list[dict] = []
    for i in order:
        if scores[i] <= 0.01:
            continue
        rec = rows[ids[i]]
        rec["_score"] = round(float(scores[i]), 4)
        rec["_parts"] = {"lexical": round(float(lex[i]), 3),
                         "concept": round(float(con[i]), 3),
                         "visual": round(float(vis[i]), 3)}
        out.append(rec)
    return out


def _query_feature_vector(q: str, conn) -> np.ndarray | None:
    """Map a natural-language query onto the compact feature vector space by
    anchoring on well-known adjectives (dark, dense, minimal, ...)."""
    from .imagefeat import FEATURE_KEYS
    q_low = q.lower()
    target = {k: 0.0 for k in FEATURE_KEYS}
    anchors = {
        "dark": {"dark_ratio": 0.7, "brightness": 0.25},
        "light": {"light_ratio": 0.7, "brightness": 0.75},
        "dense": {"text_density": 0.7, "panel_score": 0.7,
                  "edge_density": 0.5},
        "data": {"text_density": 0.6, "panel_score": 0.6},
        "minimal": {"text_density": 0.05, "edge_density": 0.08,
                    "panel_score": 0.2},
        "colorful": {"saturation": 0.7, "colorfulness": 0.7},
        "premium": {"contrast": 0.5, "saturation": 0.2},
        "mobile": {"aspect": 0.5},
        "dashboard": {"panel_score": 0.75, "grid_score": 0.5,
                      "text_density": 0.5},
        "landing": {"text_density": 0.15, "aspect": 1.7},
    }
    hit = False
    for word, vals in anchors.items():
        if word in q_low:
            hit = True
            for k, v in vals.items():
                if k in target:
                    target[k] = v
    if not hit:
        return None
    return np.array([target[k] for k in FEATURE_KEYS], dtype=np.float32)


def context_pack(conn, q: str, limit: int | None = None) -> dict:
    """The ONLY payload a language model receives (token efficiency §29).

    Compact JSON: generated name, category, tags, key principle-aligned
    notes. No images, no videos, no base64 — ever."""
    limit = limit or int(get("search.max_context_references", 12))
    hits = search_conn(conn, q, limit=limit)
    pack = []
    for h in hits:
        def first(key: str):
            val = unj(h.get(key), []) if isinstance(h.get(key), str) \
                else (h.get(key) or [])
            return val[0] if val else None
        pack.append({
            "ref": h.get("generated_name") or h.get("original_name"),
            "type": h.get("media_type"),
            "ui_category": first("ui_category"),
            "layout": first("layout_pattern"),
            "style": first("visual_style"),
            "motion": first("motion_category"),
            "palette": [p.get("hex") for p in (unj(h.get("palette"), []) if isinstance(h.get("palette"), str) else h.get("palette") or [])[:4]],
            "score": h.get("_score"),
            "patterns": unj(h.get("design_patterns"), []) if isinstance(h.get("design_patterns"), str) else (h.get("design_patterns") or []),
        })
    return {"query": q, "count": len(pack), "references": pack}
