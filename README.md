# AI Aim (single-file version)

This project now runs from **one Python file**: `ai_aimbot.py`.

## Files

- `ai_aimbot.py` → all runtime logic (config loading, model loading, inference loop).
- `requirements.txt` → dependencies.
- `configs/*.yaml` → per-game settings.
- `models/<game>/*.onnx` → per-game ONNX model files.

## Run

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python ai_aimbot.py --profile valorant --monitor 1 --fps 120
```

You can also use a custom config path:

```bash
python ai_aimbot.py --profile configs/cs2.yaml
```

## Important

- Configs now point to `.onnx` models.
- Place model files at paths matching each config (example: `models/valorant/yolov8n-valorant.onnx`).
