"""Deduplication (build spec §12): exact + perceptual, annotate-only.

Originals are never deleted. The pipeline writes:
  duplicate_of   -> asset id of the retained copy
  similar_to     -> json list of neighbour asset ids
  cluster_id     -> assigned later by clustering
"""

from __future__ import annotations

import json

from .config import get
from .hashing import aggregate_video_hash, hamming


def run(conn, force: bool = False) -> dict:
    stats = {"exact": 0, "near": 0, "similar_links": 0}
    if not get("dedup.exact", True) and not force:
        pass  # still run; exact flag only documents intent

    rows = [dict(r) for r in conn.execute(
        "SELECT id, media_type, content_hash, phash, keyframes, duplicate_of, "
        "original_path FROM assets ORDER BY id")]

    # ---- exact duplicates (byte-identical) --------------------------------
    by_hash: dict[str, int] = {}
    for r in rows:
        h = r["content_hash"]
        if not h:
            continue
        if h in by_hash:
            conn.execute(
                "UPDATE assets SET duplicate_of=? WHERE id=?",
                (by_hash[h], r["id"]))
            stats["exact"] += 1
        else:
            by_hash[h] = r["id"]

    # ---- perceptual near-duplicates ----------------------------------------
    phash_thr = int(get("dedup.phash_threshold", 6))
    sim_thr = int(get("dedup.similar_threshold", 14))
    vid_thr = int(get("dedup.video_threshold", 8))
    buckets: dict[str, list[dict]] = {}
    for r in rows:
        if r["duplicate_of"]:
            continue  # exact dup: skip visual pass
        ph = r["phash"]
        if r["media_type"] == "video" and not ph and r.get("keyframes"):
            # fold keyframe hashes into one signature
            kfs = [k.split("|")[-1] for k in json.loads(r["keyframes"] or "[]")]
            ph = aggregate_video_hash(kfs)
            if ph:
                conn.execute("UPDATE assets SET phash=? WHERE id=?", (ph, r["id"]))
                r["phash"] = ph
        if not ph:
            continue
        key = ph[:4]  # coarse bucket to keep the O(n^2) scan local
        buckets.setdefault((r["media_type"], key), []).append(r)

    for (media, _k), group in buckets.items():
        thr = vid_thr if media == "video" else phash_thr
        for i, a in enumerate(group):
            for b in group[i + 1:]:
                d = hamming(a["phash"], b["phash"])
                if d <= thr:
                    # keep the lower asset id as canonical
                    canon, dup = (a, b) if a["id"] < b["id"] else (b, a)
                    if not dup["duplicate_of"]:
                        conn.execute(
                            "UPDATE assets SET duplicate_of=? WHERE id=?",
                            (canon["id"], dup["id"]))
                        stats["near"] += 1
                elif d <= sim_thr:
                    a_id, b_id = a["id"], b["id"]
                    for src, dst in ((a_id, b_id), (b_id, a_id)):
                        row = conn.execute(
                            "SELECT similar_to FROM assets WHERE id=?",
                            (src,)).fetchone()
                        cur = json.loads(row["similar_to"] or "[]") if row else []
                        if b_id if src == a_id else a_id not in cur:
                            want = b_id if src == a_id else a_id
                            if want not in cur:
                                cur.append(want)
                        conn.execute(
                            "UPDATE assets SET similar_to=? WHERE id=?",
                            (json.dumps(cur[:16]), src))
                        stats["similar_links"] += 1
    conn.commit()
    return stats
