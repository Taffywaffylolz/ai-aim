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

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Populate model weights:

```bash
python scripts/bootstrap_models.py
```

Run with a profile:

```bash
ai-aimbot --profile valorant --monitor 1 --fps 120
```

or point directly to a YAML profile:

```bash
ai-aimbot --profile configs/cs2.yaml
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
