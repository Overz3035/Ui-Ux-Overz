"""Ingestion pipeline (build spec Â§6â€“Â§8, Â§30).

INBOX/sources/source-XXX/{images,videos}  -> grouped sources
INBOX/loose/{images,videos}, INBOX/images, INBOX/videos -> loose assets

For every asset:
  1. exact cache check (content hash + analyzer fingerprint)
  2. local analysis (image: Pillow+numpy; video: ffprobe+ffmpeg)
  3. rule-based classification (taxonomy)
  4. source assignment (folder group or inferred stem group)
  5. generated name + REFERENCES/ materialisation (hardlink/copy)
  6. write metadata row + tags

Originals are NEVER modified or deleted.
"""

from __future__ import annotations

import json
import os
import shutil
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from . import classify, db, hashing, imagefeat, naming, videofeat
from .config import analyzer_fingerprint, get, load_config, path_for
from .tools import find_tool

VIDEO_EXT = {".mp4", ".webm", ".mov", ".m4v", ".mkv", ".avi"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tiff", ".avif"}


def _inbox() -> Path:
    return path_for("inbox")


def _sources_root() -> Path:
    return path_for("sources")


def _references_root() -> Path:
    return path_for("references")


def discover() -> dict[str, list[Path]]:
    """Walk INBOX and bucket every supported file.

    Loose conventions: INBOX/images, INBOX/videos, INBOX/loose/*.
    Any other INBOX subfolder is treated as a source group (§7)."""
    root = _inbox()
    loose_names = {"images", "videos", "loose"}
    out: dict[str, list[Path]] = {"grouped": [], "loose": []}
    if not root.is_dir():
        return out
    for entry in sorted(root.iterdir()):
        if entry.name.startswith("."):
            continue
        if entry.is_dir() and entry.name.lower() == "sources":
            for group in sorted(entry.iterdir()):
                if not group.is_dir() or group.name.startswith("."):
                    continue
                for p in group.rglob("*"):
                    if p.is_file() and p.suffix.lower() in IMAGE_EXT | VIDEO_EXT:
                        out["grouped"].append(p)
        elif entry.is_dir() and entry.name.lower() in loose_names:
            for p in entry.rglob("*"):
                if p.is_file() and p.suffix.lower() in IMAGE_EXT | VIDEO_EXT:
                    out["loose"].append(p)
        elif entry.is_dir():
            # unknown subfolder: treat as a source group (auto_source_from_folder)
            if get("ingest.auto_source_from_folder", True):
                for p in entry.rglob("*"):
                    if p.is_file() and p.suffix.lower() in IMAGE_EXT | VIDEO_EXT:
                        out["grouped"].append(p)
        elif entry.suffix.lower() in IMAGE_EXT | VIDEO_EXT:
            out["loose"].append(entry)
    return out


def _source_for_grouped(path: Path) -> str:
    """source id from the directory layout: INBOX/sources/<gid>/... or
    INBOX/<gid>/..."""
    rel = path.relative_to(_inbox())
    parts = rel.parts
    if parts and parts[0].lower() == "sources":
        gid = parts[1] if len(parts) > 1 else "unknown"
    else:
        gid = parts[0]
    return _mk_source_id(gid, str(path.parent))


def _mk_source_id(gid: str, hint: str) -> str:
    import re
    slug = re.sub(r"[^a-z0-9]+", "-", gid.lower()).strip("-") or "src"
    import hashlib
    h = hashlib.sha1(hint.encode("utf-8", "ignore")).hexdigest()[:4]
    return f"source-{slug[:28]}-{h}"


def _upsert_source(conn, sid: str, label: str, kind: str, inbox_path: str,
                   confidence: str) -> None:
    conn.execute(
        "INSERT INTO sources(id,label,origin_url,inbox_path,kind,"
        "source_confidence) VALUES(?,?,?,?,?,?) "
        "ON CONFLICT(id) DO UPDATE SET label=excluded.label, "
        "kind=excluded.kind, inbox_path=excluded.inbox_path, "
        "source_confidence=excluded.source_confidence, "
        "updated_at=datetime('now')",
        (sid, label, None, inbox_path, kind, confidence))


def _infer_loose_groups(paths: list[Path]) -> dict[Path, tuple[str, str]]:
    """Filename-stem clustering for loose assets (build spec Â§8).

    'GetLayers AI â€” An AI-native library of templates._10.mp4' and its
    siblings share the stem before the trailing _N suffix -> one soft group.
    Returns path -> (source_id, confidence)."""
    import re
    conf = get("ingest.infer_source_from_filename", True)
    min_assets = int(get("ingest.infer_source_min_assets", 2))
    out: dict[Path, tuple[str, str]] = {}
    if not conf:
        return out
    stems: dict[str, list[Path]] = {}
    for p in paths:
        stem = re.sub(r"[_\-]?\d+$", "", p.stem).strip(" -_")
        if not stem or stem.lower() in ("img", "image", "video", "screenshot"):
            continue  # no meaningful stem -> stays source_confidence: low
        stems.setdefault(stem.lower(), []).append(p)
    for stem, members in stems.items():
        if len(members) < min_assets:
            continue
        sample = members[0]
        sid = _mk_source_id(stem, str(sample.parent) + stem)
        for p in members:
            out[p] = (sid, "medium")
    return out


def _materialize(src: Path, dest_dir: Path, generated: str) -> Path | None:
    """Hardlink (or copy) the original into REFERENCES/ under its new name.

    Idempotent: if the target already exists and IS this file (hardlink
    shares the inode), it is reused instead of suffixed."""
    mode = str(get("ingest.materialize", "hardlink")).lower()
    if mode == "none":
        return None
    dest_dir.mkdir(parents=True, exist_ok=True)
    target = dest_dir / generated
    if target.exists():
        try:
            if os.path.samefile(src, target):
                return target
        except OSError:
            pass
        target = naming.unique_target(dest_dir, generated)
    try:
        if mode == "hardlink":
            try:
                os.link(src, target)
                return target
            except OSError:
                mode = "copy"  # different volume (e.g. INBOX on another drive)
        if mode in ("copy", "symlink"):
            if mode == "copy":
                shutil.copy2(src, target)
            else:
                try:
                    os.symlink(src.resolve(), target)
                except OSError:
                    shutil.copy2(src, target)
            return target
    except OSError as exc:
        print(f"  ! materialize failed for {src.name}: {exc}")
    return None


def _seq_by_prefix() -> dict[str, int]:
    return {"image": {}, "video": {}}


def _next_seq(seq: dict, kind: str, key: str) -> int:
    seq[kind][key] = seq[kind].get(key, 0) + 1
    return seq[kind][key]


def _analyze_one(path: Path, kind: str, cache_dir: Path) -> dict:
    """Analyze a single asset with the content-hash + fingerprint cache."""
    from .config import load_config
    cfg = load_config()
    content_hash = hashing.file_hash(path)
    fingerprint = analyzer_fingerprint()
    cache_key = f"{content_hash[:24]}-{fingerprint[:12]}-{kind}"
    cache_file = cache_dir / f"{cache_key}.json"
    if cache_file.exists() and get("cache.enabled", True):
        try:
            data = json.loads(cache_file.read_text(encoding="utf-8"))
            data["_cached"] = True
            return data
        except Exception:
            pass
    if kind == "image":
        result = imagefeat.analyze_image(path)
        result["media_type"] = "image"
        result["capability_gaps"] = []
        if load_config().get("engine", {}).get("mode") == "adaptive":
            if not find_tool("tesseract"):
                result["capability_gaps"].append("ocr_unavailable")
    else:
        rel = Path("videos") / path.name  # keyframes land under INDEX/cache
        work = cache_dir / "video" / content_hash[:16]
        result = videofeat.analyze_video(path, work)
        result["media_type"] = "video"
    result["content_hash"] = content_hash
    result["analyzer_config"] = fingerprint
    # persist to cache (never store numpy arrays raw)
    save = {k: (v.tolist() if isinstance(v, __import__("numpy").ndarray) else v)
            for k, v in result.items() if not isinstance(v, Path)}
    try:
        cache_file.write_text(json.dumps(save, default=str), encoding="utf-8")
    except OSError:
        pass
    return result


def run(conn, workers: int = 0) -> dict:
    t0 = time.time()
    found = discover()
    loose_infer = _infer_loose_groups(found["loose"]) if found["loose"] else {}
    cache_dir = path_for("cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    seq = _seq_by_prefix()

    # prune index rows whose source file the user deleted (metadata only;
    # the engine itself never deletes media)
    known_paths = {str(p) for p in found["grouped"] + found["loose"]}
    stale = [r["id"] for r in conn.execute("SELECT id, original_path FROM assets")
             if str(r["original_path"]) not in known_paths]
    for asset_id in stale:
        conn.execute("DELETE FROM asset_tags WHERE asset_id=?", (asset_id,))
        conn.execute("DELETE FROM pattern_evidence WHERE asset_id=?", (asset_id,))
        conn.execute("DELETE FROM assets WHERE id=?", (asset_id,))
    if stale:
        print(f"  pruned {len(stale)} index row(s) for deleted files")

    jobs: list[tuple[Path, str | None, str]] = []
    for p in found["grouped"]:
        jobs.append((p, _source_for_grouped(p), "high"))
    for p in found["loose"]:
        sid, conf = loose_infer.get(p, (None, "low"))
        jobs.append((p, sid, conf))

    total = len(jobs)
    report = {"discovered": total, "analyzed": 0, "cached": 0,
              "skipped": 0, "errors": 0, "sources": 0, "renamed": 0}

    if workers <= 0:
        workers = max(1, (os.cpu_count() or 2) - 1)

    def process(job: tuple[Path, str | None, str]) -> dict | None:
        path, sid, confidence = job
        try:
            kind = "video" if path.suffix.lower() in VIDEO_EXT else "image"
            analysis = _analyze_one(path, kind, cache_dir)
            return {"path": path, "sid": sid, "confidence": confidence,
                    "analysis": analysis}
        except Exception as exc:  # noqa: BLE001 - keep the batch going
            return {"path": path, "sid": sid, "confidence": confidence,
                    "error": str(exc)}

    results: list[dict | None] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(process, j) for j in jobs]
        done = 0
        for fut in as_completed(futures):
            results.append(fut.result())
            done += 1
            if done % 10 == 0 or done == total:
                print(f"  analyzing {done}/{total}")

    # deterministic order for stable sequence numbers
    results.sort(key=lambda r: str(r["path"]) if r else "")

    for res in results:
        if res is None:
            continue
        if "error" in res:
            report["errors"] += 1
            print(f"  ! {res['path'].name}: {res['error'][:120]}")
            continue
        path = res["path"]
        sid = res["sid"]
        confidence = res["confidence"]
        analysis = res["analysis"]
        kind = analysis["media_type"]
        if analysis.get("_cached"):
            report["cached"] += 1
        else:
            report["analyzed"] += 1

        # source rows ------------------------------------------------------
        if sid:
            label = path.parent.name if sid.startswith("source-") else sid
            if "sources" in str(path.parent).lower():
                pass
            _upsert_source(conn, sid, label,
                           "folder" if confidence == "high" else "inferred",
                           str(path.parent), confidence)
            report["sources"] += 0  # counted below via DISTINCT
        else:
            sid = None

        # classification ----------------------------------------------------
        haystack = " ".join([
            path.name, Path(analysis.get("generated_name", "")).stem,
            analysis.get("ocr_text", "") or "",
        ])
        feats = analysis.get("feats") or {k: float(v) for k, v in
                                          (analysis.get("features") or {}).items()}
        facets = ("ui_category", "component_category", "visual_style",
                  "layout_pattern", "motion_category") if kind == "video" \
            else ("ui_category", "component_category", "visual_style",
                  "layout_pattern")
        classes = classify.classify_asset(haystack, feats, facets=facets)

        # naming ------------------------------------------------------------
        ext = path.suffix.lower()
        if kind == "video":
            seq_key = "motion-" + (classes.get("motion_category") or ["misc"])[0]
            generated = naming.video_name(classes, _next_seq(seq, "video", seq_key), ext)
            ref_dir = _references_root() / "videos"
        else:
            seq_key = (classes.get("ui_category") or ["unknown"])[0]
            generated = naming.image_name(classes, _next_seq(seq, "image", seq_key), ext)
            ref_dir = _references_root() / "images"
        ref_path = None
        if get("ingest.rename", True):
            ref_path = _materialize(path, ref_dir, generated)
            if ref_path:
                report["renamed"] += 1

        # media details ------------------------------------------------------
        st = path.stat()
        rec = {
            "media_type": kind,
            "content_hash": analysis["content_hash"],
            "original_path": str(path),
            "original_name": path.name,
            "generated_name": generated,
            "reference_path": str(ref_path) if ref_path else None,
            "source_id": sid,
            "source_confidence": confidence if sid else "low",
            "size_bytes": st.st_size,
            "mtime": st.st_mtime,
            "width": analysis.get("width"),
            "height": analysis.get("height"),
            "aspect": analysis.get("aspect"),
            "duration": analysis.get("duration"),
            "fps": analysis.get("fps"),
            "codec": analysis.get("codec"),
            "palette": analysis.get("palette"),
            "ocr_text": analysis.get("ocr_text"),
            "analyzer_version": analysis.get("analyzer_version"),
            "analyzer_config": analysis.get("analyzer_config"),
            "capability_gaps": analysis.get("capability_gaps", []),
        }
        if kind == "image":
            rec["features"] = analysis.get("features")
            rec["ahash"] = analysis.get("ahash")
            rec["dhash"] = analysis.get("dhash")
            rec["phash"] = analysis.get("phash")
        else:
            rec["keyframes"] = analysis.get("keyframes")
            rec["phash"] = hashing.aggregate_video_hash(
                analysis.get("kf_hashes") or [])
            rec["contact_sheet"] = analysis.get("contact_sheet")
            rec["scene_cuts"] = analysis.get("scene_cuts")
            motion = analysis.get("motion") or {}
            rec["features"] = {**motion,
                               **(analysis.get("feats") or {})}
            vid_feats = classify.classify_asset(
                haystack, rec["features"], facets=("motion_category",))
            classes["motion_category"] = vid_feats.get("motion_category", [])

        rec["ui_category"] = [t for t in (classes.get("ui_category") or [])
                              if not t.endswith("_unknown")]
        rec["component_tags"] = [t for t in (classes.get("component_category") or [])
                                 if not t.endswith("_unknown")]
        rec["visual_style"] = [t for t in (classes.get("visual_style") or [])
                               if not t.endswith("_unknown")]
        rec["layout_pattern"] = [t for t in (classes.get("layout_pattern") or [])
                                 if not t.endswith("_unknown")]
        rec["motion_category"] = [t for t in (classes.get("motion_category") or [])
                                  if not t.endswith("_unknown")]
        facet_prefix = {"ui_category": "ui", "component_category": "component",
                        "visual_style": "style", "layout_pattern": "layout",
                        "motion_category": "motion"}
        flat = []
        for facet, items in classes.items():
            prefix = facet_prefix.get(facet, facet)
            for item in items:
                if not item.endswith("_unknown"):
                    flat.append(f"{prefix}:{item}")
        rec["tags"] = flat

        asset_id = db.upsert_asset(conn, rec)
        conn.execute("DELETE FROM asset_tags WHERE asset_id=?", (asset_id,))
        for facet, items in classes.items():
            for item in items:
                conn.execute(
                    "INSERT OR REPLACE INTO asset_tags(asset_id,tag,facet,weight)"
                    " VALUES(?,?,?,1.0)", (asset_id, item, facet))

    # counts of sources
    row = conn.execute("SELECT COUNT(*) c FROM sources").fetchone()
    report["sources"] = int(row["c"]) if row else 0
    from .db import set_meta
    set_meta(conn, "last_ingest_at", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    conn.commit()
    report["elapsed_s"] = round(time.time() - t0, 1)
    return report


def summarize_source_languages(conn) -> None:
    """Roll asset tags up into per-source visual/motion language (§15)."""
    for src in [dict(r) for r in conn.execute("SELECT id FROM sources")]:
        sid = src["id"]
        tags = [dict(r) for r in conn.execute(
            "SELECT t.tag, t.facet, COUNT(*) c FROM asset_tags t "
            "JOIN assets a ON a.id=t.asset_id WHERE a.source_id=? "
            "GROUP BY t.tag ORDER BY c DESC LIMIT 12", (sid,))]
        visual = [t["tag"] for t in tags
                  if t["facet"] in ("visual_style", "ui_category",
                                    "layout_pattern")]
        motion = [t["tag"] for t in tags if t["facet"] == "motion_category"]
        counts = {r["media_type"]: r["c"] for r in conn.execute(
            "SELECT media_type, COUNT(*) c FROM assets WHERE source_id=? "
            "GROUP BY media_type", (sid,))}
        conn.execute(
            "UPDATE sources SET visual_language=?, motion_language=?, "
            "asset_count=?, image_count=?, video_count=?, "
            "updated_at=datetime('now') WHERE id=?",
            (db.j(visual[:10]), db.j(motion[:8]),
             counts.get("image", 0) + counts.get("video", 0),
             counts.get("image", 0), counts.get("video", 0), sid))
    conn.commit()
    write_source_metadata(conn)


def write_source_metadata(conn) -> None:
    """One metadata file per source under SOURCES/ (§7, §15).

    Originals stay in INBOX; this file records the relationship between all
    assets that originated from the same source."""
    root = _sources_root()
    root.mkdir(parents=True, exist_ok=True)
    for src in [dict(r) for r in conn.execute(
            "SELECT * FROM sources WHERE id IN "
            "(SELECT DISTINCT source_id FROM assets WHERE source_id IS NOT NULL)")]:
        sid = src["id"]
        assets = [dict(r) for r in conn.execute(
            "SELECT id, media_type, original_name, generated_name, "
            "reference_path FROM assets WHERE source_id=? ORDER BY id",
            (sid,))]
        meta = {
            "id": sid,
            "label": src["label"],
            "kind": src["kind"],
            "source_confidence": src["source_confidence"],
            "inbox_path": src["inbox_path"],
            "counts": {
                "assets": len(assets),
                "images": sum(1 for a in assets if a["media_type"] == "image"),
                "videos": sum(1 for a in assets if a["media_type"] == "video"),
            },
            "visual_language": db.unj(src.get("visual_language"), []),
            "motion_language": db.unj(src.get("motion_language"), []),
            "technology_hints": db.unj(src.get("technology_hints"), []),
            "usage_categories": db.unj(src.get("usage_categories"), []),
            "assets": [
                {"id": a["id"], "type": a["media_type"],
                 "original_name": a["original_name"],
                 "generated_name": a["generated_name"],
                 "reference_path": a["reference_path"]}
                for a in assets
            ],
        }
        out_dir = root / sid
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "source.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

