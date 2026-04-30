from __future__ import annotations

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.contracts import BoundingBox, ClassificationResult, ImageMatrix, KanjiSegment
from app.services.errors import NoKanjiFoundError, TranslationFailedError
from app.services.image_decoder import ImageDecoder
from app.services.translation_pipeline import TranslationPipeline


def encode_test_image() -> bytes:
    image = np.zeros((64, 64, 3), dtype=np.uint8)
    success, encoded = cv2.imencode(".jpg", image)
    assert success
    return encoded.tobytes()


class FakeSegmentationService:
    def __init__(self, segments: list[KanjiSegment]) -> None:
        self.segments = segments

    def segment_and_normalize(self, image_bgr: ImageMatrix) -> list[KanjiSegment]:
        return self.segments


class FakeClassificationService:
    def __init__(self, results: list[ClassificationResult]) -> None:
        self.results = results

    def classify_batch(self, segments: list[KanjiSegment]) -> list[ClassificationResult]:
        return self.results


class FakeTranslationService:
    def __init__(self, translation: str = "Dragon", should_fail: bool = False) -> None:
        self.translation = translation
        self.should_fail = should_fail

    async def translate_to_english(self, japanese_text: str) -> str:
        if self.should_fail:
            raise TranslationFailedError()
        return self.translation


def build_segment() -> KanjiSegment:
    return KanjiSegment(
        order=1,
        crop=np.zeros((28, 28, 3), dtype=np.uint8),
        bounding_box=BoundingBox(x=1, y=2, w=28, h=28),
    )


@pytest.mark.anyio
async def test_pipeline_returns_no_kanji_found_when_segmentation_is_empty() -> None:
    pipeline = TranslationPipeline(
        image_decoder=ImageDecoder(),
        segmentation_service=FakeSegmentationService([]),
        classification_service=FakeClassificationService([]),
        translation_service=FakeTranslationService(),
    )

    with pytest.raises(NoKanjiFoundError):
        await pipeline.process(encode_test_image(), "image/jpeg")


@pytest.mark.anyio
async def test_pipeline_surfaces_translation_failure() -> None:
    segment = build_segment()
    pipeline = TranslationPipeline(
        image_decoder=ImageDecoder(),
        segmentation_service=FakeSegmentationService([segment]),
        classification_service=FakeClassificationService(
            [ClassificationResult(old_kanji="龍", modern_kanji="竜", confidence=0.97)]
        ),
        translation_service=FakeTranslationService(should_fail=True),
    )

    with pytest.raises(TranslationFailedError):
        await pipeline.process(encode_test_image(), "image/jpeg")


@pytest.mark.anyio
async def test_pipeline_success_preserves_public_response_shape() -> None:
    segment = build_segment()
    pipeline = TranslationPipeline(
        image_decoder=ImageDecoder(),
        segmentation_service=FakeSegmentationService([segment]),
        classification_service=FakeClassificationService(
            [ClassificationResult(old_kanji="龍", modern_kanji="竜", confidence=0.97)]
        ),
        translation_service=FakeTranslationService("Dragon"),
    )

    response = await pipeline.process(encode_test_image(), "image/jpeg")

    assert response["success"] is True
    assert response["data"]["characters"] == [
        {
            "order": 1,
            "old_kanji": "龍",
            "modern_kanji": "竜",
            "confidence": 0.97,
            "bounding_box": {"x": 1, "y": 2, "w": 28, "h": 28},
        }
    ]
    assert response["data"]["japanese_text"] == "竜"
    assert response["data"]["english_translation"] == "Dragon"
    assert isinstance(response["data"]["processing_time_ms"], int)
    assert response["error"] is None


def test_translate_endpoint_accepts_valid_image() -> None:
    with TestClient(app) as client:
        files = {"image": ("sample.jpg", encode_test_image(), "image/jpeg")}
        response = client.post("/translate", files=files)

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["japanese_text"] == "春夜夢"
