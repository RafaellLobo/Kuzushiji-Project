from __future__ import annotations

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

import argparse

import cv2
import numpy as np

from app.services.yolo_agent import SegmentationService

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "debug_segments"


def _parse_args() -> Path:
    parser = argparse.ArgumentParser(
        description="Executa a segmentacao YOLO e salva artefatos de debug fora do pipeline da API."
    )
    parser.add_argument("image_path", type=Path, help="Caminho da imagem de entrada")
    return parser.parse_args().image_path


def _validate_crop(crop: np.ndarray) -> tuple[int, int, int, np.ndarray]:
    unique_values = np.unique(crop)
    white_pixels = int(np.count_nonzero(crop == 255))
    black_pixels = int(np.count_nonzero(crop == 0))
    non_binary_pixels = int(np.count_nonzero((crop != 0) & (crop != 255)))

    assert crop.shape == (28, 28), "Crop nao esta em 28x28"
    assert crop.dtype == np.uint8, "Crop nao esta como np.uint8"

    return white_pixels, black_pixels, non_binary_pixels, unique_values


def _save_debug_images(crop: np.ndarray, order: int) -> None:
    crop_path = OUTPUT_DIR / f"{order:03d}_28x28.png"
    preview_path = OUTPUT_DIR / f"{order:03d}_preview_280x280.png"

    cv2.imwrite(str(crop_path), crop)

    preview = cv2.resize(
        crop,
        (280, 280),
        interpolation=cv2.INTER_NEAREST,
    )
    cv2.imwrite(str(preview_path), preview)


def main() -> None:
    image_path = _parse_args()

    if not image_path.exists():
        raise SystemExit(f"Imagem nao encontrada: {image_path}")

    image_bgr = cv2.imread(str(image_path))

    if image_bgr is None:
        raise SystemExit(f"Nao foi possivel ler a imagem: {image_path}")

    segmenter = SegmentationService()
    segments = segmenter.segment_and_normalize(image_bgr)

    print("=" * 70)
    print("DEBUG YOLO SEGMENTS")
    print("=" * 70)
    print(f"Imagem: {image_path}")
    print(f"Segmentos detectados: {len(segments)}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not segments:
        print("Nenhum segmento detectado.")
        return

    for segment in segments:
        crop = segment.crop
        bbox = segment.bounding_box
        white_pixels, black_pixels, non_binary_pixels, unique_values = _validate_crop(crop)

        print("-" * 70)
        print(f"Ordem: {segment.order}")
        print(f"BBox: x={bbox.x}, y={bbox.y}, w={bbox.w}, h={bbox.h}")
        print(f"Shape: {crop.shape}")
        print(f"Dtype: {crop.dtype}")
        print(f"Min/Max: {crop.min()} / {crop.max()}")
        print(f"Valores unicos: {unique_values[:20]}")
        print(f"Pixels pretos: {black_pixels}")
        print(f"Pixels brancos: {white_pixels}")
        print(f"Pixels nao-binarios: {non_binary_pixels}")

        if non_binary_pixels > 0:
            print("AVISO: crop possui valores diferentes de 0 e 255.")

        if white_pixels == 0:
            print("AVISO: crop esta totalmente preto. Pode haver erro de bbox/threshold.")

        _save_debug_images(crop, segment.order)

    print("=" * 70)
    print(f"Arquivos de debug salvos em: {OUTPUT_DIR.resolve()}")
    print("=" * 70)


if __name__ == "__main__":
    main()
