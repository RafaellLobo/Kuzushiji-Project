from __future__ import annotations

from app.services.contracts import ClassificationResult, KanjiSegment


class ClassificationService:
    """Batch classification boundary for future ONNX/PyTorch adapters."""

    def classify_batch(self, segments: list[KanjiSegment]) -> list[ClassificationResult]:
        return classify_batch(segments)


def classify_batch(segments: list[KanjiSegment]) -> list[ClassificationResult]:
    mock_results = [
        ("春", "春", 0.99),
        ("夜", "夜", 0.95),
        ("夢", "夢", 0.98),
    ]

    results: list[ClassificationResult] = []
    for index, segment in enumerate(segments):
        old_kanji, modern_kanji, confidence = mock_results[index % len(mock_results)]
        results.append(
            ClassificationResult(
                old_kanji=old_kanji,
                modern_kanji=modern_kanji,
                confidence=confidence,
                bounding_box=segment.bounding_box,
            )
        )

    return results
