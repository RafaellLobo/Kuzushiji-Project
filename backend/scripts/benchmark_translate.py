from __future__ import annotations

import statistics
import sys
from pathlib import Path
from time import perf_counter

import cv2
import numpy as np
from fastapi.testclient import TestClient

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app


def encode_image(width: int, height: int) -> bytes:
    image = np.zeros((height, width, 3), dtype=np.uint8)
    success, encoded = cv2.imencode(".jpg", image)
    if not success:
        raise RuntimeError("Failed to encode benchmark image.")
    return encoded.tobytes()


def run(iterations: int = 20) -> None:
    samples_ms: list[float] = []
    image_bytes = encode_image(width=640, height=480)

    with TestClient(app) as client:
        for _ in range(iterations):
            started_at = perf_counter()
            response = client.post(
                "/translate",
                files={"image": ("benchmark.jpg", image_bytes, "image/jpeg")},
            )
            response.raise_for_status()
            samples_ms.append((perf_counter() - started_at) * 1000)

    print(
        "translate endpoint benchmark: "
        f"iterations={iterations} "
        f"avg_ms={statistics.mean(samples_ms):.2f} "
        f"p95_ms={statistics.quantiles(samples_ms, n=20)[18]:.2f}"
    )


if __name__ == "__main__":
    run()
