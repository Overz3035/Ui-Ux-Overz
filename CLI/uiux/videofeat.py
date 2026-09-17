"""Local video analysis via ffprobe/ffmpeg (build spec §10).

For each video we extract, entirely locally:
  duration, resolution, fps, codec, aspect ratio
  N representative keyframes (spread over the timeline)
  scene-change count (ffmpeg scene filter, when available)
  motion energy + vertical flow (frame-difference on decoded frames)
  per-keyframe perceptual hashes (dedup) and visual descriptors (search)

Videos are NEVER sent to a language model; only the compact metadata and a
few extracted thumbnails are stored.
"""

from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path
from typing import Any

from . import imagefeat
from .config import get
from .hashing import ahash
from .tools import find_tool, run

MOTION_CATEGORIES = (
    "hover", "scroll", "parallax", "page_transition", "navigation", "card",
    "button", "cursor", "micro_interaction", "loading", "hero", "three_d",
    "shader", "liquid", "text_animation", "background", "misc",
)


def ffprobe_json(path: Path) -> dict | None:
    ffprobe = find_tool("ffprobe")
    if not ffprobe:
        return None
    ok, out, _err = run([
        ffprobe, "-v", "error", "-print_format", "json", "-show_format",
        "-show_streams", str(path),
    ], timeout=60)
    if not ok:
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return None


def probe(path: Path) -> dict:
    """Structured metadata from ffprobe, with sane fallbacks."""
    meta: dict[str, Any] = {
        "duration": None, "width": None, "height": None, "fps": None,
        "codec": None, "bit_rate": None,
    }
    data = ffprobe_json(path)
    if not data:
        return meta
    fmt = data.get("format", {})
    try:
        meta["duration"] = round(float(fmt.get("duration", 0)), 3) or None
    except (TypeError, ValueError):
        pass
    br = fmt.get("bit_rate")
    try:
        meta["bit_rate"] = int(br) if br else None
    except (TypeError, ValueError):
        pass
    video = next((s for s in data.get("streams", [])
                  if s.get("codec_type") == "video"), None)
    if video:
        meta["codec"] = video.get("codec_name")
        meta["width"] = video.get("width")
        meta["height"] = video.get("height")
        rate = video.get("avg_frame_rate") or video.get("r_frame_rate") or "0/1"
        try:
            num, den = rate.split("/")
            meta["fps"] = round(float(num) / float(den), 3) if float(den) else None
        except (ValueError, ZeroDivisionError):
            pass
    return meta


def _ffmpeg_extract(path: Path, out_dir: Path, count: int,
                    max_side: int, contact: bool) -> dict:
    """Extract keyframes + a contact sheet. Returns paths + scene count."""
    ffmpeg = find_tool("ffmpeg")
    result: dict[str, Any] = {"keyframes": [], "contact_sheet": None,
                              "scene_cuts": None, "error": None}
    if not ffmpeg:
        result["error"] = "ffmpeg not found"
        return result
    out_dir.mkdir(parents=True, exist_ok=True)
    # 1) scene-change count (cheap, decodes once)
    ok, _out, err = run([
        ffmpeg, "-hide_banner", "-i", str(path),
        "-vf", "select='gt(scene,0.30)',metadata=print:file=-",
        "-an", "-f", "null", "-",
    ], timeout=180)
    if ok:
        result["scene_cuts"] = err.count("lavfi.scene_score") or 0
    # 2) uniformly spread keyframes (decode is per-frame; use fps filter trick)
    dur_probe = ffprobe_json(path)
    dur = 0.0
    try:
        dur = float(dur_probe.get("format", {}).get("duration", 0) or 0)
    except (TypeError, ValueError, AttributeError):
        pass
    if dur <= 0:
        result["error"] = result["error"] or "no duration"
        return result
    step = max(dur / max(count, 1), 0.1)
    for i in range(count):
        ts = min(i * step + step * 0.5, max(dur - 0.05, 0.05))
        out = out_dir / f"kf-{i:02d}.jpg"
        ok, _o, _e = run([
            ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
            "-ss", f"{ts:.3f}", "-i", str(path), "-frames:v", "1",
            "-vf", f"scale='if(gt(iw,ih),{max_side},-1)':'if(gt(iw,ih),-1,{max_side})'",
            str(out),
        ], timeout=60)
        if ok and out.exists() and out.stat().st_size > 0:
            result["keyframes"].append(out)
    # 3) contact sheet (PIL-based: deterministic, no xstack layout fiddling)
    if contact and result["keyframes"]:
        sheet = out_dir / "contact-sheet.jpg"
        result["contact_sheet"] = _contact_sheet_pil(result["keyframes"], sheet)
    return result


def _contact_sheet_pil(keyframes: list[Path], out: Path) -> str | None:
    try:
        from PIL import Image
    except ImportError:
        return None
    imgs = []
    for k in keyframes[:8]:
        try:
            with Image.open(k) as im:
                im.load()
                im.thumbnail((320, 320))
                imgs.append(im.convert("RGB").copy())
        except Exception:
            continue
    if not imgs:
        return None
    cols = 4
    rows = (len(imgs) + cols - 1) // cols
    cw = max(im.width for im in imgs)
    ch = max(im.height for im in imgs)
    sheet = Image.new("RGB", (cols * cw, rows * ch), (24, 24, 24))
    for i, im in enumerate(imgs):
        sheet.paste(im, ((i % cols) * cw, (i // cols) * ch))
    sheet.save(out, quality=82)
    return out.name


def motion_metrics(path: Path, sample: int = 24) -> dict:
    """Frame-difference metrics: total motion energy and vertical flow.

    Decodes at a tiny scale for speed; values are relative (0..1)."""
    ffmpeg = find_tool("ffmpeg")
    if not ffmpeg:
        return {}
    # run() returns decoded bytes; do it inline because we need binary stdout.
    try:
        proc = subprocess.run(
            [ffmpeg, "-hide_banner", "-loglevel", "error", "-i", str(path),
             "-vf", "scale=96:54,format=gray", "-f", "rawvideo",
             "-pix_fmt", "gray", "-"],
            capture_output=True, timeout=120, check=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        out = proc.stdout
    except (OSError, subprocess.TimeoutExpired):
        return {}
    frame = 96 * 54
    frames = []
    buf = out
    while len(buf) >= frame and len(frames) < sample:
        frames.append(buf[:frame])
        buf = buf[frame:]
    if len(frames) < 3:
        return {}
    import numpy as np
    arr = np.frombuffer(b"".join(frames), dtype=np.uint8)
    arr = arr.reshape(len(frames), 54, 96).astype(np.float32) / 255.0
    diffs = np.abs(np.diff(arr, axis=0))
    motion_energy = float(diffs.mean())
    # vertical flow: how much of the change happens along the y axis
    dy = np.abs(np.diff(diffs, axis=1)).mean()
    dx = np.abs(np.diff(diffs, axis=2)).mean()
    vertical_flow = float(dy / (dy + dx)) if (dy + dx) > 1e-6 else 0.5
    return {
        "motion_energy": round(min(motion_energy * 8.0, 1.0), 4),
        "vertical_flow": round(vertical_flow, 4),
        "sampled_frames": len(frames),
    }


def analyze_video(path: Path, work_dir: Path) -> dict[str, Any]:
    """Full local analysis of one video file."""
    meta = probe(path)
    settings = {
        "keyframes": int(get("video_analysis.keyframes", 8)),
        "max_side": int(get("video_analysis.keyframe_max_side", 640)),
        "contact": bool(get("video_analysis.contact_sheet", True)),
        "sample": int(get("video_analysis.motion_sample_frames", 24)),
    }
    result: dict[str, Any] = {**meta, "settings": settings,
                              "keyframes": [], "capability_gaps": []}
    ext = get("video_analysis.enabled", "auto")
    if str(ext).lower() in ("false", "0", "no", "off"):
        result["capability_gaps"].append("video_analysis_disabled")
        return result
    if not find_tool("ffmpeg"):
        result["capability_gaps"].append("ffmpeg_missing")
        return result

    extraction = _ffmpeg_extract(path, work_dir, settings["keyframes"],
                                 settings["max_side"], settings["contact"])
    result["keyframes"] = [str(p.name) for p in extraction["keyframes"]]
    result["contact_sheet"] = extraction.get("contact_sheet")
    result["scene_cuts"] = extraction.get("scene_cuts")
    result["motion"] = motion_metrics(path, settings["sample"])
    if extraction.get("error"):
        result["capability_gaps"].append(extraction["error"])

    # Per-keyframe analysis: hashes + descriptors + palette of the middle frame
    kf_hashes: list[str] = []
    descriptors = []
    middle = None
    for i, kfp in enumerate(extraction["keyframes"]):
        try:
            rgb, orig = imagefeat.load_rgb(kfp, max_side=256)
        except Exception:
            continue
        kf_hashes.append(ahash(imagefeat.to_gray(rgb)))
        descriptors.append(imagefeat.visual_descriptor(
            rgb, imagefeat.extract_features(rgb, orig), []))
        if i == len(extraction["keyframes"]) // 2:
            middle = (rgb, orig)
    result["kf_hashes"] = kf_hashes
    if descriptors:
        import numpy as np
        result["descriptor"] = np.mean(descriptors, axis=0)
    if middle:
        rgb, orig = middle
        result["palette"] = imagefeat.dominant_palette(rgb)
        result["feats"] = imagefeat.extract_features(rgb, orig)
    if not kf_hashes:
        result["capability_gaps"].append("no_keyframes_extracted")
    w, h = meta.get("width"), meta.get("height")
    if w and h:
        result["aspect"] = round(w / h, 4)
    return result
