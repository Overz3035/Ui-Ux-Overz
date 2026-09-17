"""UI UX Pro Max adapter logic (build spec §19).

Detection first, native invocation second, honest fallback third.

This machine HAS ui-ux-pro-max installed as a skill with a native Python
search CLI (src/ui-ux-pro-max/scripts/search.py, --domain/--stack/
--design-system flags) — verified at engine build time. The detector below
probes several skill homes so the adapter keeps working when the engine
folder is copied to another machine where it is absent.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from .tools import run

PROBE_HOMES = [
    Path.home() / ".kilo" / "skills",
    Path.home() / ".claude" / "skills",
    Path.home() / ".agents" / "skills",
    Path.cwd() / ".agents" / "skills",
]

NAMES = ("ui-ux-pro-max", "uiux-pro-max", "ui_ux_pro_max")


def detect() -> dict | None:
    """Locate the skill; return its root + CLI script when present."""
    for home in PROBE_HOMES:
        for name in NAMES:
            root = home / name
            if not root.is_dir():
                continue
            script = _find_search_script(root)
            return {"root": root, "script": script, "home": str(home)}
    # vendored copy shipped with the engine
    from .config import engine_root
    vendor = engine_root() / "ADAPTERS" / "ui-ux-pro-max" / "vendor"
    if vendor.is_dir():
        script = _find_search_script(vendor)
        return {"root": vendor, "script": script, "home": "engine-vendor"}
    return None


def _find_search_script(root: Path) -> str | None:
    for cand in root.rglob("search.py"):
        if "ui-ux-pro-max" in str(cand).lower() or "scripts" in cand.parts:
            return str(cand)
    return None


def invoke(query: str, domain: str | None = None, stack: str | None = None,
           design_system: bool = False, variance: int | None = None,
           motion: int | None = None, density: int | None = None,
           limit: int = 5) -> dict:
    """Call the native search CLI with argv (no shell), preserving its own
    behaviour. Never fabricates flags: unsupported ones are omitted."""
    found = detect()
    if not found:
        return {"ok": False, "reason": "not-installed",
                "fallback": "ENGINE/design-dna-engine.md"}
    script = found["script"]
    if not script:
        return {"ok": False, "reason": "native-cli-not-found",
                "fallback": "ENGINE/design-dna-engine.md"}
    python = shutil.which("python") or shutil.which("python3") or "python"
    argv = [python, script, query, "-n", str(limit)]
    if domain:
        argv += ["--domain", domain]
    if stack:
        argv += ["--stack", stack]
    if design_system:
        argv.append("--design-system")
        if variance is not None:
            argv += ["--variance", str(variance)]
        if motion is not None:
            argv += ["--motion", str(motion)]
        if density is not None:
            argv += ["--density", str(density)]
    ok, out, err = run(argv, timeout=120)
    return {"ok": ok, "output": out if ok else err, "argv": argv}


def route(task_kind: str) -> dict:
    """Router decision: hand the task to the native engine when installed,
    otherwise return the internal fallback path."""
    if task_kind not in ("design-system-generation", "ui-ux-audit",
                         "product-design-guidance", "component-spec"):
        return {"route": "internal", "reason": "task-kind-not-routed"}
    found = detect()
    if found:
        return {"route": "ui-ux-pro-max", "script": found["script"]}
    return {"route": "internal-fallback",
            "fallback": ["ENGINE/design-dna-engine.md",
                         "ENGINE/quality-engine.md"]}
