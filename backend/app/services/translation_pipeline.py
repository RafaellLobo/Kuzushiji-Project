from __future__ import annotations

from time import perf_counter
from typing import Any

from app.services.classifier import ClassificationService
from app.services.contracts import BoundingBox
from app.services.errors import ClassifierNotIntegratedError, NoKanjiFoundError
from app.services.image_decoder import ImageDecoder
from app.services.translator import TranslationService
from app.services.yolo_agent import SegmentationService


class TranslationPipeline:
    def __init__(
        self,
        image_decoder: ImageDecoder,
        segmentation_service: SegmentationService,
        classification_service: ClassificationService,
        translation_service: TranslationService,
    ) -> None:
        self.image_decoder = image_decoder
        self.segmentation_service = segmentation_service
        self.classification_service = classification_service
        self.translation_service = translation_service

    async def process(self, image_bytes: bytes, content_type: str | None) -> dict[str, Any]:
        started_at = perf_counter()
        image_bgr = self.image_decoder.decode(image_bytes, content_type)
        segments = self.segmentation_service.segment_and_normalize(image_bgr)

        if not segments:
            raise NoKanjiFoundError()

        classification_results = self.classification_service.classify_batch(segments)
        if len(classification_results) != len(segments):
            raise ClassifierNotIntegratedError("Classificador retornou quantidade invalida de resultados.")

        characters = [
            result.to_response(order=segment.order, fallback_box=segment.bounding_box)
            for segment, result in zip(segments, classification_results)
        ]
        japanese_text = "".join(character["modern_kanji"] for character in characters)
        english_translation = await self.translation_service.translate_to_english(japanese_text)

        return {
            "success": True,
            "data": {
                "characters": characters,
                "japanese_text": japanese_text,
                "english_translation": english_translation,
                "processing_time_ms": int((perf_counter() - started_at) * 1000),
            },
            "error": None,
        }


def build_demo_translation_response() -> dict[str, Any]:
    demo_characters = [
        {
            "order": 1,
            "old_kanji": "春",
            "modern_kanji": "春",
            "confidence": 0.98,
            "bounding_box": BoundingBox(x=120, y=80, w=32, h=36).to_dict(),
        },
        {
            "order": 2,
            "old_kanji": "風",
            "modern_kanji": "風",
            "confidence": 0.97,
            "bounding_box": BoundingBox(x=120, y=125, w=30, h=34).to_dict(),
        },
        {
            "order": 3,
            "old_kanji": "花",
            "modern_kanji": "花",
            "confidence": 0.96,
            "bounding_box": BoundingBox(x=120, y=168, w=31, h=35).to_dict(),
        },
        {
            "order": 4,
            "old_kanji": "鳥",
            "modern_kanji": "鳥",
            "confidence": 0.95,
            "bounding_box": BoundingBox(x=120, y=212, w=33, h=37).to_dict(),
        },
    ]

    return {
        "success": True,
        "data": {
            "characters": demo_characters,
            "japanese_text": "春風花鳥",
            "english_translation": "Spring breeze, flowers and birds.",
            "processing_time_ms": 42.0,
            "demo_mode": True,
        },
        "error": None,
    }


def build_translation_pipeline(translation_service: TranslationService) -> TranslationPipeline:
    return TranslationPipeline(
        image_decoder=ImageDecoder(),
        segmentation_service=SegmentationService(),
        classification_service=ClassificationService(),
        translation_service=translation_service,
    )
