from pathlib import Path

from ultralytics import YOLO

GAMES = ["valorant", "apex", "fortnite", "cs2", "overwatch2"]


def main() -> None:
    model = YOLO("yolov8n.pt")
    weights = Path(model.ckpt_path)
    for game in GAMES:
        out = Path("models") / game / f"yolov8n-{game}.pt"
        out.write_bytes(weights.read_bytes())
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
