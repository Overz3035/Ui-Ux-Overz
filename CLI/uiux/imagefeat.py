"""Local image analysis: numeric features, palette, hashes, descriptor.

Everything here runs on the local machine with Pillow + numpy only. No image
is ever sent to a language model (build spec §9, §29). The output is a compact
feature dict that the rule-based classifier and the search index consume.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageFile

from . import VERSIONS
from .config import get
from .hashing import ahash, dhash, phash

ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = 300_000_000

FEATURE_KEYS = (
    "width", "height", "aspect", "megapixels", "brightness", "contrast",
    "saturation", "colorfulness", "edge_density", "text_density",
    "dark_ratio", "light_ratio", "hue_spread", "unique_colors",
    "vertical_structure", "horizontal_structure", "corner_radius_hint",
    "grid_score", "panel_score", "warm_ratio", "cool_ratio", "neutral_ratio",
)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
def load_rgb(path: Path, max_side: int | None = None) -> tuple[np.ndarray, tuple[int, int]]:
    """Return (float RGB array in 0..1, original (w, h))."""
    max_side = max_side or int(get("image_analysis.work_size", 512))
    with Image.open(path) as im:
        im.load()
        orig = (im.width, im.height)
        if im.mode in ("P", "LA", "RGBA", "La"):
            bg = Image.new("RGB", im.size, (255, 255, 255))
            conv = im.convert("RGBA")
            bg.paste(conv, mask=conv.split()[-1])
            im = bg
        elif im.mode != "RGB":
            im = im.convert("RGB")
        scale = max_side / float(max(im.size)) if max(im.size) > max_side else 1.0
        if scale < 1.0:
            im = im.resize(
                (max(1, int(im.width * scale)), max(1, int(im.height * scale))),
                Image.Resampling.BILINEAR,
            )
        arr = np.asarray(im, dtype=np.float32) / 255.0
    return arr, orig


def array_from_pil(im: Image.Image, max_side: int = 512) -> np.ndarray:
    if im.mode != "RGB":
        im = im.convert("RGB")
    scale = max_side / float(max(im.size)) if max(im.size) > max_side else 1.0
    if scale < 1.0:
        im = im.resize(
            (max(1, int(im.width * scale)), max(1, int(im.height * scale))),
            Image.Resampling.BILINEAR,
        )
    return np.asarray(im, dtype=np.float32) / 255.0


# ---------------------------------------------------------------------------
# Colour space helpers
# ---------------------------------------------------------------------------
def to_gray(rgb: np.ndarray) -> np.ndarray:
    return rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722


def to_hsv(rgb: np.ndarray) -> np.ndarray:
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx = rgb.max(axis=-1)
    mn = rgb.min(axis=-1)
    diff = mx - mn
    hue = np.zeros_like(mx)
    mask = diff > 1e-6
    with np.errstate(invalid="ignore", divide="ignore"):
        rm = (mx == r) & mask
        gm = (mx == g) & mask & ~rm
        bm = (mx == b) & mask & ~rm & ~gm
        hue[rm] = ((g - b)[rm] / diff[rm]) % 6.0
        hue[gm] = ((b - r)[gm] / diff[gm]) + 2.0
        hue[bm] = ((r - g)[bm] / diff[bm]) + 4.0
    hue = hue / 6.0
    sat = np.where(mx > 1e-6, diff / np.maximum(mx, 1e-6), 0.0)
    return np.stack([hue, sat, mx], axis=-1)


def srgb_to_oklab(rgb: np.ndarray) -> np.ndarray:
    """Linear-light sRGB -> OKLab. Perceptually uniform, good for clustering."""
    c = np.clip(rgb, 0.0, 1.0)
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = lin[..., 0], lin[..., 1], lin[..., 2]
    l_ = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m_ = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s_ = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = np.cbrt(l_), np.cbrt(m_), np.cbrt(s_)
    return np.stack([
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    ], axis=-1)


# ---------------------------------------------------------------------------
# Structure primitives
# ---------------------------------------------------------------------------
def sobel(gray: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return (gx, gy) using a 3x3 Sobel via array shifts (no scipy needed)."""
    g = np.pad(gray, 1, mode="edge")
    gx = (
        -1 * g[:-2, :-2] + 1 * g[:-2, 2:]
        - 2 * g[1:-1, :-2] + 2 * g[1:-1, 2:]
        - 1 * g[2:, :-2] + 1 * g[2:, 2:]
    ) / 4.0
    gy = (
        -1 * g[:-2, :-2] - 2 * g[:-2, 1:-1] - 1 * g[:-2, 2:]
        + 1 * g[2:, :-2] + 2 * g[2:, 1:-1] + 1 * g[2:, 2:]
    ) / 4.0
    return gx, gy


def box_blur(a: np.ndarray, radius: int = 1) -> np.ndarray:
    """Separable box blur via cumulative sums."""
    if radius < 1:
        return a
    k = 2 * radius + 1

    def blur1(x: np.ndarray, axis: int) -> np.ndarray:
        pad = [(0, 0)] * x.ndim
        pad[axis] = (radius, radius)
        xp = np.pad(x, pad, mode="edge")
        cs = np.cumsum(xp, axis=axis)
        zero_shape = list(cs.shape)
        zero_shape[axis] = 1
        cs = np.concatenate([np.zeros(zero_shape, dtype=cs.dtype), cs], axis=axis)
        hi = np.take(cs, np.arange(k, k + x.shape[axis]), axis=axis)
        lo = np.take(cs, np.arange(0, x.shape[axis]), axis=axis)
        return (hi - lo) / float(k)

    return blur1(blur1(a, 0), 1)


def _peakiness(profile: np.ndarray, ignore_border: float = 0.06) -> float:
    """How much a 1-D profile is dominated by a few sharp interior peaks."""
    n = profile.size
    if n < 8:
        return 0.0
    b = max(1, int(n * ignore_border))
    core = profile[b:-b]
    if core.size < 4 or core.max() <= 1e-9:
        return 0.0
    norm = core / core.max()
    med = float(np.median(norm))
    return float(np.clip((1.0 - med) * (norm > 0.55).mean() * 3.2, 0.0, 1.0))


def _periodicity(profile: np.ndarray) -> float:
    """Strength of the best non-trivial autocorrelation peak (grid rhythm)."""
    n = profile.size
    if n < 16:
        return 0.0
    x = profile - profile.mean()
    denom = float((x * x).sum())
    if denom <= 1e-9:
        return 0.0
    ac = np.correlate(x, x, mode="full")[n - 1:] / denom
    lo, hi = max(2, n // 32), max(4, n // 2)
    window = ac[lo:hi]
    if window.size == 0:
        return 0.0
    return float(np.clip(window.max(), 0.0, 1.0))


def _long_run_mask(binary: np.ndarray, length: int, axis: int) -> np.ndarray:
    """Pixels belonging to a straight run of at least ``length`` along ``axis``.

    UI chrome (panel borders, table rules, dividers) produces long straight
    runs; photographic and 3D content almost never does. This is the signal
    that separates "interface" from "image".
    """
    n = binary.shape[axis]
    if n < length or length < 2:
        return np.zeros_like(binary, dtype=bool)
    cs = np.cumsum(binary.astype(np.int32), axis=axis)
    pad = [(0, 0), (0, 0)]
    pad[axis] = (1, 0)
    cs = np.pad(cs, pad, mode="constant")
    lo = np.take(cs, np.arange(0, n - length + 1), axis=axis)
    hi = np.take(cs, np.arange(length, n + 1), axis=axis)
    starts = (hi - lo) == length
    out = np.zeros_like(binary, dtype=bool)
    for shift in range(length):
        sl = [slice(None), slice(None)]
        sl[axis] = slice(shift, shift + starts.shape[axis])
        out[tuple(sl)] |= starts
    return out


def _rectilinearity(strong_edge: np.ndarray) -> tuple[float, np.ndarray]:
    """Fraction of strong edges on long straight runs, plus the run mask."""
    total = float(strong_edge.sum())
    if total < 32:
        return 0.0, np.zeros_like(strong_edge, dtype=bool)
    span = max(10, int(min(strong_edge.shape) * 0.06))
    runs = (_long_run_mask(strong_edge, span, axis=1)
            | _long_run_mask(strong_edge, span, axis=0))
    return float(runs.sum() / total), runs


def _entropy(hist: np.ndarray) -> float:
    p = hist / max(hist.sum(), 1e-9)
    p = p[p > 0]
    if p.size == 0:
        return 0.0
    return float(-(p * np.log2(p)).sum() / math.log2(max(hist.size, 2)))


# ---------------------------------------------------------------------------
# Feature extraction
# ---------------------------------------------------------------------------
def extract_features(rgb: np.ndarray, orig_size: tuple[int, int]) -> dict[str, float]:
    """Compute the numeric feature vector used by classification and search."""
    h, w = rgb.shape[:2]
    gray = to_gray(rgb)
    hsv = to_hsv(rgb)
    hue, sat, val = hsv[..., 0], hsv[..., 1], hsv[..., 2]

    ow, oh = orig_size
    feats: dict[str, float] = {
        "width": float(ow),
        "height": float(oh),
        "aspect": float(ow) / float(max(oh, 1)),
        "megapixels": (ow * oh) / 1_000_000.0,
    }

    # --- tone -------------------------------------------------------------
    feats["brightness"] = float(gray.mean())
    feats["contrast"] = float(gray.std())
    feats["dark_ratio"] = float((gray < 0.28).mean())
    feats["light_ratio"] = float((gray > 0.72).mean())

    # --- colour -----------------------------------------------------------
    feats["saturation"] = float(sat.mean())
    # Hasler & Susstrunk colourfulness on opponent channels.
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    rg = r - g
    yb = 0.5 * (r + g) - b
    feats["colorfulness"] = float(
        np.clip(
            (math.hypot(float(rg.std()), float(yb.std()))
             + 0.3 * math.hypot(float(rg.mean()), float(yb.mean()))) * 1.8,
            0.0, 1.0,
        )
    )
    # Hue spread only counts reasonably saturated pixels; grey has no hue.
    strong = sat > 0.16
    if strong.sum() > 32:
        hue_hist, _ = np.histogram(hue[strong], bins=36, range=(0.0, 1.0))
        feats["hue_spread"] = _entropy(hue_hist.astype(np.float64))
        hh = hue[strong]
        feats["warm_ratio"] = float(((hh < 0.11) | (hh > 0.92)).mean())
        feats["cool_ratio"] = float(((hh > 0.44) & (hh < 0.75)).mean())
    else:
        feats["hue_spread"] = 0.0
        feats["warm_ratio"] = 0.0
        feats["cool_ratio"] = 0.0
    feats["neutral_ratio"] = float((sat <= 0.16).mean())
    q = (np.stack([r, g, b], axis=-1) * 15.0).astype(np.int16)
    codes = q[..., 0] * 256 + q[..., 1] * 16 + q[..., 2]
    feats["unique_colors"] = float(
        np.clip(np.unique(codes).size / 900.0, 0.0, 1.0)
    )

    # --- edges / detail ---------------------------------------------------
    gx, gy = sobel(gray)
    mag = np.hypot(gx, gy)
    thresh = max(0.055, float(np.percentile(mag, 82)) * 0.55)
    edges = mag > thresh
    feats["edge_density"] = float(edges.mean())

    # Text produces fine detail that survives at full scale but disappears
    # when the image is blurred: use the fine/coarse energy ratio, gated by
    # local bimodality (text is dark-on-light or light-on-dark).
    coarse = box_blur(gray, 2)
    fine = np.abs(gray - coarse)
    local_var = box_blur(gray * gray, 1) - box_blur(gray, 1) ** 2
    bimodal = local_var > 0.0035
    text_mask = (fine > 0.055) & bimodal
    raw_text = float(text_mask.mean())
    # Small connected specks (glyph strokes) rather than large shapes.
    speck = float((text_mask & ~box_blur(text_mask.astype(np.float32), 3).astype(bool)).mean())
    feats["text_density"] = float(np.clip(raw_text * 0.85 + speck * 1.6, 0.0, 1.0))

    # --- layout structure -------------------------------------------------
    vert_energy = np.abs(gx).mean(axis=0)      # per-column
    horiz_energy = np.abs(gy).mean(axis=1)     # per-row
    feats["vertical_structure"] = _peakiness(vert_energy)
    feats["horizontal_structure"] = max(
        _peakiness(horiz_energy), _periodicity(horiz_energy) * 0.9
    )
    feats["grid_score"] = float(
        np.clip(
            0.5 * _periodicity(vert_energy) + 0.5 * _periodicity(horiz_energy)
            + 0.15 * min(feats["vertical_structure"], feats["horizontal_structure"]),
            0.0, 1.0,
        )
    )

    # Panels: flat regions bounded by long straight rules. Rectilinearity is
    # measured over *runs*, so photographic edge clutter does not inflate it.
    flat = local_var < 0.0012
    strong_edge = mag > max(0.06, float(np.percentile(mag, 88)))
    rect, run_mask = _rectilinearity(strong_edge)
    feats["panel_score"] = float(
        np.clip(flat.mean() * 0.28 + rect * 0.92 + feats["grid_score"] * 0.16,
                0.0, 1.0)
    )
    # Curvature: diagonal edge energy that is NOT part of a straight run.
    curved = strong_edge & ~run_mask & (np.abs(gx) > 0.04) & (np.abs(gy) > 0.04)
    feats["corner_radius_hint"] = float(
        np.clip(curved.sum() / max(float(strong_edge.sum()), 1.0) * 1.6, 0.0, 1.0)
    )

    return {k: float(round(v, 6)) for k, v in feats.items()}


def dominant_palette(rgb: np.ndarray, n: int = 6, iters: int = 12) -> list[dict]:
    """k-means in OKLab so clusters follow perception, not RGB distance."""
    lab = srgb_to_oklab(rgb).reshape(-1, 3)
    if lab.shape[0] > 20000:
        idx = np.linspace(0, lab.shape[0] - 1, 20000).astype(int)
        sample = lab[idx]
    else:
        sample = lab
    n = int(max(1, min(n, sample.shape[0])))
    # Deterministic seeding: spread over lightness order (repeatable runs).
    order = np.argsort(sample[:, 0])
    seeds = sample[order[np.linspace(0, len(order) - 1, n).astype(int)]].copy()
    for _ in range(iters):
        d = ((sample[:, None, :] - seeds[None, :, :]) ** 2).sum(axis=2)
        who = d.argmin(axis=1)
        moved = 0.0
        for k in range(n):
            members = sample[who == k]
            if members.size:
                new = members.mean(axis=0)
                moved = max(moved, float(np.abs(new - seeds[k]).max()))
                seeds[k] = new
        if moved < 1e-4:
            break
    d = ((sample[:, None, :] - seeds[None, :, :]) ** 2).sum(axis=2)
    who = d.argmin(axis=1)
    out: list[dict] = []
    for k in range(n):
        ratio = float((who == k).mean())
        if ratio <= 0.002:
            continue
        srgb = oklab_to_srgb(seeds[k])
        out.append({
            "hex": "#%02x%02x%02x" % tuple(int(round(c * 255)) for c in srgb),
            "ratio": round(ratio, 4),
            "oklab": [round(float(x), 4) for x in seeds[k]],
        })
    out.sort(key=lambda d_: -d_["ratio"])
    return out


def oklab_to_srgb(lab: np.ndarray) -> np.ndarray:
    l_, a, b = float(lab[0]), float(lab[1]), float(lab[2])
    l = l_ + 0.3963377774 * a + 0.2158037573 * b
    m = l_ - 0.1055613458 * a - 0.0638541728 * b
    s = l_ - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l ** 3, m ** 3, s ** 3
    lin = np.array([
        +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    ])
    lin = np.clip(lin, 0.0, 1.0)
    return np.where(lin <= 0.0031308, lin * 12.92, 1.055 * lin ** (1 / 2.4) - 0.055)


def compute_hashes(rgb: np.ndarray) -> dict[str, str]:
    gray = to_gray(rgb)
    cfg_a = int(get("image_analysis.ahash_bits", 8))
    cfg_d = int(get("image_analysis.dhash_bits", 8))
    cfg_p = int(get("image_analysis.phash_bits", 8))
    return {
        "ahash": ahash(gray, cfg_a),
        "dhash": dhash(gray, cfg_d),
        "phash": phash(gray, cfg_p),
    }


def analyzer_version() -> str:
    return str(VERSIONS.get("analyzer", "0"))


# ---------------------------------------------------------------------------
# Visual descriptor  (the "visual-stat" embedding provider, build spec §14)
# ---------------------------------------------------------------------------
DESCRIPTOR_DIM = 288
_ASPECT_EDGES = (0.5, 0.65, 0.8, 0.95, 1.15, 1.45, 1.7, 1.9, 2.4)


def _resample(profile: np.ndarray, bins: int) -> np.ndarray:
    n = profile.size
    if n == 0:
        return np.zeros(bins, dtype=np.float32)
    edges = np.linspace(0, n, bins + 1).astype(int)
    out = np.empty(bins, dtype=np.float32)
    for i in range(bins):
        a, b = edges[i], max(edges[i] + 1, edges[i + 1])
        out[i] = profile[a:b].mean()
    return out


def visual_descriptor(rgb: np.ndarray, feats: dict[str, float],
                      palette: list[dict]) -> np.ndarray:
    """Deterministic 288-D visual descriptor.

    Composition (documented so the layer stays swappable):
      27  RGB 3x3x3 joint histogram      | coarse colour identity
      32  hue histogram                  | palette character
       8  saturation histogram           | vividness distribution
      16  lightness histogram            | dark/light surface signature
      45  3x3 grid x (L,a,b,edge,text)   | spatial composition
      32  column edge-energy profile     | vertical layout rhythm
      32  row edge-energy profile        | horizontal layout rhythm
      16  gradient orientation histogram | geometry (axis vs organic)
       8  4-level detail pyramid         | scale of detail
      24  top-6 palette (L,a,b,ratio)    | dominant colour structure
      16  row-band text density          | where the copy sits
      10  aspect bucket one-hot          | viewport class
      22  scalar feature block           | interpretable summary
    """
    h, w = rgb.shape[:2]
    gray = to_gray(rgb)
    hsv = to_hsv(rgb)
    lab = srgb_to_oklab(rgb)
    gx, gy = sobel(gray)
    mag = np.hypot(gx, gy)
    parts: list[np.ndarray] = []

    q = np.clip((rgb * 3).astype(np.int16), 0, 2)
    codes = (q[..., 0] * 9 + q[..., 1] * 3 + q[..., 2]).ravel()
    parts.append(np.bincount(codes, minlength=27).astype(np.float32) / codes.size)

    strong = hsv[..., 1] > 0.14
    hue_vals = hsv[..., 0][strong]
    hist_h = (np.histogram(hue_vals, bins=32, range=(0, 1))[0].astype(np.float32)
              / max(hue_vals.size, 1)) if hue_vals.size else np.zeros(32, np.float32)
    parts.append(hist_h)
    parts.append(np.histogram(hsv[..., 1], bins=8, range=(0, 1))[0].astype(np.float32) / gray.size)
    parts.append(np.histogram(gray, bins=16, range=(0, 1))[0].astype(np.float32) / gray.size)

    coarse = box_blur(gray, 2)
    fine = np.abs(gray - coarse)
    grid = np.zeros((3, 3, 5), dtype=np.float32)
    ys = np.linspace(0, h, 4).astype(int)
    xs = np.linspace(0, w, 4).astype(int)
    for i in range(3):
        for jj in range(3):
            y0, y1 = ys[i], max(ys[i] + 1, ys[i + 1])
            x0, x1 = xs[jj], max(xs[jj] + 1, xs[jj + 1])
            cell_lab = lab[y0:y1, x0:x1]
            grid[i, jj] = (
                float(cell_lab[..., 0].mean()),
                float(cell_lab[..., 1].mean()) + 0.5,
                float(cell_lab[..., 2].mean()) + 0.5,
                float((mag[y0:y1, x0:x1] > 0.08).mean()),
                float((fine[y0:y1, x0:x1] > 0.055).mean()),
            )
    parts.append(grid.ravel())

    parts.append(_resample(np.abs(gx).mean(axis=0), 32))
    parts.append(_resample(np.abs(gy).mean(axis=1), 32))

    ang = np.arctan2(gy, gx)
    sel = mag > max(0.05, float(np.percentile(mag, 80)))
    if sel.sum() > 16:
        oh = np.histogram(ang[sel] % math.pi, bins=16, range=(0, math.pi))[0]
        parts.append(oh.astype(np.float32) / max(oh.sum(), 1))
    else:
        parts.append(np.zeros(16, np.float32))

    pyramid = []
    cur = gray
    for _ in range(4):
        blurred = box_blur(cur, 1)
        pyramid.extend([float(np.abs(cur - blurred).mean()) * 6.0,
                        float((np.hypot(*sobel(cur)) > 0.08).mean())])
        cur = cur[::2, ::2] if min(cur.shape) > 8 else cur
    parts.append(np.array(pyramid, dtype=np.float32))

    pal = np.zeros((6, 4), dtype=np.float32)
    for i, entry in enumerate(palette[:6]):
        ok = entry.get("oklab") or [0, 0, 0]
        pal[i] = (float(ok[0]), float(ok[1]) + 0.5, float(ok[2]) + 0.5,
                  float(entry.get("ratio", 0.0)))
    parts.append(pal.ravel())

    band_text = np.zeros(16, dtype=np.float32)
    bys = np.linspace(0, h, 17).astype(int)
    for i in range(16):
        y0, y1 = bys[i], max(bys[i] + 1, bys[i + 1])
        band_text[i] = float((fine[y0:y1] > 0.055).mean())
    parts.append(band_text)

    bucket = np.zeros(10, dtype=np.float32)
    aspect = feats.get("aspect", 1.0)
    idx = int(np.searchsorted(np.array(_ASPECT_EDGES), aspect))
    bucket[min(idx, 9)] = 1.0
    parts.append(bucket)

    parts.append(np.array([float(feats.get(k, 0.0)) for k in FEATURE_KEYS],
                          dtype=np.float32))

    vec = np.concatenate(parts).astype(np.float32)
    if vec.size < DESCRIPTOR_DIM:
        vec = np.pad(vec, (0, DESCRIPTOR_DIM - vec.size))
    elif vec.size > DESCRIPTOR_DIM:
        vec = vec[:DESCRIPTOR_DIM]
    vec = np.nan_to_num(vec, nan=0.0, posinf=0.0, neginf=0.0)
    norm = float(np.linalg.norm(vec))
    return vec / norm if norm > 1e-8 else vec


def analyze_image(path: Path) -> dict[str, Any]:
    """Full local analysis of one image file."""
    rgb, orig = load_rgb(path)
    feats = extract_features(rgb, orig)
    palette = dominant_palette(rgb, int(get("image_analysis.palette_colors", 6)))
    hashes = compute_hashes(rgb)
    return {
        "features": feats,
        "palette": palette,
        "descriptor": visual_descriptor(rgb, feats, palette),
        "width": int(orig[0]),
        "height": int(orig[1]),
        "aspect": feats["aspect"],
        **hashes,
    }
