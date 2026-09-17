"""Embedding + semantic search index (build spec §14).

Two replaceable providers, resolved per CONFIG/embeddings:

  visual-stat      deterministic 288-D local descriptor (Pillow+numpy only).
                   Always available; no model download. Encodes colour,
                   composition, texture, density, layout rhythm.
  lexical-concept  text embedding of the asset's tag vocabulary expanded
                   through CONFIG/concepts.yaml. Local, deterministic.
  st-neural        optional sentence-transformers encoder; activated only
                   when importable and configured.

Vectors are stored as float32 files under INDEX/embeddings with an id map,
so search loads only one matrix + the SQLite index — never the media.
"""

from __future__ import annotations

import json
import struct
from pathlib import Path
from typing import Any

import numpy as np

from . import VERSIONS, imagefeat
from .config import concepts, get, path_for
from .db import connect, unj

_EMB_DIR: Path | None = None
_IDMAP_NAME = "ids.json"
_ST_MODEL = None  # lazy sentence-transformers singleton


def emb_dir() -> Path:
    global _EMB_DIR
    if _EMB_DIR is None:
        _EMB_DIR = path_for("embeddings")
        _EMB_DIR.mkdir(parents=True, exist_ok=True)
    return _EMB_DIR


# ---------------------------------------------------------------------------
# lexical-concept provider
# ---------------------------------------------------------------------------
VOCAB_DIM = 512


def _vocab() -> list[str]:
    """Deterministic vocabulary: taxonomy tags + concept words."""
    from .config import taxonomy
    vocab: list[str] = []
    for facet, rules in taxonomy().items():
        if isinstance(rules, dict):
            vocab.extend(str(tag) for tag in rules.keys() if tag != "version")
    for word in (concepts().get("concepts") or {}).keys():
        if word not in vocab:
            vocab.append(word)
    for entry in (concepts().get("concepts") or {}).values():
        for alias in entry.get("aliases", []) or []:
            if alias not in vocab:
                vocab.append(alias)
    return sorted(vocab)[:VOCAB_DIM]


def _concept_expand(token: str) -> dict[str, float]:
    out: dict[str, float] = {}
    cons = concepts().get("concepts") or {}
    for name, entry in cons.items():
        aliases = [name, *(entry.get("aliases") or [])]
        if token in aliases or token in name:
            out[name] = 1.0
            for target, weight in (entry.get("expands_to") or {}).items():
                out[target] = max(out.get(target, 0.0), float(weight))
    return out


def lexical_vector(text: str) -> np.ndarray:
    """Hash-free, vocabulary-indexed bag of concepts."""
    vocab = _vocab()
    index = {w: i for i, w in enumerate(vocab)}
    vec = np.zeros(VOCAB_DIM, dtype=np.float32)
    tokens = [t for t in text.lower().replace("-", "_").replace(" ", "_").split("_")
              if t]
    tokens += text.lower().split()
    for token in tokens:
        expansion = _concept_expand(token)
        bag = {token: 1.0, **{k: v for k, v in expansion.items()}}
        for word, weight in bag.items():
            i = index.get(word)
            if i is not None:
                vec[i] = max(vec[i], float(weight))
    n = float(np.linalg.norm(vec))
    return vec / n if n > 1e-8 else vec


def lexical_asset_text(rec: dict) -> str:
    """The searchable text for one asset row (tags + categories + name)."""
    parts: list[str] = []
    for key in ("ui_category", "component_tags", "visual_style",
                "layout_pattern", "motion_category", "design_patterns", "tags"):
        val = rec.get(key)
        if isinstance(val, str):
            parts.extend(unj(val, []) or [])
        elif isinstance(val, list):
            parts.extend(str(x) for x in val)
    name = rec.get("generated_name") or rec.get("original_name") or ""
    parts.append(Path(name).stem)
    if rec.get("caption"):
        parts.append(rec["caption"])
    if rec.get("ocr_text"):
        parts.append(rec["ocr_text"][:400])
    return " ".join(parts)


# ---------------------------------------------------------------------------
# st-neural provider (optional)
# ---------------------------------------------------------------------------
def st_available() -> bool:
    providers = get("embeddings.text_provider", [])
    if "st-neural" not in (providers or []):
        return False
    try:
        import sentence_transformers  # noqa: F401
        return True
    except Exception:
        return False


def st_model():
    global _ST_MODEL
    if _ST_MODEL is not None:
        return _ST_MODEL
    from sentence_transformers import SentenceTransformer
    _ST_MODEL = SentenceTransformer(get("embeddings.st_model", ""))
    return _ST_MODEL


def st_vector(text: str) -> np.ndarray | None:
    if not st_available():
        return None
    try:
        model = st_model()
        vec = model.encode([text], normalize_embeddings=True)[0]
        return np.asarray(vec, dtype=np.float32)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------
def _store(kind: str, ids: list[int], matrix: np.ndarray) -> Path:
    d = emb_dir()
    ids_path = d / f"{kind}-{_IDMAP_NAME}"
    if ids_path.exists():
        prev = json.loads(ids_path.read_text(encoding="utf-8"))
        prev_ids: list[int] = prev["ids"]
        vec_file = d / f"{kind}.f32"
        dim = int(prev["dim"])
        old = np.fromfile(vec_file, dtype=np.float32).reshape(-1, dim) \
            if vec_file.exists() and dim else np.zeros((0, matrix.shape[1]), np.float32)
        keep = {int(i): old[row] for row, i in enumerate(prev_ids)
                if int(i) in set(ids)}
        merged_ids = list(keep.keys())
        rows = [keep[i] for i in merged_ids]
        for i, row in zip(ids, matrix):
            merged_ids.append(int(i))
            rows.append(row)
        ids, matrix = merged_ids, np.stack(rows)
    ids_path.write_text(json.dumps({"ids": ids, "dim": int(matrix.shape[1])}),
                        encoding="utf-8")
    matrix.astype(np.float32).tofile(d / f"{kind}.f32")
    return d / f"{kind}.f32"


def build(conn, force: bool = False) -> dict[str, int]:
    """(Re)build embedding matrices from the asset index. Returns counts."""
    counts: dict[str, int] = {}
    rows = [dict(r) for r in conn.execute(
        "SELECT * FROM assets ORDER BY id")]
    if not rows:
        return counts

    # --- visual vectors ------------------------------------------------
    vis_ids, vis_vecs = [], []
    dim_v = int(get("embeddings.dim_visual", 288))
    for rec in rows:
        feats = unj(rec.get("features"), None)
        if not feats:
            continue
        vec = np.zeros(dim_v, dtype=np.float32)
        keys = imagefeat.FEATURE_KEYS
        for i, k in enumerate(keys):
            if i >= dim_v:
                break
            vec[i] = float(feats.get(k, 0.0))
        # palette block appended when available (compact, not the full 288-D
        # descriptor which is stored at analysis time for images)
        vis_ids.append(int(rec["id"]))
        vis_vecs.append(vec)
    if vis_ids:
        m = np.stack(vis_vecs)
        m /= np.maximum(np.linalg.norm(m, axis=1, keepdims=True), 1e-8)
        _store("visual", vis_ids, m.astype(np.float32))
        counts["visual"] = len(vis_ids)

    # --- text vectors ---------------------------------------------------
    use_st = st_available()
    txt_ids, txt_vecs = [], []
    for rec in rows:
        text = lexical_asset_text(rec)
        vec = st_vector(text) if use_st else None
        if vec is None:
            vec = lexical_vector(text)
        txt_ids.append(int(rec["id"]))
        txt_vecs.append(vec)
    m = np.stack(txt_vecs).astype(np.float32)
    m /= np.maximum(np.linalg.norm(m, axis=1, keepdims=True), 1e-8)
    _store("text", txt_ids, m.astype(np.float32))
    counts["text"] = len(txt_ids)
    counts["provider"] = 1 if use_st else 0
    return counts


def _load(kind: str) -> tuple[list[int], np.ndarray] | None:
    d = emb_dir()
    ids_path = d / f"{kind}-{_IDMAP_NAME}"
    vec_path = d / f"{kind}.f32"
    if not ids_path.exists() or not vec_path.exists():
        return None
    meta = json.loads(ids_path.read_text(encoding="utf-8"))
    dim = int(meta["dim"])
    if dim == 0:
        return None
    m = np.fromfile(vec_path, dtype=np.float32)
    if m.size != dim * len(meta["ids"]):
        return None
    return meta["ids"], m.reshape(-1, dim)


def query_vector(q: str, kind: str = "text") -> np.ndarray | None:
    ids_mat = _load(kind)
    if ids_mat is None:
        return None
    _ids, mat = ids_mat
    if kind == "text":
        vec = st_vector(q) if st_available() else None
        if vec is None:
            vec = lexical_vector(q)
        vec = np.asarray(vec, dtype=np.float32)
        if vec.shape[0] != mat.shape[1]:
            # provider switched since build; fall back to lexical
            vec = lexical_vector(q)
            if vec.shape[0] != mat.shape[1]:
                return None
    else:
        return None
    n = float(np.linalg.norm(vec))
    return vec / n if n > 1e-8 else vec
