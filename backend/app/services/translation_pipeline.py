from __future__ import annotations

from time import perf_counter
from typing import Any

from app.services.classifier import ClassificationService
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
        segments = self.segmentation_service.normalize_single_character(image_bgr)

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


def build_translation_pipeline(translation_service: TranslationService) -> TranslationPipeline:
    return TranslationPipeline(
        image_decoder=ImageDecoder(),
        segmentation_service=SegmentationService(),
        classification_service=ClassificationService(),
        translation_service=translation_service,
    )
