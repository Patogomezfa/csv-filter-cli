# Eatventure automation scaffold (mss + OpenCV + ADB)

Minimal demo for scrcpy-based game automation. Not a full bot — proves capture + template matching loop.

## Setup

```bash
cd deliverables/eatventure-bot
pip install -r requirements.txt
copy config.example.yaml config.yaml
# Add PNG templates under assets/ (chef, barista, upgrade button)
python run_demo.py --config config.yaml --save-frame frame.png
```

## Stack

- **Capture:** `mss` on scrcpy window region (fast, no adb screencap)
- **Vision:** OpenCV `matchTemplate` (+ perceptual hash extension on hire)
- **Input:** `adb shell input tap/swipe` via `bot/actions.py`

Built as portfolio/demo for r/slavelabour OpenCV task ($50–75).
