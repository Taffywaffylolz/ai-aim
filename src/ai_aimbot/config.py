from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass(slots=True)
class AimTuning:
    confidence: float = 0.45
    fov_radius: int = 260
    smoothing: float = 0.25
    max_speed: float = 60.0
    prediction_strength: float = 0.7
    recoil_compensation: float = 0.08
    target_zone: str = "head"
    triggerbot: bool = False


@dataclass(slots=True)
class Keybinds:
    hold_to_aim: str = "alt"
    toggle_on: str = "f8"
    panic_off: str = "f12"


@dataclass(slots=True)
class Profile:
    name: str
    game: str
    model_path: str
    classes: list[str]
    aim: AimTuning = field(default_factory=AimTuning)
    keybinds: Keybinds = field(default_factory=Keybinds)


def _project_root() -> Path:
    # src/ai_aimbot/config.py -> repository root
    return Path(__file__).resolve().parents[2]


def _resolve_existing_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute() and candidate.exists():
        return candidate

    probes = [candidate, _project_root() / candidate]
    for probe in probes:
        if probe.exists():
            return probe

    attempted = ", ".join(str(p) for p in probes)
    raise FileNotFoundError(f"Could not locate path '{path}'. Tried: {attempted}")


def _normalize_project_relative(path: str | Path) -> str:
    candidate = Path(path)
    if candidate.is_absolute():
        return str(candidate)
    return str((_project_root() / candidate).resolve())


class ProfileLoader:
    """Loads game profiles and provides a validated Profile object."""

    @staticmethod
    def load(path: str | Path) -> Profile:
        path = _resolve_existing_path(path)
        with path.open("r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)

        required = {"name", "game", "model_path", "classes"}
        missing = required - set(raw or {})
        if missing:
            raise ValueError(f"Missing required config keys: {sorted(missing)}")

        aim = AimTuning(**(raw.get("aim") or {}))
        keybinds = Keybinds(**(raw.get("keybinds") or {}))

        model_path = _normalize_project_relative(raw["model_path"])

        return Profile(
            name=raw["name"],
            game=raw["game"],
            model_path=model_path,
            classes=list(raw["classes"]),
            aim=aim,
            keybinds=keybinds,
        )


DEFAULT_PROFILE_MAP: dict[str, str] = {
    "valorant": "configs/valorant.yaml",
    "apex": "configs/apex.yaml",
    "fortnite": "configs/fortnite.yaml",
    "cs2": "configs/cs2.yaml",
    "overwatch2": "configs/overwatch2.yaml",
}


def list_profiles() -> dict[str, str]:
    return DEFAULT_PROFILE_MAP.copy()
