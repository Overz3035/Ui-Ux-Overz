"""`uiux` command line interface (build spec Â§28).

Commands: init, ingest, search, analyze, design, review, polish, status,
doctor, update, version. Every command supports --json for machine
consumption by agents and adapters.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from . import VERSIONS

log = logging.getLogger("uiux")


def _setup_logging() -> None:
    from .config import get, path_for
    level = str(get("logging.level", "info")).upper()
    logging.basicConfig(level=getattr(logging, level, logging.INFO),
                        format="%(asctime)s %(levelname)s %(message)s")
    try:
        log_file = path_for("index") / "uiux.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        log.addHandler(fh)
    except Exception:
        pass


def _emit(data: dict | list, as_json: bool) -> None:
    if as_json:
        print(json.dumps(data, ensure_ascii=False, indent=2, default=str))
    return


# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------
def cmd_doctor(args) -> int:
    from . import doctor
    report = doctor.run(json_out=args.json)
    _emit(report, args.json)
    if not args.json:
        failed_required = [c for c in report["checks"]
                           if c["required"] and not c["ok"]]
        print(f"\n  {'PASS' if not failed_required else 'FAIL'}: "
              f"{len(report['checks'])} checks, "
              f"{len(failed_required)} required failure(s)")
    return 0 if all(c["ok"] or not c["required"] for c in report["checks"]) else 1


def cmd_ingest(args) -> int:
    from . import cluster, db, dedupe, embed, ingest, patterns
    conn = db.init()
    report = {"ingest": ingest.run(conn, workers=args.workers)}
    if not args.no_dedupe:
        report["dedupe"] = dedupe.run(conn)
    report["clusters"] = cluster.run(conn)
    patterns.run(conn)
    ingest.summarize_source_languages(conn)
    report["embeddings"] = embed.build(conn)
    report["exports"] = db.export_json(conn)
    counts = db.counts(conn)
    report["totals"] = counts
    conn.close()
    _emit(report, args.json)
    if not args.json:
        ing = report["ingest"]
        print(f"\n  ingest: {ing['discovered']} discovered, "
              f"{ing['analyzed']} analyzed, {ing['cached']} cached, "
              f"{ing['errors']} errors ({ing['elapsed_s']}s)")
        d = report.get("dedupe", {})
        print(f"  dedupe: {d.get('exact', 0)} exact, {d.get('near', 0)} near, "
              f"{d.get('similar_links', 0)} similar links")
        print(f"  clusters: {report['clusters'].get('clusters', 0)} "
              f"({report['clusters'].get('assigned', 0)} assets)")
        print(f"  patterns: {counts['patterns']} | exports: "
              f"{', '.join(report['exports'])}")
    return 0 if ing["errors"] == 0 else 1


def cmd_search(args) -> int:
    from . import db, search
    conn = db.init()
    try:
        if args.context_pack:
            pack = search.context_pack(conn, args.query, limit=args.limit)
            _emit(pack, True)  # context packs are always JSON
            return 0
        hits = search.search_conn(conn, args.query, limit=args.limit,
                                  media=args.media)
        if args.json:
            _emit([{
                "name": h.get("generated_name") or Path(h["original_path"]).name,
                "type": h["media_type"],
                "source": h.get("source_id"),
                "score": h.get("_score"),
                "parts": h.get("_parts"),
                "ui_category": h.get("ui_category"),
                "layout_pattern": h.get("layout_pattern"),
                "visual_style": h.get("visual_style"),
                "motion_category": h.get("motion_category"),
            } for h in hits], True)
            return 0
        if not hits:
            print("no matches â€” run `uiux ingest` first, or broaden the query")
            return 1
        for h in hits:
            name = h.get("generated_name") or Path(h["original_path"]).name
            src = h.get("source_id") or "-"
            parts = h.get("_parts", {})
            print(f"  {h['_score']:.3f}  [{h['media_type']:<5}] {name}")
            print(f"          source={src} lex={parts.get('lexical')} "
                  f"concept={parts.get('concept')} visual={parts.get('visual')}")
        return 0
    finally:
        conn.close()


def cmd_analyze(args) -> int:
    from . import classify, imagefeat, ingest, videofeat
    path = Path(args.path).resolve()
    if not path.exists():
        print(f"not found: {path}")
        return 1
    targets = [path] if path.is_file() else [
        p for p in sorted(path.rglob("*"))
        if p.is_file() and p.suffix.lower() in ingest.IMAGE_EXT | ingest.VIDEO_EXT]
    out = []
    for t in targets[:args.max]:
        kind = "video" if t.suffix.lower() in ingest.VIDEO_EXT else "image"
        if kind == "image":
            res = imagefeat.analyze_image(t)
            feats = res.pop("features")
            desc = res.pop("descriptor", None)
            classes = classify.classify_asset(t.name, feats)
            out.append({"file": str(t), "kind": kind,
                        "size": [res.get("width"), res.get("height")],
                        "palette": [p["hex"] for p in res.get("palette", [])],
                        "classification": classes,
                        "features": {k: round(v, 4) for k, v in feats.items()
                                     if isinstance(v, (int, float))}})
        else:
            res = videofeat.analyze_video(t, path_for_cache() / "analyze")
            out.append({"file": str(t), "kind": kind,
                        "duration": res.get("duration"),
                        "fps": res.get("fps"), "codec": res.get("codec"),
                        "keyframes": len(res.get("keyframes") or []),
                        "scene_cuts": res.get("scene_cuts"),
                        "motion": res.get("motion"),
                        "gaps": res.get("capability_gaps")})
    _emit(out, args.json)
    if not args.json:
        for entry in out:
            print(json.dumps(entry, ensure_ascii=False, indent=2)[:1400])
    return 0


def path_for_cache() -> Path:
    from .config import path_for
    return path_for("cache")


def cmd_init(args) -> int:
    from . import projectctx
    root = Path(args.project).resolve()
    if not root.is_dir():
        print(f"project directory not found: {root}")
        return 1
    answers = {}
    if args.answers:
        answers = json.loads(Path(args.answers).read_text(encoding="utf-8"))
    result = projectctx.init_project(root, answers)
    _emit({"written": result["written"],
           "direction": result["dna"]["direction"]["name"],
           "framework": result["context"]["framework"]}, args.json)
    if not args.json:
        ctx = result["context"]
        print(f"  project: {ctx['name']}")
        print(f"  framework: {', '.join(ctx['framework'])} | styling: "
              f"{ctx['styling']} | industry: {ctx['industry']}")
        print(f"  direction: {result['dna']['direction']['name']}")
        print(f"  written:")
        for w in result["written"]:
            print(f"    - {w}")
    return 0


def cmd_design(args) -> int:
    """Generate a fresh Design DNA from answers (no project files touched)."""
    from . import dna, projectctx
    if args.answers:
        raw = args.answers.strip()
        if raw.startswith("{"):
            answers = json.loads(raw)
        else:
            # utf-8-sig tolerates PowerShell's BOM
            answers = json.loads(Path(raw).read_text(encoding="utf-8-sig"))
    else:
        answers = {}
    if not answers.get("name"):
        answers["name"] = args.name or "unnamed-project"
    payload = dna.generate(answers)
    _emit(payload, args.json)
    if not args.json:
        md = projectctx.render_dna_md(payload)
        if args.out:
            out = Path(args.out)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(md, encoding="utf-8")
            print(f"  design DNA written to {out}")
        else:
            print(md)
    return 0


def cmd_build(args) -> int:
    """One-shot local pipeline: status -> references -> external engine
    lookups -> Design DNA -> routed plan. The agent then implements from
    the plan and runs review (per the uiux-engine skill)."""
    from . import db, doctor, projectctx, promax, search
    from .config import engine_root, path_for

    root = Path(args.project).resolve()
    prompt = args.prompt
    report: dict = {"prompt": prompt, "engine_root": str(engine_root())}

    # 1. state
    conn = db.init()
    report["index"] = db.counts(conn)

    # 2. references (context pack is the only model-facing payload)
    concept = " ".join(prompt.lower().split()[:6])
    report["references"] = search.context_pack(conn, concept, limit=8)

    # 3. external active-engine lookup (UI UX Pro Max, when present)
    pm = promax.invoke(prompt, design_system=True, variance=5, motion=5,
                       density=5, limit=2)
    report["uiux_pro_max"] = {"ok": pm.get("ok"),
                              "summary": (pm.get("output") or "")[:1200]
                              if pm.get("ok") else pm.get("reason")}

    # 4. project context + Design DNA
    if root.is_dir():
        ctx = projectctx.detect(root)
    else:
        ctx = {"name": root.name}
    ctx["product_type"] = prompt[:80]
    dna_payload = dna_payload_for(ctx)
    report["context"] = ctx
    report["dna"] = dna_payload

    # 5. write plan + dna
    out_dir = root / ".uiux" if root.is_dir() else path_for("index") / "plans"
    out_dir.mkdir(parents=True, exist_ok=True)
    dna_path = out_dir / "design-dna.md"
    if not dna_path.exists() or not root.is_dir():
        dna_path.write_text(projectctx.render_dna_md(dna_payload),
                            encoding="utf-8")
    plan_path = Path(args.out) if args.out else out_dir / "design-plan.md"
    plan_path.write_text(render_plan(prompt, report, dna_payload),
                         encoding="utf-8")
    report["plan"] = str(plan_path)
    report["dna_path"] = str(dna_path)
    conn.close()

    _emit(report, args.json)
    if not args.json:
        print(f"  prompt: {prompt}")
        print(f"  direction: {dna_payload['direction']['name']}")
        print(f"  references: {len(report['references']['references'])}")
        print(f"  ui-ux-pro-max: {'ok' if report['uiux_pro_max']['ok'] else 'fallback'}")
        print(f"  plan: {plan_path}")
        print(f"  dna:  {dna_path}")
    return 0


def dna_payload_for(ctx: dict) -> dict:
    from . import dna
    return dna.generate(ctx)


def render_plan(prompt: str, report: dict, payload: dict) -> str:
    """Implementation plan the agent follows after this command."""
    d = payload["direction"]
    p = payload["palette"]
    t = payload["typography"]
    m = payload["motion"]
    refs = report.get("references", {}).get("references", [])
    lines = [
        f"# Design Plan — {prompt}",
        "",
        f"Generated by `uiux build`. Implement per the uiux-engine skill:",
        "tokens -> components -> pages -> review.",
        "",
        "## Direction",
        f"- {d['name']}: {d['description']}",
        f"- Density {d['density']}, motion {d['motion']}, radius {d['radius']}",
        f"- Layout: nav={payload['layout']['navigation']}, "
        f"grid={payload['layout']['grid']}, hero={payload['layout']['hero']}",
        f"- Imagery: {payload['imagery']}",
        "",
        "## Tokens (design-dna.md is authoritative)",
        f"- Colors: bg `{p['background']}`, surface `{p['surface']}`, "
        f"text `{p['text']}`, muted `{p['muted']}`, accent `{p['accent']}`"
        + (f", accent2 `{p['accent2']}`" if p.get("accent2") else ""),
        f"- Type: {t['display']} / {t['body']} (scale {t['scale']})",
        f"- Motion: fast {m['fast']}ms, base {m['base']}ms, slow {m['slow']}ms, "
        f"easing `{m['easing']}`",
        "",
        "## References (principles only — never copy)",
    ]
    for r in refs:
        lines.append(f"- {r.get('ref')} [{r.get('type')}] "
                     f"({r.get('ui_category')}, {r.get('layout')}, {r.get('style')})")
    lines += [
        "",
        "## Implementation checklist",
        "1. Map tokens (Tailwind theme or CSS vars; alias existing names).",
        "2. Install libs only if the design needs them (framer-motion/gsap/three).",
        "3. Semantic HTML, focus/hover/active/disabled states, 44px targets.",
        "4. Responsive: mobile nav model, 320/768/1024/1440 classes.",
        "5. Reduced-motion equivalent for every choreographed effect.",
        "6. `uiux review <project>` -> fix all P0 -> re-run.",
        "",
        "## Methodology skills to consult (load max 2)",
        "- taste (design-taste-frontend): visual direction, anti-generic checks",
        "- frontend-design / motion-design / web-design-guidelines as needed",
        "",
    ]
    return "\n".join(lines)


def cmd_review(args) -> int:
    from . import review as reviewmod
    root = Path(args.project).resolve()
    if not root.is_dir():
        print(f"project not found: {root}")
        return 1
    result = reviewmod.review(root)
    report_path = reviewmod.render_report(root, result)
    _emit(result, args.json)
    if not args.json:
        print(f"  findings: {len(result['findings'])} "
              f"(high: {sum(1 for f in result['findings'] if f['severity'] == 'high')})")
        print(f"  report: {report_path}")
    return 0


def cmd_polish(args) -> int:
    from . import review as reviewmod
    root = Path(args.project).resolve()
    if not root.is_dir():
        print(f"project not found: {root}")
        return 1
    result = reviewmod.review(root)
    plan_path = reviewmod.polish_plan(root, result)
    _emit({"plan": str(plan_path), "findings": len(result["findings"])}, args.json)
    if not args.json:
        print(f"  polish plan: {plan_path}")
        print(f"  based on {len(result['findings'])} findings")
    return 0


def cmd_status(args) -> int:
    from . import db
    from .config import path_for
    conn = db.init()
    counts = db.counts(conn)
    last = db.get_meta(conn, "last_ingest_at")
    pending = 0
    inbox = path_for("inbox")
    if inbox.is_dir():
        from .ingest import IMAGE_EXT, VIDEO_EXT
        known = {r["original_path"] for r in conn.execute(
            "SELECT original_path FROM assets")}
        pending = sum(1 for p in inbox.rglob("*")
                      if p.is_file() and p.suffix.lower() in IMAGE_EXT | VIDEO_EXT
                      and str(p) not in known)
    conn.close()
    out = {"counts": counts, "last_ingest": last, "pending_inbox": pending,
           "engine_root": str(Path(__file__).resolve().parents[2])}
    _emit(out, args.json)
    if not args.json:
        print(f"  assets: {counts['assets']} ({counts['images']} images, "
              f"{counts['videos']} videos)")
        print(f"  sources: {counts['sources']} | clusters: {counts['clusters']} "
              f"| duplicates: {counts['duplicates']} | patterns: "
              f"{counts['patterns']}")
        print(f"  last ingest: {last or 'never'} | pending in INBOX: {pending}")
    return 0


def cmd_update(args) -> int:
    """Incremental refresh: ingest new/changed assets, rebuild knowledge."""
    return cmd_ingest(argparse.Namespace(no_dedupe=False, workers=0,
                                         json=args.json))


def cmd_version(_args) -> int:
    print(f"uiux engine {VERSIONS['engine']} (analyzer {VERSIONS['analyzer']}, "
          f"index {VERSIONS['index']}, schema {VERSIONS['schema']})")
    return 0


# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="uiux",
        description="UIUX ENGINE â€” local design intelligence (ingest, search, "
                    "design DNA, review).")
    sub = p.add_subparsers(dest="command", required=True)

    def add(name: str, **kw) -> argparse.ArgumentParser:
        s = sub.add_parser(name, **kw)
        # --json accepted both before and after the subcommand
        s.add_argument("--json", action="store_true",
                       help="machine-readable output")
        return s

    s = add("doctor", help="environment + capability report")
    s.set_defaults(func=cmd_doctor)

    s = add("ingest", help="index INBOX assets (analyze, name, dedupe, cluster)")
    s.add_argument("--workers", type=int, default=0)
    s.add_argument("--no-dedupe", action="store_true")
    s.set_defaults(func=cmd_ingest)

    s = add("search", help="semantic search over the reference library")
    s.add_argument("query")
    s.add_argument("-n", "--limit", type=int, default=None)
    s.add_argument("--media", choices=["image", "video"], default=None)
    s.add_argument("--context-pack", action="store_true",
                   help="emit the compact token-efficient pack for LLM context")
    s.set_defaults(func=cmd_search)

    s = add("analyze", help="analyze a file/folder without ingesting")
    s.add_argument("path")
    s.add_argument("--max", type=int, default=5)
    s.set_defaults(func=cmd_analyze)

    s = add("init", help="connect a project; detect framework/tokens; write .uiux/")
    s.add_argument("project", nargs="?", default=".")
    s.add_argument("--answers", help="path to a JSON file with industry/audience/etc.")
    s.set_defaults(func=cmd_init)

    s = add("design", help="generate a Design DNA from answers JSON")
    s.add_argument("--answers", help="inline JSON or path to answers file")
    s.add_argument("--name", default=None)
    s.add_argument("--out", help="write design-dna.md to this path")
    s.set_defaults(func=cmd_design)

    s = add("build", help="one-shot pipeline: search + route + DNA plan for a prompt")
    s.add_argument("prompt", help="what to design, e.g. 'premium industrial dashboard'")
    s.add_argument("--project", default=".", help="project path to attach/init")
    s.add_argument("--out", help="where to write the plan (default <project>\\.uiux\\design-plan.md)")
    s.set_defaults(func=cmd_build)

    s = add("review", help="static quality report for a project")
    s.add_argument("project", nargs="?", default=".")
    s.set_defaults(func=cmd_review)

    s = add("polish", help="prioritized fix plan for a project")
    s.add_argument("project", nargs="?", default=".")
    s.set_defaults(func=cmd_polish)

    s = add("status", help="index status and pending INBOX count")
    s.set_defaults(func=cmd_status)

    s = add("update", help="incremental ingest + knowledge rebuild")
    s.set_defaults(func=cmd_update)

    s = add("version", help="print versions")
    s.set_defaults(func=cmd_version)
    return p


def main(argv: list[str] | None = None) -> int:
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    parser = build_parser()
    args = parser.parse_args(argv)
    _setup_logging()
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\ninterrupted")
        return 130
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        log.exception("command failed")
        if getattr(args, "json", False):
            print(json.dumps({"error": str(exc), "type": type(exc).__name__}))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

