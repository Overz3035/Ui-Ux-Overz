"""Threshold clustering over visual/text vectors (build spec §7, §12).

Simple agglomerative pass with a cosine threshold; clusters annotate assets
with cluster_id and get human-readable labels from dominant member tags.
No original file is ever touched.
"""

from __future__ import annotations

import json

import numpy as np

from .config import get
from .db import unj


def _cosine_clusters(matrix: np.ndarray, threshold: float) -> list[list[int]]:
    """Greedy single-pass leader clustering; O(n * k). Deterministic."""
    n = matrix.shape[0]
    centroids: list[np.ndarray] = []
    members: list[list[int]] = []
    order = np.argsort(-np.linalg.norm(matrix, axis=1))  # strongest first
    for idx in order:
        vec = matrix[idx]
        best, best_sim = -1, -1.0
        for ci, cvec in enumerate(centroids):
            sim = float(np.dot(vec, cvec) /
                        max(np.linalg.norm(vec) * np.linalg.norm(cvec), 1e-8))
            if sim > best_sim:
                best, best_sim = ci, sim
        if best >= 0 and best_sim >= 1.0 - threshold:
            members[best].append(int(idx))
            centroids[best] = (centroids[best] * (len(members[best]) - 1)
                               + vec) / len(members[best])
        else:
            centroids.append(vec.copy())
            members.append([int(idx)])
    return members


def label_for(tags: list[str]) -> str:
    """Human-readable cluster label from dominant (facet-prefixed) tags."""
    stop = {"unknown", "misc"}
    words = []
    for t in tags:
        if not t or t in stop:
            continue
        clean = t.split(":", 1)[-1]  # strip facet prefix
        if clean and clean not in stop and clean not in words:
            words.append(clean)
    return "-".join(words[:3]) if words else "cluster"


def run(conn, force: bool = False) -> dict:
    thr = float(get("cluster.threshold", 0.22))
    min_size = int(get("cluster.min_cluster_size", 2))
    rows = [dict(r) for r in conn.execute(
        "SELECT id, tags, ui_category, visual_style, layout_pattern, "
        "motion_category FROM assets WHERE duplicate_of IS NULL ORDER BY id")]
    if len(rows) < min_size:
        return {"clusters": 0, "assigned": 0}

    # Build a tag-space matrix (stable, interpretable, no embeddings needed).
    vocab: dict[str, int] = {}
    vecs = np.zeros((len(rows), 0), dtype=np.float32)
    tag_lists = []
    for r in rows:
        tags: set[str] = set()
        for key in ("tags", "ui_category", "visual_style", "layout_pattern",
                    "motion_category"):
            val = r.get(key)
            items = unj(val, []) if isinstance(val, str) else (val or [])
            tags.update(str(t) for t in items)
        tag_lists.append(sorted(tags))
        for t in tags:
            vocab.setdefault(t, len(vocab))
    if not vocab:
        return {"clusters": 0, "assigned": 0}
    vecs = np.zeros((len(rows), len(vocab)), dtype=np.float32)
    for i, tags in enumerate(tag_lists):
        for t in tags:
            vecs[i, vocab[t]] = 1.0
    norms = np.maximum(np.linalg.norm(vecs, axis=1, keepdims=True), 1e-8)
    vecs /= norms

    members = _cosine_clusters(vecs, thr)
    conn.execute("DELETE FROM clusters")
    conn.execute("UPDATE assets SET cluster_id=NULL")
    stats = {"clusters": 0, "assigned": 0}
    for group in members:
        if len(group) < min_size:
            continue
        all_tags: list[str] = []
        for i in group:
            all_tags.extend(tag_lists[i])
        dom: dict[str, int] = {}
        for t in all_tags:
            dom[t] = dom.get(t, 0) + 1
        top = sorted(dom.items(), key=lambda kv: -kv[1])[:6]
        cur = conn.execute(
            "INSERT INTO clusters(label,size,dominant) VALUES(?,?,?)",
            (label_for([t for t, _ in top]), len(group),
             json.dumps([t for t, _ in top])))
        cid = cur.lastrowid
        for i in group:
            conn.execute("UPDATE assets SET cluster_id=? WHERE id=?",
                         (cid, rows[i]["id"]))
            stats["assigned"] += 1
        stats["clusters"] += 1
    conn.commit()
    return stats
