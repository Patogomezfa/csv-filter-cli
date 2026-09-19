"""ADB input helpers for tap / swipe-hold."""

from __future__ import annotations

import subprocess
from typing import Optional


def _base_cmd(device: Optional[str]) -> list[str]:
    cmd = ["adb"]
    if device:
        cmd.extend(["-s", device])
    return cmd


def tap(x: int, y: int, device: Optional[str] = None) -> None:
    subprocess.run(
        _base_cmd(device) + ["shell", "input", "tap", str(x), str(y)],
        check=True,
    )


def swipe_hold(
    x: int,
    y: int,
    hold_ms: int,
    device: Optional[str] = None,
) -> None:
    """Simulate press-and-hold with a short swipe to same point."""
    duration = max(hold_ms, 50)
    subprocess.run(
        _base_cmd(device)
        + [
            "shell",
            "input",
            "swipe",
            str(x),
            str(y),
            str(x),
            str(y),
            str(duration),
        ],
        check=True,
    )
