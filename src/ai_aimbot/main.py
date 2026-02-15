from __future__ import annotations

import argparse
import time

from .config import ProfileLoader, list_profiles
from .engine import AimbotEngine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="YOLOv8 AI aimbot engine")
    parser.add_argument("--profile", default="valorant", help="Profile name or path to YAML")
    parser.add_argument("--monitor", type=int, default=1, help="MSS monitor index")
    parser.add_argument("--fps", type=float, default=120.0, help="Loop cap")
    return parser.parse_args()


def resolve_profile(profile_arg: str) -> str:
    if profile_arg.endswith(".yaml"):
        return profile_arg
    profiles = list_profiles()
    if profile_arg not in profiles:
        raise SystemExit(f"Unknown profile '{profile_arg}'. Choose from: {', '.join(profiles)}")
    return profiles[profile_arg]


def main() -> None:
    args = parse_args()
    profile_path = resolve_profile(args.profile)
    profile = ProfileLoader.load(profile_path)
    engine = AimbotEngine(profile=profile, monitor_index=args.monitor)

    frame_time = 1 / args.fps
    while True:
        start = time.time()
        engine.tick()
        elapsed = time.time() - start
        time.sleep(max(0.0, frame_time - elapsed))


if __name__ == "__main__":
    main()
