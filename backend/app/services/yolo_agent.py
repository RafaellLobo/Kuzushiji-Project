from __future__ import annotations

import cv2

from app.services.contracts import BoundingBox, ImageMatrix, KanjiSegment


class SegmentationService:
    """Adapter boundary for YOLO/ONNX/PyTorch segmentation runtimes."""

    def segment_and_normalize(self, image_bgr: ImageMatrix) -> list[KanjiSegment]:
        return segment_and_normalize(image_bgr)


def segment_and_normalize(image_bgr: ImageMatrix) -> list[KanjiSegment]:
    """
    Development adapter until the trained YOLO model is plugged in.

    The contract is already production-shaped: receive an OpenCV BGR matrix and
    return ordered 28x28 crops plus bounding boxes, without disk I/O.
    """
    height, width = image_bgr.shape[:2]
    if height == 0 or width == 0:
        return []

    crop_size = min(height, width, 96)
    y = max((height - crop_size) // 2, 0)
    step = max(crop_size // 2, 1)
    segment_count = 3
    segments: list[KanjiSegment] = []

    for index in range(segment_count):
        x = min(index * step, max(width - crop_size, 0))
        crop = image_bgr[y : y + crop_size, x : x + crop_size]
        normalized_crop = cv2.resize(crop, (28, 28), interpolation=cv2.INTER_AREA)
        segments.append(
            KanjiSegment(
                order=index + 1,
                crop=normalized_crop,
                bounding_box=BoundingBox(x=x, y=y, w=crop.shape[1], h=crop.shape[0]),
            )
        )

    return segments
