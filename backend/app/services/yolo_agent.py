from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

from app.services.contracts import BoundingBox, ImageMatrix, KanjiSegment

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class DetectedBox:
    """Representa uma detecção bruta do YOLO em coordenadas da imagem original."""

    x1: int
    y1: int
    x2: int
    y2: int
    confidence: float

    @property
    def width(self) -> int:
        return max(0, self.x2 - self.x1)

    @property
    def height(self) -> int:
        return max(0, self.y2 - self.y1)

    @property
    def x_center(self) -> float:
        return (self.x1 + self.x2) / 2

    @property
    def y_center(self) -> float:
        return (self.y1 + self.y2) / 2

    def to_bounding_box(self) -> BoundingBox:
        return BoundingBox(
            x=self.x1,
            y=self.y1,
            w=self.width,
            h=self.height,
        )


class SegmentationService:
    """
    Adapter de segmentação YOLO para o pipeline FastAPI.

    Entrada:
        image_bgr: matriz OpenCV BGR em RAM.

    Saída:
        list[KanjiSegment], onde cada crop é uma matriz 28x28,
        fundo preto e caractere branco.
    """

    def __init__(
        self,
        model_path: str | Path | None = None,
        confidence_threshold: float = 0.5,
        character_size: int = 28,
        margin_px: int = 5,
        column_tolerance_factor: float = 1.5,
    ) -> None:
        self.model_path = Path(model_path or "app/models/best.pt")
        self.confidence_threshold = confidence_threshold
        self.character_size = character_size
        self.margin_px = margin_px
        self.column_tolerance_factor = column_tolerance_factor

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Modelo YOLO não encontrado em: {self.model_path}. "
                "Coloque o arquivo best.pt em backend/app/models/best.pt."
            )

        self.model = YOLO(str(self.model_path))
        logger.info("Modelo YOLO carregado: %s", self.model_path)

    def segment_and_normalize(self, image_bgr: ImageMatrix) -> list[KanjiSegment]:
        """
        Detecta caracteres na imagem completa, ordena na leitura japonesa vertical
        e retorna crops normalizados para 28x28.
        """
        if image_bgr is None or image_bgr.size == 0:
            return []

        image_height, image_width = image_bgr.shape[:2]

        results = self.model.predict(
            source=image_bgr,
            conf=self.confidence_threshold,
            verbose=False,
        )

        if not results:
            return []

        boxes = self._extract_boxes(
            yolo_boxes=results[0].boxes,
            image_width=image_width,
            image_height=image_height,
        )

        if not boxes:
            return []

        ordered_boxes = self._sort_boxes_japanese_vertical(boxes)

        binary_image = self._binarize_full_image(image_bgr)

        segments: list[KanjiSegment] = []

        for order, box in enumerate(ordered_boxes, start=1):
            crop = self._crop_with_margin(
                binary_image=binary_image,
                box=box,
                image_width=image_width,
                image_height=image_height,
            )

            normalized_crop = self._normalize_to_28x28(crop)

            if not self._is_valid_crop(normalized_crop):
                continue

            segments.append(
                KanjiSegment(
                    order=order,
                    crop=normalized_crop,
                    bounding_box=box.to_bounding_box(),
                )
            )

        return segments

    def _extract_boxes(
        self,
        yolo_boxes,
        image_width: int,
        image_height: int,
    ) -> list[DetectedBox]:
        """Extrai e valida bounding boxes vindas do YOLO."""
        detected_boxes: list[DetectedBox] = []

        if yolo_boxes is None or len(yolo_boxes) == 0:
            return detected_boxes

        for raw_box in yolo_boxes:
            x1, y1, x2, y2 = raw_box.xyxy[0].cpu().numpy()
            confidence = float(raw_box.conf[0].cpu().numpy())

            if confidence < self.confidence_threshold:
                continue

            x1 = int(np.clip(round(x1), 0, image_width - 1))
            y1 = int(np.clip(round(y1), 0, image_height - 1))
            x2 = int(np.clip(round(x2), 0, image_width))
            y2 = int(np.clip(round(y2), 0, image_height))

            box = DetectedBox(
                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2,
                confidence=confidence,
            )

            if box.width < 2 or box.height < 2:
                continue

            detected_boxes.append(box)

        return detected_boxes

    def _sort_boxes_japanese_vertical(self, boxes: list[DetectedBox]) -> list[DetectedBox]:
        """
        Ordena os caracteres no padrão japonês vertical:

        1. Colunas da direita para a esquerda.
        2. Dentro de cada coluna, caracteres de cima para baixo.
        """
        if not boxes:
            return []

        widths = [box.width for box in boxes if box.width > 0]
        median_width = float(np.median(widths)) if widths else 28.0
        column_tolerance = median_width * self.column_tolerance_factor

        columns: list[list[DetectedBox]] = []

        # Primeiro percorre da direita para a esquerda.
        boxes_by_x = sorted(boxes, key=lambda box: box.x_center, reverse=True)

        for box in boxes_by_x:
            matched_column: list[DetectedBox] | None = None

            for column in columns:
                column_center = float(np.mean([item.x_center for item in column]))

                if abs(box.x_center - column_center) <= column_tolerance:
                    matched_column = column
                    break

            if matched_column is None:
                columns.append([box])
            else:
                matched_column.append(box)

        # Ordena colunas pela média de X, da direita para a esquerda.
        columns.sort(
            key=lambda column: float(np.mean([box.x_center for box in column])),
            reverse=True,
        )

        ordered_boxes: list[DetectedBox] = []

        for column in columns:
            # Dentro da coluna, leitura de cima para baixo.
            ordered_boxes.extend(sorted(column, key=lambda box: box.y_center))

        return ordered_boxes

    def _binarize_full_image(self, image_bgr: ImageMatrix) -> ImageMatrix:
        """
        Converte imagem BGR para binária:

        fundo preto = 0
        caractere/tinta = 255
        """
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

        _, binary = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
        )

        return binary

    def _crop_with_margin(
        self,
        binary_image: ImageMatrix,
        box: DetectedBox,
        image_width: int,
        image_height: int,
    ) -> ImageMatrix:
        """Recorta o caractere da imagem binária usando margem segura."""
        x1 = max(0, box.x1 - self.margin_px)
        y1 = max(0, box.y1 - self.margin_px)
        x2 = min(image_width, box.x2 + self.margin_px)
        y2 = min(image_height, box.y2 + self.margin_px)

        return binary_image[y1:y2, x1:x2]

    def _normalize_to_28x28(self, crop: ImageMatrix) -> ImageMatrix:
        """
        Normaliza o crop para 28x28 mantendo proporção e usando padding preto.
        """
        target_size = self.character_size

        if crop is None or crop.size == 0:
            return np.zeros((target_size, target_size), dtype=np.uint8)

        height, width = crop.shape[:2]

        if height == 0 or width == 0:
            return np.zeros((target_size, target_size), dtype=np.uint8)

        scale = min(target_size / height, target_size / width)

        new_width = max(1, int(round(width * scale)))
        new_height = max(1, int(round(height * scale)))

        resized = cv2.resize(
            crop,
            (new_width, new_height),
            interpolation=cv2.INTER_AREA,
        )

        # Garante novamente 0/255 após resize.
        _, resized = cv2.threshold(resized, 127, 255, cv2.THRESH_BINARY)

        canvas = np.zeros((target_size, target_size), dtype=np.uint8)

        offset_x = (target_size - new_width) // 2
        offset_y = (target_size - new_height) // 2

        canvas[
            offset_y : offset_y + new_height,
            offset_x : offset_x + new_width,
        ] = resized

        return canvas

    def _is_valid_crop(self, crop: ImageMatrix) -> bool:
        """Valida o formato final esperado pelo classificador."""
        return (
            isinstance(crop, np.ndarray)
            and crop.shape == (self.character_size, self.character_size)
            and crop.dtype == np.uint8
        )