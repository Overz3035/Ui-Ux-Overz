"""SQLite index for assets, sources, patterns, clusters and knowledge edges.

SQLite is the primary store (build spec §13) because it stays consistent with
tens of thousands of assets and supports incremental cache lookups. The JSON
files under INDEX/ are *exports* generated from here for portability.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Iterable

from . import VERSIONS
from .config import path_for

SCHEMA_VERSION = 1

_DDL = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS sources (
    id                TEXT PRIMARY KEY,     -- source-001
    label             TEXT,
    origin_url        TEXT,
    inbox_path        TEXT,
    kind              TEXT,                 -- folder | inferred | loose
    source_confidence TEXT,                 -- high | medium | low
    asset_count       INTEGER DEFAULT 0,
    image_count       INTEGER DEFAULT 0,
    video_count       INTEGER DEFAULT 0,
    visual_language   TEXT,                 -- json array of tags
    motion_language   TEXT,                 -- json array of tags
    technology_hints  TEXT,                 -- json array
    usage_categories  TEXT,                 -- json array
    notes             TEXT,
    created_at        TEXT DEFAULT (datetime('now')),
    updated_at        TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS assets (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    media_type        TEXT NOT NULL,        -- image | video
    content_hash      TEXT NOT NULL,
    original_path     TEXT NOT NULL,
    original_name     TEXT NOT NULL,
    generated_name    TEXT,
    reference_path    TEXT,
    source_id         TEXT REFERENCES sources(id) ON DELETE SET NULL,
    source_confidence TEXT,
    size_bytes        INTEGER,
    mtime             REAL,
    width             INTEGER,
    height            INTEGER,
    aspect            REAL,
    duration          REAL,
    fps               REAL,
    codec             TEXT,
    features          TEXT,                 -- json: numeric feature vector
    palette           TEXT,                 -- json: [{hex,ratio}]
    ocr_text          TEXT,
    ui_category       TEXT,
    component_tags    TEXT,                 -- json array
    visual_style      TEXT,                 -- json array
    layout_pattern    TEXT,                 -- json array
    motion_category   TEXT,                 -- json array (video)
    design_patterns   TEXT,                 -- json array
    tags              TEXT,                 -- json array (flattened, searchable)
    caption           TEXT,
    keyframes         TEXT,                 -- json array of relative paths
    ahash             TEXT,
    dhash             TEXT,
    phash             TEXT,
    duplicate_of      INTEGER REFERENCES assets(id) ON DELETE SET NULL,
    similar_to        TEXT,                 -- json array of asset ids
    cluster_id        INTEGER,
    analyzer_version  TEXT,
    analyzer_config   TEXT,
    capability_gaps   TEXT,                 -- json array: what could not be computed
    analyzed_at       TEXT DEFAULT (datetime('now')),
    UNIQUE(original_path)
);

CREATE INDEX IF NOT EXISTS idx_assets_hash    ON assets(content_hash);
CREATE INDEX IF NOT EXISTS idx_assets_type    ON assets(media_type);
CREATE INDEX IF NOT EXISTS idx_assets_source  ON assets(source_id);
CREATE INDEX IF NOT EXISTS idx_assets_cluster ON assets(cluster_id);
CREATE INDEX IF NOT EXISTS idx_assets_uicat   ON assets(ui_category);

CREATE TABLE IF NOT EXISTS asset_tags (
    asset_id INTEGER NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    tag      TEXT NOT NULL,
    facet    TEXT NOT NULL,                 -- ui_category | component | style | ...
    weight   REAL DEFAULT 1.0,
    PRIMARY KEY (asset_id, tag, facet)
);
CREATE INDEX IF NOT EXISTS idx_tags_tag ON asset_tags(tag);

CREATE TABLE IF NOT EXISTS clusters (
    id          INTEGER PRIMARY KEY,
    label       TEXT,
    size        INTEGER,
    centroid    TEXT,                       -- json array (short, quantised)
    dominant    TEXT,                       -- json: dominant tags
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS patterns (
    name        TEXT PRIMARY KEY,
    principle   TEXT,
    use_when    TEXT,
    avoid_when  TEXT,
    evidence    INTEGER DEFAULT 0,          -- how many assets support it
    facets      TEXT,                       -- json: requirement map
    card_path   TEXT,
    updated_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS pattern_evidence (
    pattern  TEXT NOT NULL REFERENCES patterns(name) ON DELETE CASCADE,
    asset_id INTEGER NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    score    REAL DEFAULT 1.0,
    PRIMARY KEY (pattern, asset_id)
);

-- Obsidian-inspired knowledge graph (concept adopted, no dependency).
CREATE TABLE IF NOT EXISTS nodes (
    id    TEXT PRIMARY KEY,                 -- "pattern:persistent_sidebar"
    kind  TEXT NOT NULL,                    -- pattern | source | asset | token | principle
    label TEXT,
    data  TEXT
);
CREATE TABLE IF NOT EXISTS edges (
    src      TEXT NOT NULL,
    dst      TEXT NOT NULL,
    relation TEXT NOT NULL,                 -- evidences | contradicts | refines | belongs_to
    weight   REAL DEFAULT 1.0,
    PRIMARY KEY (src, dst, relation)
);
CREATE INDEX IF NOT EXISTS idx_edges_dst ON edges(dst);

CREATE TABLE IF NOT EXISTS projects (
    id          TEXT PRIMARY KEY,
    name        TEXT,
    root        TEXT,
    framework   TEXT,
    styling     TEXT,
    industry    TEXT,
    audience    TEXT,
    dna_path    TEXT,
    dna_seed    TEXT,
    created_at  TEXT DEFAULT (datetime('now')),
    updated_at  TEXT DEFAULT (datetime('now'))
);
"""


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    p = db_path or path_for("db")
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(p))
    conn.row_factory = sqlite3.Row
    return conn


def init(conn: sqlite3.Connection | None = None) -> sqlite3.Connection:
    conn = conn or connect()
    conn.executescript(_DDL)
    set_meta(conn, "schema_version", str(SCHEMA_VERSION))
    set_meta(conn, "engine_version", VERSIONS["engine"])
    set_meta(conn, "index_version", VERSIONS["index"])
    conn.commit()
    return conn


def set_meta(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        "INSERT INTO meta(key,value) VALUES(?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value),
    )


def get_meta(conn: sqlite3.Connection, key: str, default: str | None = None) -> str | None:
    row = conn.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default


def j(value: Any) -> str:
    """JSON-encode for a TEXT column."""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def unj(value: Any, default: Any = None) -> Any:
    if value in (None, "", b""):
        return default if default is not None else []
    if isinstance(value, (list, dict)):
        return value
    try:
        decoded = json.loads(value)
        return default if default is not None and decoded is None else decoded
    except (TypeError, ValueError):
        return default if default is not None else []


def row_to_asset(row: sqlite3.Row) -> dict:
    """Inflate a DB row into a plain dict with JSON columns decoded."""
    d = dict(row)
    for key in (
        "features", "palette", "component_tags", "visual_style", "layout_pattern",
        "motion_category", "design_patterns", "tags", "keyframes", "similar_to",
        "capability_gaps", "ui_category",
    ):
        if key in d:
            d[key] = unj(d[key], {} if key in ("features",) else [])
    return d


def upsert_asset(conn: sqlite3.Connection, rec: dict) -> int:
    """Insert or update by original_path, returning the asset id.

    SQLite validates NOT NULL even on the conflict path, so a partial update
    record is first merged with the stored row."""
    cols = [
        "media_type", "content_hash", "original_path", "original_name",
        "generated_name", "reference_path", "source_id", "source_confidence",
        "size_bytes", "mtime", "width", "height", "aspect", "duration", "fps",
        "codec", "features", "palette", "ocr_text", "ui_category",
        "component_tags", "visual_style", "layout_pattern", "motion_category",
        "design_patterns", "tags", "caption", "keyframes", "ahash", "dhash",
        "phash", "analyzer_version", "analyzer_config", "capability_gaps",
    ]
    json_cols = {
        "features", "palette", "component_tags", "visual_style", "layout_pattern",
        "motion_category", "design_patterns", "tags", "keyframes", "capability_gaps",
        "ui_category",
    }
    existing = conn.execute(
        "SELECT * FROM assets WHERE original_path=?",
        (rec["original_path"],)).fetchone()
    # source fields are always overwritten (an asset may become ungrouped);
    # everything else merges so partial update records stay valid.
    overwrite = ("source_id", "source_confidence")
    if existing:
        prev = dict(existing)
        for c in cols:
            if rec.get(c) is None and c in prev and c not in overwrite:
                rec[c] = unj(prev[c]) if c in json_cols else prev[c]
    values = []
    for c in cols:
        v = rec.get(c)
        values.append(j(v) if c in json_cols and not isinstance(v, str) else v)
    placeholders = ",".join("?" * len(cols))
    updates = ",".join(f"{c}=excluded.{c}" for c in cols if c != "original_path")
    cur = conn.execute(
        f"INSERT INTO assets({','.join(cols)}) VALUES({placeholders}) "
        f"ON CONFLICT(original_path) DO UPDATE SET {updates}, "
        f"analyzed_at=datetime('now')",
        values,
    )
    # lastrowid is unreliable on the UPDATE path of an upsert: always resolve.
    row = conn.execute(
        "SELECT id FROM assets WHERE original_path=?", (rec["original_path"],)
    ).fetchone()
    return int(row["id"])


def replace_tags(conn: sqlite3.Connection, asset_id: int,
                 tags: Iterable[tuple[str, str, float]]) -> None:
    conn.execute("DELETE FROM asset_tags WHERE asset_id=?", (asset_id,))
    conn.executemany(
        "INSERT OR REPLACE INTO asset_tags(asset_id,tag,facet,weight) VALUES(?,?,?,?)",
        [(asset_id, t, f, w) for (t, f, w) in tags],
    )


def cached_record(conn: sqlite3.Connection, original_path: str) -> dict | None:
    row = conn.execute(
        "SELECT * FROM assets WHERE original_path=?", (original_path,)
    ).fetchone()
    return row_to_asset(row) if row else None


def counts(conn: sqlite3.Connection) -> dict:
    def one(sql: str, *a: Any) -> int:
        r = conn.execute(sql, a).fetchone()
        return int(r[0]) if r else 0

    return {
        "assets": one("SELECT COUNT(*) FROM assets"),
        "images": one("SELECT COUNT(*) FROM assets WHERE media_type='image'"),
        "videos": one("SELECT COUNT(*) FROM assets WHERE media_type='video'"),
        "sources": one("SELECT COUNT(*) FROM sources"),
        "clusters": one("SELECT COUNT(*) FROM clusters"),
        "duplicates": one("SELECT COUNT(*) FROM assets WHERE duplicate_of IS NOT NULL"),
        "patterns": one("SELECT COUNT(*) FROM patterns"),
        "tags": one("SELECT COUNT(DISTINCT tag) FROM asset_tags"),
        "projects": one("SELECT COUNT(*) FROM projects"),
    }


def export_json(conn: sqlite3.Connection, out_dir: Path | None = None) -> dict[str, int]:
    """Write portable JSON exports (build spec §13)."""
    out = out_dir or path_for("index")
    out.mkdir(parents=True, exist_ok=True)
    written: dict[str, int] = {}

    def dump(name: str, rows: list[dict]) -> None:
        (out / name).write_text(
            json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        written[name] = len(rows)

    img = [row_to_asset(r) for r in conn.execute(
        "SELECT * FROM assets WHERE media_type='image' ORDER BY id")]
    vid = [row_to_asset(r) for r in conn.execute(
        "SELECT * FROM assets WHERE media_type='video' ORDER BY id")]
    src = []
    for r in conn.execute("SELECT * FROM sources ORDER BY id"):
        d = dict(r)
        for k in ("visual_language", "motion_language", "technology_hints",
                  "usage_categories"):
            d[k] = unj(d.get(k), [])
        src.append(d)
    pat = []
    for r in conn.execute("SELECT * FROM patterns ORDER BY evidence DESC, name"):
        d = dict(r)
        d["facets"] = unj(d.get("facets"), {})
        pat.append(d)
    clu = []
    for r in conn.execute("SELECT * FROM clusters ORDER BY size DESC"):
        d = dict(r)
        d["centroid"] = unj(d.get("centroid"), [])
        d["dominant"] = unj(d.get("dominant"), [])
        d["members"] = [int(x["id"]) for x in conn.execute(
            "SELECT id FROM assets WHERE cluster_id=? ORDER BY id", (d["id"],))]
        clu.append(d)

    dump("images.json", img)
    dump("videos.json", vid)
    dump("sources.json", src)
    dump("patterns.json", pat)
    dump("clusters.json", clu)
    return written
