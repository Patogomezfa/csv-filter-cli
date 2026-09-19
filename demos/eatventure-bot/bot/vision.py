"""Template matching utilities for menu / station detection."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np


@dataclass(frozen=True)
class Match:
    score: float
    top_left: Tuple[int, int]
    bottom_right: Tuple[int, int]

    @property
    def center(self) -> Tuple[int, int]:
        x1, y1 = self.top_left
        x2, y2 = self.bottom_right
        return ((x1 + x2) // 2, (y1 + y2) // 2)


def load_template(path: Path) -> np.ndarray:
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Template not found: {path}")
    return img


def best_match(
    frame_bgr: np.ndarray,
    template_bgr: np.ndarray,
    threshold: float = 0.8,
) -> Optional[Match]:
    result = cv2.matchTemplate(frame_bgr, template_bgr, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    if max_val < threshold:
        return None
    h, w = template_bgr.shape[:2]
    x, y = max_loc
    return Match(
        score=float(max_val),
        top_left=(x, y),
        bottom_right=(x + w, y + h),
    )


def phash(bgr: np.ndarray, hash_size: int = 8) -> int:
    """Perceptual hash — faster icon checks than full template scan each frame."""
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (hash_size + 1, hash_size), interpolation=cv2.INTER_AREA)
    diff = resized[:, 1:] > resized[:, :-1]
    bits = diff.flatten()
    value = 0
    for bit in bits:
        value = (value << 1) | int(bit)
    return value


def hamming(a: int, b: int) -> int:
    return (a ^ b).bit_count()


def icon_hash(path: Path, hash_size: int = 8) -> int:
    return phash(load_template(path), hash_size)


def should_skip_row(
    frame_bgr: np.ndarray,
    icon_paths: list[Path],
    threshold: float,
    *,
    icon_hashes: list[int] | None = None,
    hash_distance: int = 12,
) -> bool:
    """True if chef or barista icon appears in the current menu row crop."""
    if icon_hashes:
        crop_hash = phash(frame_bgr)
        for ref in icon_hashes:
            if hamming(crop_hash, ref) <= hash_distance:
                return True
    for path in icon_paths:
        if path.exists() and best_match(frame_bgr, load_template(path), threshold):
            return True
    return False
