"""Content and perceptual hashing (build spec §12, §30).

* ``content_hash``  - SHA-256 of the file bytes; drives exact dedup + cache.
* ``ahash/dhash/phash`` - 64-bit perceptual hashes computed with numpy only,
  so no extra dependency is needed. Hamming distance between them expresses
  visual similarity.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np

_HEX_BITS = 16  # 64 bits -> 16 hex chars


def file_hash(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            block = fh.read(chunk)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def quick_signature(path: Path) -> str:
    """Cheap change detector: size + mtime. Used before the full hash."""
    st = path.stat()
    return f"{st.st_size}:{int(st.st_mtime)}"


def _bits_to_hex(bits: np.ndarray) -> str:
    flat = bits.astype(np.uint8).flatten()
    value = 0
    for b in flat:
        value = (value << 1) | int(b)
    return f"{value:0{_HEX_BITS}x}"


def ahash(gray: np.ndarray, size: int = 8) -> str:
    """Average hash: is each cell brighter than the mean?"""
    small = _resize_gray(gray, size, size)
    return _bits_to_hex(small > small.mean())


def dhash(gray: np.ndarray, size: int = 8) -> str:
    """Difference hash: horizontal gradient direction per cell."""
    small = _resize_gray(gray, size + 1, size)
    return _bits_to_hex(small[:, 1:] > small[:, :-1])


def phash(gray: np.ndarray, size: int = 8, factor: int = 4) -> str:
    """Perceptual hash via a separable DCT-II on a low-res grayscale image."""
    n = size * factor
    small = _resize_gray(gray, n, n).astype(np.float64)
    basis = _dct_matrix(n)
    coeffs = basis @ small @ basis.T
    block = coeffs[:size, :size].copy()
    dc = block[0, 0]
    block[0, 0] = 0.0
    med = np.median(block)
    bits = block > med
    bits[0, 0] = dc > med
    return _bits_to_hex(bits)


def _dct_matrix(n: int) -> np.ndarray:
    k = np.arange(n).reshape(-1, 1)
    x = np.arange(n).reshape(1, -1)
    m = np.cos(np.pi * (2 * x + 1) * k / (2 * n))
    m[0, :] *= np.sqrt(1.0 / n)
    m[1:, :] *= np.sqrt(2.0 / n)
    return m


def _resize_gray(gray: np.ndarray, w: int, h: int) -> np.ndarray:
    """Box-average resize. Avoids a Pillow round-trip for hash-sized images."""
    src_h, src_w = gray.shape[:2]
    if (src_w, src_h) == (w, h):
        return gray.astype(np.float64)
    ys = (np.linspace(0, src_h, h + 1)).astype(int)
    xs = (np.linspace(0, src_w, w + 1)).astype(int)
    out = np.empty((h, w), dtype=np.float64)
    for i in range(h):
        y0, y1 = ys[i], max(ys[i] + 1, ys[i + 1])
        row = gray[y0:y1]
        for jj in range(w):
            x0, x1 = xs[jj], max(xs[jj] + 1, xs[jj + 1])
            out[i, jj] = row[:, x0:x1].mean()
    return out


def hamming(a: str | None, b: str | None) -> int:
    """Hamming distance between two hex hashes; 64 when either is missing."""
    if not a or not b:
        return 64
    try:
        return bin(int(a, 16) ^ int(b, 16)).count("1")
    except ValueError:
        return 64


def similarity(a: str | None, b: str | None, bits: int = 64) -> float:
    return 1.0 - (hamming(a, b) / float(bits))


def aggregate_video_hash(frame_hashes: list[str]) -> str:
    """Fold per-keyframe hashes into one signature for video dedup.

    Bitwise majority vote across keyframes: stable against a few outlier
    frames while still separating genuinely different clips.
    """
    if not frame_hashes:
        return ""
    mats = []
    for h in frame_hashes:
        try:
            v = int(h, 16)
        except (TypeError, ValueError):
            continue
        mats.append([(v >> i) & 1 for i in range(63, -1, -1)])
    if not mats:
        return ""
    arr = np.array(mats, dtype=np.uint8)
    majority = (arr.mean(axis=0) >= 0.5).astype(np.uint8)
    value = 0
    for b in majority:
        value = (value << 1) | int(b)
    return f"{value:0{_HEX_BITS}x}"
