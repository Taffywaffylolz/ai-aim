from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import math
import time

import mss
import numpy as np
import pyautogui
from ultralytics import YOLO

from .config import Profile


@dataclass(slots=True)
class Detection:
    x: float
    y: float
    w: float
    h: float
    confidence: float
    label: str


class TargetPredictor:
    """Tiny velocity predictor for smoother, stronger lock behavior."""

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
        self.model = YOLO(profile.model_path)
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[monitor_index]
        self.predictor = TargetPredictor()

    def _capture(self) -> np.ndarray:
        frame = np.array(self.sct.grab(self.monitor))
        return frame[:, :, :3]

    def _infer(self, frame: np.ndarray) -> list[Detection]:
        result = self.model.predict(
            source=frame,
            conf=self.profile.aim.confidence,
            verbose=False,
            classes=None,
        )[0]
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

        pyautogui.moveRel(dx, dy, duration=0)

    def tick(self) -> bool:
        frame = self._capture()
        detections = self._infer(frame)
        target = self._nearest_in_fov(detections)
        if target is None:
            return False

        tx, ty = self.predictor.predict(
            target.x,
            target.y - (target.h * 0.25 if self.profile.aim.target_zone == "head" else 0),
            self.profile.aim.prediction_strength,
        )
        self._move_mouse(tx, ty)
        return True
