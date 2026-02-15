from __future__ import annotations

import argparse
import math
import time
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any, Iterable, TypeVar


T = TypeVar("T")


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


@dataclass(slots=True)
class Detection:
    x: float
    y: float
    w: float
    h: float
    confidence: float
    label: str


def project_root() -> Path:
    return Path(__file__).resolve().parent


def resolve_existing_path(path: str | Path) -> Path:
    candidate = Path(path)
    probes = [candidate, project_root() / candidate]
    for probe in probes:
        if probe.exists():
            return probe.resolve()
    attempted = ", ".join(str(p) for p in probes)
    raise FileNotFoundError(f"Could not locate path '{path}'. Tried: {attempted}")


def normalize_project_relative(path: str | Path) -> str:
    candidate = Path(path)
    if candidate.is_absolute():
        return str(candidate)
    return str((project_root() / candidate).resolve())


def dataclass_from_dict(cls: type[T], payload: dict[str, Any] | None) -> T:
    payload = payload or {}
    allowed = {f.name for f in fields(cls)}
    filtered = {k: v for k, v in payload.items() if k in allowed}
    return cls(**filtered)


DEFAULT_PROFILE_MAP: dict[str, str] = {
    "valorant": "configs/valorant.yaml",
    "apex": "configs/apex.yaml",
    "fortnite": "configs/fortnite.yaml",
    "cs2": "configs/cs2.yaml",
    "overwatch2": "configs/overwatch2.yaml",
}


class ProfileLoader:
    @staticmethod
    def load(path: str | Path) -> Profile:
        config_path = resolve_existing_path(path)
        try:
            import yaml
        except ImportError as exc:
            raise RuntimeError("Missing runtime dependency PyYAML. Install with: pip install -r requirements.txt") from exc

        with config_path.open("r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)

        required = {"name", "game", "model_path", "classes"}
        missing = required - set(raw or {})
        if missing:
            raise ValueError(f"Missing required config keys: {sorted(missing)}")

        return Profile(
            name=raw["name"],
            game=raw["game"],
            model_path=normalize_project_relative(raw["model_path"]),
            classes=list(raw["classes"]),
            aim=dataclass_from_dict(AimTuning, raw.get("aim")),
            keybinds=dataclass_from_dict(Keybinds, raw.get("keybinds")),
        )


class TargetPredictor:
    def __init__(self) -> None:
        self._last: tuple[float, float] | None = None
        self._last_time: float | None = None

    def predict(self, x: float, y: float, strength: float) -> tuple[float, float]:
        now = time.time()
        if self._last is None or self._last_time is None:
            self._last = (x, y)
            self._last_time = now
            return x, y

        dt = max(now - self._last_time, 1e-3)
        vx = (x - self._last[0]) / dt
        vy = (y - self._last[1]) / dt

        self._last = (x, y)
        self._last_time = now
        return x + vx * strength * 0.01, y + vy * strength * 0.01


class AimbotEngine:
    def __init__(self, profile: Profile, monitor_index: int = 1) -> None:
        self.profile = profile
        try:
            import mss
            import pyautogui
            from ultralytics import YOLO
        except ImportError as exc:
            raise RuntimeError(
                "Missing runtime dependency. Install with: pip install -r requirements.txt"
            ) from exc

        self._mss = mss
        self._pyautogui = pyautogui
        self.model = YOLO(profile.model_path)
        self.sct = self._mss.mss()
        self.monitor = self.sct.monitors[monitor_index]
        self.predictor = TargetPredictor()

    def _capture(self) -> Any:
        import numpy as np

        frame = np.array(self.sct.grab(self.monitor))
        return frame[:, :, :3]

    def _infer(self, frame: Any) -> list[Detection]:
        result = self.model.predict(source=frame, conf=self.profile.aim.confidence, verbose=False)[0]
        labels = self.model.names
        detections: list[Detection] = []
        for box in result.boxes:
            cls_id = int(box.cls.item())
            label = labels.get(cls_id, str(cls_id))
            if label not in self.profile.classes:
                continue
            xywh = box.xywh[0].tolist()
            detections.append(
                Detection(
                    x=xywh[0],
                    y=xywh[1],
                    w=xywh[2],
                    h=xywh[3],
                    confidence=float(box.conf.item()),
                    label=label,
                )
            )
        return detections

    def _nearest_in_fov(self, detections: Iterable[Detection]) -> Detection | None:
        cx = self.monitor["width"] / 2
        cy = self.monitor["height"] / 2
        fov = self.profile.aim.fov_radius
        best: tuple[float, Detection] | None = None
        for det in detections:
            dist = math.dist((cx, cy), (det.x, det.y))
            if dist > fov:
                continue
            if best is None or dist < best[0]:
                best = (dist, det)
        return best[1] if best else None

    def _move_mouse(self, target_x: float, target_y: float) -> None:
        cx = self.monitor["width"] / 2
        cy = self.monitor["height"] / 2
        dx = (target_x - cx) * self.profile.aim.smoothing
        dy = (target_y - cy) * self.profile.aim.smoothing
        dy -= self.profile.aim.recoil_compensation * 20
        max_speed = self.profile.aim.max_speed
        dx = max(-max_speed, min(max_speed, dx))
        dy = max(-max_speed, min(max_speed, dy))
        self._pyautogui.moveRel(dx, dy, duration=0)

    def tick(self) -> bool:
        frame = self._capture()
        target = self._nearest_in_fov(self._infer(frame))
        if target is None:
            return False
        head_offset = target.h * 0.25 if self.profile.aim.target_zone == "head" else 0
        tx, ty = self.predictor.predict(target.x, target.y - head_offset, self.profile.aim.prediction_strength)
        self._move_mouse(tx, ty)
        return True


def resolve_profile(profile_arg: str) -> str:
    if profile_arg.endswith(".yaml"):
        return profile_arg
    if profile_arg not in DEFAULT_PROFILE_MAP:
        raise SystemExit(f"Unknown profile '{profile_arg}'. Choose from: {', '.join(DEFAULT_PROFILE_MAP)}")
    return DEFAULT_PROFILE_MAP[profile_arg]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="YOLOv8 ONNX configurable aim engine")
    parser.add_argument("--profile", default="valorant", help="Profile name or path to YAML")
    parser.add_argument("--monitor", type=int, default=1, help="MSS monitor index")
    parser.add_argument("--fps", type=float, default=120.0, help="Loop cap")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    profile = ProfileLoader.load(resolve_profile(args.profile))
    engine = AimbotEngine(profile=profile, monitor_index=args.monitor)
    frame_time = 1 / args.fps

    while True:
        start = time.time()
        engine.tick()
        elapsed = time.time() - start
        time.sleep(max(0.0, frame_time - elapsed))


if __name__ == "__main__":
    main()
