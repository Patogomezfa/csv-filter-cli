"""Fast screen capture via mss (scrcpy window region)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import mss
import numpy as np


@dataclass(frozen=True)
class Region:
    left: int
    top: int
    width: int
    height: int

    @classmethod
    def from_sequence(cls, values: Tuple[int, int, int, int]) -> "Region":
        left, top, width, height = values
        return cls(left=left, top=top, width=width, height=height)

    def as_mss_dict(self) -> dict:
        return {
            "left": self.left,
            "top": self.top,
            "width": self.width,
            "height": self.height,
        }


def grab_bgr(region: Region) -> np.ndarray:
    """Return BGR frame suitable for OpenCV."""
    with mss.mss() as sct:
        raw = np.array(sct.grab(region.as_mss_dict()))
    # mss returns BGRA
    return raw[:, :, :3].copy()
