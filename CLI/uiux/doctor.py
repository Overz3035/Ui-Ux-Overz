"""`uiux doctor` — environment, capability and resource detection.

Writes INDEX/resource-state.json so the resource registry (CONFIG/
resources.yaml) and every adapter see live detection results without the
registry itself being edited by hand.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from . import VERSIONS, db, tools
from .config import engine_root, get, load_config, path_for


def _python_ok() -> tuple[bool, str]:
    v = sys.version_info
    ok = v >= (3, 10)
    return ok, f"{v.major}.{v.minor}.{v.micro}"


def collect() -> dict:
    checks: list[dict] = []

    def add(name: str, ok: bool, detail: str, required: bool = False) -> None:
        checks.append({"name": name, "ok": bool(ok), "detail": detail,
                       "required": required})

    ok, ver = _python_ok()
    add("python", ok, ver, required=True)
    ok, detail = tools.importable("PIL")
    add("pillow", ok, tools.python_package("pillow") or detail, required=True)
    ok, detail = tools.importable("numpy")
    add("numpy", ok, tools.python_package("numpy") or detail, required=True)
    ok, detail = tools.importable("yaml")
    add("pyyaml", ok, detail + " (built-in mini-YAML fallback active)" if not ok else tools.python_package("pyyaml") or "ok")

    for toolname in ("ffmpeg", "ffprobe", "tesseract"):
        p = tools.find_tool(toolname)
        add(toolname, bool(p), p or "not found")
    add("pytesseract", tools.importable("pytesseract")[0],
        tools.python_package("pytesseract") or "not installed (OCR off)")
    add("sentence-transformers", tools.importable("sentence_transformers")[0],
        tools.python_package("sentence-transformers") or "not installed (lexical embeddings)")
    add("torch", tools.importable("torch")[0],
        tools.python_package("torch") or "not installed")

    # directory health
    root = engine_root()
    missing_dirs = [d for d in
                    ("INBOX", "SOURCES", "REFERENCES", "INDEX", "KNOWLEDGE",
                     "ENGINE", "SKILLS", "PROMPTS", "WORKFLOWS", "MODULES",
                     "ADAPTERS", "SCRIPTS", "CLI", "CONFIG", "DOCS")
                    if not (root / d).is_dir()]
    add("directories", not missing_dirs,
        "all present" if not missing_dirs else f"missing: {', '.join(missing_dirs)}")

    # index health
    try:
        conn = db.init()
        counts = db.counts(conn)
        add("index", True,
            f"{counts['images']} images, {counts['videos']} videos, "
            f"{counts['sources']} sources, {counts['patterns']} patterns "
            f"(schema v{db.get_meta(conn, 'schema_version', '?')})")
        conn.close()
    except Exception as exc:  # noqa: BLE001
        add("index", False, f"{type(exc).__name__}: {exc}")

    # configuration
    try:
        cfg = load_config(reload=True)
        mode = get("engine.mode", cfg)
        add("config", True, f"mode={mode}, tools pinned: "
            f"{', '.join(k for k in ('ffmpeg', 'ffprobe', 'tesseract') if get(f'tools.{k}', '')) or 'none'}")
    except Exception as exc:  # noqa: BLE001
        add("config", False, str(exc)[:120])

    # resource detection (registry + live probes)
    resources = detect_resources()
    return {"versions": dict(VERSIONS), "checks": checks,
            "resources": resources,
            "engine_root": str(root)}


def _probe(item: dict) -> tuple[bool, str]:
    kind, name = item.get("kind"), item.get("name", "")
    if kind == "claude_skill":
        homes = [
            Path.home() / ".kilo" / "skills",
            Path.home() / ".claude" / "skills",
            Path.home() / ".agents" / "skills",
            engine_root() / "SKILLS",
            engine_root() / ".agents" / "skills",
            Path.cwd() / ".kilo" / "skills",
            Path.cwd() / ".claude" / "skills",
            Path.cwd() / ".agents" / "skills",
        ]
        for home in homes:
            cand = home / name / "SKILL.md"
            if cand.is_file():
                return True, str(cand)
        return False, "skill not found"
    if kind == "npm_global":
        ok, out, _err = tools.run(["npm", "ls", "-g", "--depth=0", name], timeout=30)
        return ok and name in out, "npm global" if ok else "not in npm global"
    if kind == "ecc_install":
        state = Path.home() / ".claude" / "ecc" / "install-state.json"
        if state.is_file():
            try:
                import json
                data = json.loads(state.read_text(encoding="utf-8"))
                profile = data.get("profile", "?")
                return True, f"installed (profile={profile})"
            except (OSError, ValueError):
                return True, "install-state present"
        return False, "no ~/.claude/ecc/install-state.json"
    if kind == "claude_plugin":
        cand = Path.home() / ".claude" / "plugins" / name
        return cand.is_dir(), str(cand) if cand.is_dir() else "plugin not found"
    if kind == "path_binary":
        which = shutil.which(name)
        return bool(which), which or "not on PATH"
    if kind == "env_var":
        import os
        v = os.environ.get(name)
        return bool(v), v or "env var unset"
    if kind == "directory":
        p = engine_root() / name
        return p.is_dir(), str(p) if p.is_dir() else "vendor dir absent"
    if kind == "file":
        p = Path(str(item.get("path", name))).expanduser()
        return p.is_file(), str(p) if p.is_file() else "file absent"
    return False, f"unknown probe kind: {kind}"


def detect_resources() -> dict:
    """Run every detection probe declared in CONFIG/resources.yaml."""
    from .config import resources
    reg = resources()
    state: dict[str, dict] = {}
    for section in reg.values():
        if not isinstance(section, dict):
            continue
        for name, res in section.items():
            if not isinstance(res, dict):
                continue
            probes = res.get("detection") or []
            found, detail = False, "no probes declared"
            for probe in probes:
                ok, detail = _probe(probe)
                if ok:
                    found = True
                    break
            state[name] = {"installed": found, "detail": detail,
                           "class": res.get("class"),
                           "activation": res.get("activation"),
                           "confidence": res.get("confidence"),
                           "site": res.get("site"),
                           "repo": res.get("repo")}
    return state


def persist_state(report: dict) -> Path:
    import datetime
    state = {
        "generated_at": datetime.datetime.now(datetime.timezone.utc)
        .isoformat(timespec="seconds").replace("+00:00", "Z"),
        "resources": report["resources"],
        "versions": report["versions"],
        "checks": report["checks"],
    }
    out = path_for("index") / "resource-state.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return out


def run(json_out: bool = False) -> dict:
    report = collect()
    persist_state(report)
    if json_out:
        return report
    print(f"UIUX ENGINE doctor — v{VERSIONS['engine']} "
          f"(analyzer {VERSIONS['analyzer']}, schema {VERSIONS['schema']})")
    for c in report["checks"]:
        mark = "OK  " if c["ok"] else ("REQ!" if c["required"] else "--  ")
        print(f"  [{mark}] {c['name']:<22} {c['detail']}")
    print("  resources:")
    for name, st in report["resources"].items():
        if st["installed"]:
            mark = "installed"
        elif not st.get("detail") or st["detail"] == "no probes declared":
            # consult/concept resources are remote knowledge, not installs
            mark = {"consult": "remote", "concept": "concept"}.get(
                st.get("activation") or "", "absent")
        else:
            mark = "absent"
        print(f"    [{mark:<9}] {name} ({st['class']}, "
              f"activation={st['activation']}, confidence={st['confidence']})")
    return report
