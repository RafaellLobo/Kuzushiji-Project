from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict
from pathlib import Path

import cv2
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

plt.show = lambda *args, **kwargs: None

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.services.classifier import ClassificationService  # noqa: E402
from app.services.contracts import KanjiSegment  # noqa: E402
from app.services.yolo_agent import DetectedBox, SegmentationService  # noqa: E402


def iou(a: DetectedBox, b: DetectedBox) -> float:
    x1 = max(a.x1, b.x1)
    y1 = max(a.y1, b.y1)
    x2 = min(a.x2, b.x2)
    y2 = min(a.y2, b.y2)
    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    area_a = a.width * a.height
    area_b = b.width * b.height
    union = area_a + area_b - intersection
    return float(intersection / union) if union else 0.0


def save_image(path: Path, image: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ok = cv2.imwrite(str(path), image)
    if not ok:
        raise RuntimeError(f"Falha ao salvar imagem: {path}")


def observe_crop(crop: np.ndarray, crop_original_shape: tuple[int, ...], duplicate_iou: float) -> str:
    notes = []
    if crop.shape != (28, 28):
        notes.append("shape_invalido")
    if crop.dtype != np.uint8:
        notes.append("dtype_invalido")
    if crop.size and int(crop.max()) == 0:
        notes.append("vazio")
    if crop.size and float(np.mean(crop <= 8)) < 0.35:
        notes.append("fundo_claro_ou_ruido")
    ys, xs = np.where(crop > 8)
    if len(xs) == 0 or len(ys) == 0:
        notes.append("ilegivel")
    else:
        margin = 1
        if xs.min() <= margin or ys.min() <= margin or xs.max() >= 27 - margin or ys.max() >= 27 - margin:
            notes.append("possivelmente_cortado")
        cx = float(xs.mean())
        cy = float(ys.mean())
        if abs(cx - 13.5) > 5 or abs(cy - 13.5) > 5:
            notes.append("descentralizado")
    if len(crop_original_shape) >= 2 and min(crop_original_shape[:2]) <= 4:
        notes.append("crop_original_muito_pequeno")
    if duplicate_iou >= 0.5:
        notes.append("duplicado_sobreposto")
    elif duplicate_iou >= 0.1:
        notes.append("sobreposto")
    return ", ".join(notes) if notes else "visualmente_plausivel"


def build_segment(order: int, crop: np.ndarray, box: DetectedBox) -> KanjiSegment:
    return KanjiSegment(order=order, crop=crop, bounding_box=box.to_bounding_box())


def run(image_path: Path, output_dir: Path) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    original_dir = output_dir / "original_crops"
    final_dir = output_dir / "final_28x28"
    enlarged_dir = output_dir / "final_28x28_enlarged"

    image_bgr = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image_bgr is None or image_bgr.size == 0:
        raise RuntimeError(f"Imagem invalida ou nao carregada: {image_path}")

    save_image(output_dir / "original.png", image_bgr)

    segmenter = SegmentationService()
    pipeline_segments = segmenter.segment_and_normalize(image_bgr)

    image_height, image_width = image_bgr.shape[:2]
    raw_results = segmenter.model.predict(
        source=image_bgr,
        conf=segmenter.confidence_threshold,
        verbose=False,
    )
    boxes = []
    if raw_results:
        boxes = segmenter._extract_boxes(raw_results[0].boxes, image_width, image_height)
    ordered_boxes = segmenter._sort_boxes_japanese_vertical(boxes)

    image_with_boxes = image_bgr.copy()
    for index, box in enumerate(ordered_boxes, start=1):
        cv2.rectangle(image_with_boxes, (box.x1, box.y1), (box.x2, box.y2), (0, 0, 255), 2)
        cv2.putText(
            image_with_boxes,
            f"{index} {box.confidence:.2f}",
            (box.x1, max(15, box.y1 - 5)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 0, 255),
            1,
            cv2.LINE_AA,
        )
    save_image(output_dir / "original_with_yolo_boxes.png", image_with_boxes)

    valid_segments: list[KanjiSegment] = []
    rows = []
    iou_pairs = []
    for a_index, box_a in enumerate(ordered_boxes, start=1):
        max_iou = 0.0
        for b_index, box_b in enumerate(ordered_boxes, start=1):
            if a_index >= b_index:
                continue
            score = iou(box_a, box_b)
            if score > 0:
                iou_pairs.append({"a": a_index, "b": b_index, "iou": score})
            max_iou = max(max_iou, score)

        crop_bgr = segmenter._crop_original_with_margin(image_bgr, box_a, image_width, image_height)
        save_image(original_dir / f"{a_index:03d}_crop_original.png", crop_bgr)

        ink_gray, ink_mask = segmenter._extract_grayscale_ink(crop_bgr)
        ink_mask = segmenter._remove_small_components(ink_mask)
        ink_gray, ink_mask = segmenter._trim_gray_to_mask(ink_gray, ink_mask)
        normalized_crop = segmenter._normalize_to_28x28(ink_gray)
        if segmenter.output_mode == "binary":
            _, normalized_crop = cv2.threshold(
                normalized_crop, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )

        is_valid = segmenter._is_valid_crop(normalized_crop)
        save_image(final_dir / f"{a_index:03d}_final_28x28.png", normalized_crop)
        enlarged = cv2.resize(normalized_crop, (280, 280), interpolation=cv2.INTER_NEAREST)
        save_image(enlarged_dir / f"{a_index:03d}_final_28x28_x10.png", enlarged)

        row = {
            "order": a_index,
            "x": box_a.x1,
            "y": box_a.y1,
            "w": box_a.width,
            "h": box_a.height,
            "yolo_confidence": box_a.confidence,
            "crop_original_shape": list(crop_bgr.shape),
            "crop_final_shape": list(normalized_crop.shape),
            "dtype": str(normalized_crop.dtype),
            "min": int(normalized_crop.min()) if normalized_crop.size else None,
            "max": int(normalized_crop.max()) if normalized_crop.size else None,
            "mean": float(np.mean(normalized_crop)) if normalized_crop.size else None,
            "classifier_class": None,
            "classifier_confidence": None,
            "became_unknown": None,
            "valid_segment": is_valid,
            "max_iou_with_later_box": max_iou,
            "visual_observation": observe_crop(normalized_crop, crop_bgr.shape, max_iou),
        }
        rows.append(row)

        if is_valid:
            valid_segments.append(build_segment(len(valid_segments) + 1, normalized_crop, box_a))

    classifier_error = None
    classification_results = []
    if valid_segments:
        try:
            classifier = ClassificationService()
            classification_results = classifier.classify_batch(valid_segments)
        except Exception as exc:  # diagnostic must report runtime failure
            classifier_error = repr(exc)

    valid_row_indexes = [index for index, row in enumerate(rows) if row["valid_segment"]]
    for result, row_index in zip(classification_results, valid_row_indexes):
        rows[row_index]["classifier_class"] = result.modern_kanji
        rows[row_index]["classifier_confidence"] = result.confidence
        rows[row_index]["became_unknown"] = result.modern_kanji == "?"

    with (output_dir / "detections.csv").open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(rows[0].keys()) if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)

    summary = {
        "image_path": str(image_path),
        "output_dir": str(output_dir),
        "image_shape": list(image_bgr.shape),
        "confidence_threshold": segmenter.confidence_threshold,
        "raw_yolo_boxes": len(boxes),
        "ordered_yolo_boxes": len(ordered_boxes),
        "pipeline_segments": len(pipeline_segments),
        "reconstructed_valid_segments": len(valid_segments),
        "classification_results": len(classification_results),
        "classifier_error": classifier_error,
        "iou_pairs_over_0_10": [pair for pair in iou_pairs if pair["iou"] >= 0.10],
        "iou_pairs_over_0_50": [pair for pair in iou_pairs if pair["iou"] >= 0.50],
        "rows": rows,
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    return run(args.image, args.output)


if __name__ == "__main__":
    raise SystemExit(main())
