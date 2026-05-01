from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

from app.services.yolo_agent import SegmentationService


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(
            "Uso: python scripts/debug_yolo_segments.py caminho/para/imagem.jpg"
        )

    image_path = Path(sys.argv[1])

    if not image_path.exists():
        raise SystemExit(f"Imagem não encontrada: {image_path}")

    image_bgr = cv2.imread(str(image_path))

    if image_bgr is None:
        raise SystemExit(f"Não foi possível ler a imagem: {image_path}")

    segmenter = SegmentationService()
    segments = segmenter.segment_and_normalize(image_bgr)

    print("=" * 70)
    print("DEBUG YOLO SEGMENTS")
    print("=" * 70)
    print(f"Imagem: {image_path}")
    print(f"Segmentos detectados: {len(segments)}")

    output_dir = Path("debug_segments")
    output_dir.mkdir(exist_ok=True)

    if not segments:
        print("Nenhum segmento detectado.")
        return

    for segment in segments:
        crop = segment.crop
        bbox = segment.bounding_box

        unique_values = np.unique(crop)
        white_pixels = int(np.count_nonzero(crop == 255))
        black_pixels = int(np.count_nonzero(crop == 0))
        non_binary_pixels = int(np.count_nonzero((crop != 0) & (crop != 255)))

        print("-" * 70)
        print(f"Ordem: {segment.order}")
        print(f"BBox: x={bbox.x}, y={bbox.y}, w={bbox.w}, h={bbox.h}")
        print(f"Shape: {crop.shape}")
        print(f"Dtype: {crop.dtype}")
        print(f"Min/Max: {crop.min()} / {crop.max()}")
        print(f"Valores únicos: {unique_values[:20]}")
        print(f"Pixels pretos: {black_pixels}")
        print(f"Pixels brancos: {white_pixels}")
        print(f"Pixels não-binários: {non_binary_pixels}")

        assert crop.shape == (28, 28), "Crop não está em 28x28"
        assert crop.dtype == np.uint8, "Crop não está como np.uint8"

        if non_binary_pixels > 0:
            print("AVISO: crop possui valores diferentes de 0 e 255.")

        if white_pixels == 0:
            print("AVISO: crop está totalmente preto. Pode haver erro de bbox/threshold.")

        crop_path = output_dir / f"{segment.order:03d}_28x28.png"
        preview_path = output_dir / f"{segment.order:03d}_preview_280x280.png"

        cv2.imwrite(str(crop_path), crop)

        preview = cv2.resize(
            crop,
            (280, 280),
            interpolation=cv2.INTER_NEAREST,
        )
        cv2.imwrite(str(preview_path), preview)

    print("=" * 70)
    print(f"Arquivos de debug salvos em: {output_dir.resolve()}")
    print("=" * 70)


if __name__ == "__main__":
    main()