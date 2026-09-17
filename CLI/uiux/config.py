"""Configuration loading with deep merge and a dependency-free YAML fallback."""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

from . import engine_root

_CACHE: dict[str, Any] = {}


# ---------------------------------------------------------------------------
# YAML
# ---------------------------------------------------------------------------
def load_yaml(path: Path) -> dict:
    """Load YAML via PyYAML, falling back to a small built-in parser.

    The fallback exists so a copied engine folder still works on a bare
    Python install (build spec §34 portability).
    """
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text)
        return data if isinstance(data, dict) else {}
    except ImportError:
        return _mini_yaml(text)


def _split_flow(body: str) -> list[str]:
    """Split a flow-collection body on top-level commas, honouring quotes."""
    parts, buf, depth, quote = [], [], 0, ""
    for ch in body:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = ""
            continue
        if ch in "\"'":
            quote = ch
            buf.append(ch)
        elif ch in "[{":
            depth += 1
            buf.append(ch)
        elif ch in "]}":
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if "".join(buf).strip():
        parts.append("".join(buf))
    return [p.strip() for p in parts if p.strip()]


def _parse_flow(s: str) -> Any:
    """Parse a YAML flow collection, allowing unquoted keys (JSON is a subset)."""
    s = s.strip()
    if s.startswith("[") and s.endswith("]"):
        return [_coerce(p) for p in _split_flow(s[1:-1])]
    if s.startswith("{") and s.endswith("}"):
        out: dict = {}
        for part in _split_flow(s[1:-1]):
            if ":" not in part:
                continue
            k, v = part.split(":", 1)
            out[k.strip().strip("\"'")] = _coerce(v)
        return out
    return s


def _balanced(s: str) -> bool:
    """True when every flow bracket opened in ``s`` is also closed."""
    depth, quote = 0, ""
    for ch in s:
        if quote:
            if ch == quote:
                quote = ""
            continue
        if ch in "\"'":
            quote = ch
        elif ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
    return depth <= 0


def _coerce(raw: str) -> Any:
    s = raw.strip()
    if not s:
        return ""
    if s[0] in "[{":
        return _parse_flow(s)
    low = s.lower()
    if low in ("true", "yes", "on"):
        return True
    if low in ("false", "no", "off"):
        return False
    if low in ("null", "~"):
        return None
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    if re.fullmatch(r"-?\d*\.\d+([eE][-+]?\d+)?", s):
        return float(s)
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    if s.startswith(">") or s.startswith("|"):
        return ""
    return s


def _strip_comment(line: str) -> str:
    """Remove a trailing ``#`` comment that is not inside quotes."""
    out, quote = [], ""
    for i, ch in enumerate(line):
        if quote:
            out.append(ch)
            if ch == quote:
                quote = ""
        elif ch in "\"'":
            quote = ch
            out.append(ch)
        elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
            break
        else:
            out.append(ch)
    return "".join(out).rstrip()


def _mini_yaml(text: str) -> dict:
    """Indentation-based YAML subset parser (recursive descent, two-pass).

    Supports nested maps, block sequences, sequences of maps, inline JSON-ish
    flow values and scalar coercion. Anchors, multi-line scalars and multi-line
    flow collections are out of scope; the shipped CONFIG files stay inside the
    supported subset. This exists purely so a copied engine folder still runs
    without PyYAML installed (build spec §34).
    """
    lines: list[tuple[int, str]] = []
    pending: str | None = None
    pending_indent = 0
    for raw in text.splitlines():
        if pending is not None:
            # continuation of a flow collection broken across lines
            pending += " " + raw.strip()
            if _balanced(pending):
                lines.append((pending_indent, pending.strip()))
                pending = None
            continue
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        clean = _strip_comment(raw)
        if not clean.strip():
            continue
        indent = len(clean) - len(clean.lstrip())
        body = clean.strip()
        if not _balanced(body):
            pending, pending_indent = body, indent
            continue
        lines.append((indent, body))
    if pending is not None:
        lines.append((pending_indent, pending.strip()))

    def block_scalar(idx: int, indent: int, fold: bool) -> tuple[str, int]:
        """Consume an indented block scalar introduced by ``>`` or ``|``."""
        chunks: list[str] = []
        while idx < len(lines) and lines[idx][0] > indent:
            chunks.append(lines[idx][1])
            idx += 1
        return ((" ".join(chunks) + "\n") if fold else "\n".join(chunks)), idx

    def parse_block(idx: int, indent: int) -> tuple[Any, int]:
        """Parse the block at ``indent`` starting at ``lines[idx]``."""
        if idx >= len(lines):
            return {}, idx
        container: Any = [] if lines[idx][1].startswith("- ") else {}
        while idx < len(lines):
            cur_indent, body = lines[idx]
            if cur_indent < indent:
                break
            if cur_indent > indent:  # defensive: unexpected deeper line
                idx += 1
                continue

            if body.startswith("- "):
                if not isinstance(container, list):
                    break
                item = body[2:].strip()
                if item and ":" in item and item[0] not in "[{\"'":
                    k, v = item.split(":", 1)
                    entry = {k.strip().strip("\"'"): _coerce(v)}
                    idx += 1
                    # continuation keys of this list item sit deeper than "- "
                    child_indent = indent + 2
                    while idx < len(lines) and lines[idx][0] >= child_indent \
                            and not lines[idx][1].startswith("- "):
                        sub, idx = parse_block(idx, lines[idx][0])
                        if isinstance(sub, dict):
                            entry.update(sub)
                        else:
                            break
                    container.append(entry)
                    continue
                container.append(_coerce(item))
                idx += 1
                continue

            if ":" not in body:
                idx += 1
                continue
            key, val = body.split(":", 1)
            key = key.strip().strip("\"'")
            val = val.strip()
            idx += 1
            if val in (">", "|", ">-", "|-", ">+", "|+"):
                scalar, idx = block_scalar(idx, cur_indent, val[0] == ">")
                if val.endswith("-"):
                    scalar = scalar.rstrip("\n")
                if isinstance(container, dict):
                    container[key] = scalar
                continue
            if val:
                if isinstance(container, dict):
                    container[key] = _coerce(val)
                continue
            # nested block: look ahead to size it
            if idx < len(lines) and lines[idx][0] > cur_indent:
                child, idx = parse_block(idx, lines[idx][0])
            elif idx < len(lines) and lines[idx][0] == cur_indent \
                    and lines[idx][1].startswith("- "):
                child, idx = parse_block(idx, cur_indent)
            else:
                child = {}
            if isinstance(container, dict):
                container[key] = child
        return container, idx

    result, _ = parse_block(0, lines[0][0] if lines else 0)
    return result if isinstance(result, dict) else {}


# ---------------------------------------------------------------------------
# Merge + access
# ---------------------------------------------------------------------------
def deep_merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_config(reload: bool = False) -> dict:
    if not reload and "config" in _CACHE:
        return _CACHE["config"]
    root = engine_root()
    cfg: dict = {}
    for name in ("config.default.yaml", "config.yaml"):
        p = root / "CONFIG" / name
        if p.is_file():
            cfg = deep_merge(cfg, load_yaml(p))
    # environment overrides: UIUX_<SECTION>__<KEY>
    for env_key, env_val in os.environ.items():
        if not env_key.startswith("UIUX_") or "__" not in env_key:
            continue
        parts = env_key[5:].lower().split("__")
        node = cfg
        for part in parts[:-1]:
            node = node.setdefault(part, {})
            if not isinstance(node, dict):
                break
        else:
            node[parts[-1]] = _coerce(env_val)
    _CACHE["config"] = cfg
    return cfg


def get(path: str, default: Any = None, cfg: dict | None = None) -> Any:
    """Dotted lookup: ``get("ingest.materialize")``."""
    node: Any = cfg if cfg is not None else load_config()
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return default
        node = node[part]
    return node


def resolve_path(value: str | Path, cfg: dict | None = None) -> Path:
    """Resolve a configured path against the engine root unless absolute."""
    p = Path(str(value)).expanduser()
    if p.is_absolute() or (len(str(p)) > 1 and str(p)[1] == ":"):
        return p
    return (engine_root() / p).resolve()


def path_for(key: str, cfg: dict | None = None) -> Path:
    cfg = cfg or load_config()
    raw = get(f"paths.{key}", key.upper(), cfg)
    return resolve_path(raw, cfg)


def taxonomy() -> dict:
    if "taxonomy" not in _CACHE:
        p = engine_root() / "CONFIG" / "taxonomy.yaml"
        _CACHE["taxonomy"] = load_yaml(p) if p.is_file() else {}
    return _CACHE["taxonomy"]


def concepts() -> dict:
    if "concepts" not in _CACHE:
        p = engine_root() / "CONFIG" / "concepts.yaml"
        _CACHE["concepts"] = load_yaml(p) if p.is_file() else {}
    return _CACHE["concepts"]


def resources() -> dict:
    if "resources" not in _CACHE:
        p = resolve_path(get("resources.registry", "CONFIG/resources.yaml"))
        data = load_yaml(p) if p.is_file() else {}
        # live detection state (written by `uiux doctor`) overrides the
        # static `installed:` flags — without editing the registry file.
        state_path = engine_root() / "INDEX" / "resource-state.json"
        if state_path.is_file():
            try:
                state = json.loads(state_path.read_text(encoding="utf-8"))
                live = state.get("resources", {})
                for section in data.values():
                    if not isinstance(section, dict):
                        continue
                    for name, res in section.items():
                        if isinstance(res, dict) and name in live:
                            res["installed"] = bool(live[name].get("installed"))
                            res["runtime_detail"] = live[name].get("detail")
            except (OSError, ValueError):
                pass
        _CACHE["resources"] = data
    return _CACHE["resources"]


def analyzer_fingerprint() -> str:
    """Hash of the analyzer-relevant config, used for cache invalidation (§30)."""
    cfg = load_config()
    subset = {
        "image_analysis": cfg.get("image_analysis", {}),
        "video_analysis": cfg.get("video_analysis", {}),
        "dedup": cfg.get("dedup", {}),
        "embeddings": cfg.get("embeddings", {}),
        "taxonomy_version": taxonomy().get("version"),
    }
    blob = json.dumps(subset, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]
