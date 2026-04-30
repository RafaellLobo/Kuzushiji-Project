from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray


ImageMatrix = NDArray[np.uint8]


@dataclass(frozen=True, slots=True)
class BoundingBox:
    x: int
    y: int
    w: int
    h: int

    def to_dict(self) -> dict[str, int]:
        return {"x": self.x, "y": self.y, "w": self.w, "h": self.h}


@dataclass(frozen=True, slots=True)
class KanjiSegment:
    order: int
    crop: ImageMatrix
    bounding_box: BoundingBox


@dataclass(frozen=True, slots=True)
class ClassificationResult:
    old_kanji: str
    modern_kanji: str
    confidence: float
    bounding_box: BoundingBox | None = None

    def to_response(self, order: int, fallback_box: BoundingBox) -> dict[str, Any]:
        bounding_box = self.bounding_box or fallback_box
        return {
            "order": order,
            "old_kanji": self.old_kanji,
            "modern_kanji": self.modern_kanji,
            "confidence": self.confidence,
            "bounding_box": bounding_box.to_dict(),
        }
