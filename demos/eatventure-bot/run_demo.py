"""One-shot demo: capture region + report template matches (no ADB required)."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from bot.capture import Region, grab_bgr
from bot.vision import best_match, load_template


def main() -> None:
    parser = argparse.ArgumentParser(description="Eatventure bot — capture + match demo")
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to config (copy from config.example.yaml)",
    )
    parser.add_argument("--save-frame", default="", help="Optional path to save screenshot")
    args = parser.parse_args()

    cfg_path = Path(args.config)
    if not cfg_path.exists():
        raise SystemExit(
            f"Missing {cfg_path}. Copy config.example.yaml → config.yaml and set monitor region."
        )

    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    region = Region.from_sequence(tuple(cfg["capture"]["monitor"]))
    frame = grab_bgr(region)

    if args.save_frame:
        import cv2

        cv2.imwrite(args.save_frame, frame)
        print(f"Saved frame → {args.save_frame}")

    threshold = float(cfg.get("thresholds", {}).get("template_match", 0.82))
    templates = cfg.get("templates", {})
    for name, rel in templates.items():
        path = Path(rel)
        if not path.exists():
            print(f"[skip] {name}: template missing ({path})")
            continue
        match = best_match(frame, load_template(path), threshold)
        if match:
            print(f"[hit] {name}: score={match.score:.3f} center={match.center}")
        else:
            print(f"[miss] {name}: below threshold {threshold}")


if __name__ == "__main__":
    main()
