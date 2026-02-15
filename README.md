# AI Aim (YOLOv8)

A configurable YOLOv8-based aim assistant framework with game-specific profiles, neon-purple ImGui styling utilities, and a high-refresh aiming loop.

## Included features

- YOLOv8 inference loop for target detection (`ultralytics`).
- Game profile system with per-title tuning and per-game model paths.
- Built-in profiles for Valorant, Apex, Fortnite, CS2, and Overwatch 2.
- Aggressive aim tuning controls (FOV, smoothing, max speed, prediction, recoil compensation).
- Predictive target tracking for stronger lock behavior.
- Neon purple ImGui theme preset.
- CLI entry point: `ai-aimbot`.

## How to run the app

### 1) Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

### 2) Populate model weights

This copies a base YOLOv8 model into each game folder so every built-in profile resolves to an existing `.pt` file.

```bash
python scripts/bootstrap_models.py
```

### 3) Run with a built-in profile

```bash
ai-aimbot --profile valorant --monitor 1 --fps 120
```

### 4) Or run with a custom YAML profile path

```bash
ai-aimbot --profile configs/cs2.yaml
```

### 5) Useful runtime flags

- `--profile`: built-in profile name (`valorant`, `apex`, `fortnite`, `cs2`, `overwatch2`) or path to a YAML file.
- `--monitor`: `mss` monitor index (default `1`).
- `--fps`: main loop target FPS (default `120`).

### Troubleshooting

- If `ai-aimbot` is not found, run it as a module:

  ```bash
  PYTHONPATH=src python -m ai_aimbot --profile valorant
  ```

- If you see `ImportError: attempted relative import with no known parent package` when running `python main.py`, run from the repo root with one of these:

  ```bash
  python -m ai_aimbot --profile valorant
  # or
  PYTHONPATH=src python src/ai_aimbot/main.py --profile valorant
  ```

- If dependencies fail to install, verify you have access to a Python package index and try:

  ```bash
  pip install -e .
  ```

## Profile format

Each game profile includes:

- `model_path`
- target `classes`
- aim tuning (`confidence`, `fov_radius`, `smoothing`, `max_speed`, `prediction_strength`, `recoil_compensation`, `target_zone`, `triggerbot`)
- keybind definitions

See `configs/*.yaml` for templates.

## ImGui theme

Use `ai_aimbot.ui_theme.apply_neon_purple_theme()` after ImGui context creation.

## Notes

This repository provides a technical framework and profile structure. To get strong performance per game, you should train or fine-tune each `models/<game>/yolov8n-<game>.pt` on game-specific datasets.
