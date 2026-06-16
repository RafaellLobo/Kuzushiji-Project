from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

from app.services.contracts import BoundingBox, ImageMatrix, KanjiSegment

logger = logging.getLogger(__name__)
DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "best.pt"


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
        list[KanjiSegment], onde cada crop é uma matriz 28x28 uint8,
        fundo preto e caractere em tons de cinza, parecido com KMNIST.
    """

    def __init__(
        self,
        model_path: str | Path | None = None,
        confidence_threshold: float = 0.5,
        character_size: int = 28,
        margin_px: int = 2,
        column_tolerance_factor: float = 1.5,
        min_component_area: int = 4,
        adaptive_block_size: int = 31,
        adaptive_c: int = 10,
        output_mode: str = "grayscale",
    ) -> None:
        resolved_model_path = Path(model_path).resolve() if model_path else DEFAULT_MODEL_PATH
        if resolved_model_path != DEFAULT_MODEL_PATH:
            logger.warning(
                "model_path customizado foi ignorado; usando peso fixo em %s",
                DEFAULT_MODEL_PATH,
            )

        self.model_path = DEFAULT_MODEL_PATH
        self.confidence_threshold = confidence_threshold
        self.character_size = character_size
        self.margin_px = margin_px
        self.column_tolerance_factor = column_tolerance_factor
        self.min_component_area = min_component_area
        self.adaptive_block_size = self._ensure_odd_at_least_3(adaptive_block_size)
        self.adaptive_c = adaptive_c
        self.output_mode = output_mode

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
            verbose=False,
            conf=0.6,       # era provavelmente 0.25 — aumentar elimina predições fracas
            iou=0.25,        # era provavelmente 0.45 — reduzir torna o NMS mais agressivo
            agnostic_nms=True  # NMS entre todas as classes, não só por classe
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
        segments: list[KanjiSegment] = []

        for box in ordered_boxes:
            crop_bgr = self._crop_original_with_margin(
                image_bgr=image_bgr,
                box=box,
                image_width=image_width,
                image_height=image_height,
            )

            ink_gray, ink_mask = self._extract_grayscale_ink(crop_bgr)
            ink_mask = self._remove_small_components(ink_mask)
            ink_gray, ink_mask = self._trim_gray_to_mask(ink_gray, ink_mask)
            normalized_crop = self._normalize_to_28x28(ink_gray)

            if self.output_mode == "binary":
                _, normalized_crop = cv2.threshold(
                    normalized_crop, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
                )

            if not self._is_valid_crop(normalized_crop):
                continue

            segments.append(
                KanjiSegment(
                    order=len(segments) + 1,
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

            box = DetectedBox(x1=x1, y1=y1, x2=x2, y2=y2, confidence=confidence)

            if box.width < 2 or box.height < 2:
                continue

            detected_boxes.append(box)

        return detected_boxes

    def _sort_boxes_japanese_vertical(self, boxes: list[DetectedBox]) -> list[DetectedBox]:
        """
        Ordena no padrão japonês vertical:
        colunas da direita para a esquerda e, dentro de cada coluna, de cima para baixo.
        """
        if not boxes:
            return []

        widths = [box.width for box in boxes if box.width > 0]
        median_width = float(np.median(widths)) if widths else 28.0
        column_tolerance = median_width * self.column_tolerance_factor

        columns: list[list[DetectedBox]] = []
        for box in sorted(boxes, key=lambda b: b.x_center, reverse=True):
            for column in columns:
                column_center = float(np.mean([item.x_center for item in column]))
                if abs(box.x_center - column_center) <= column_tolerance:
                    column.append(box)
                    break
            else:
                columns.append([box])

        columns.sort(
            key=lambda col: float(np.mean([b.x_center for b in col])),
            reverse=True,
        )

        return [box for col in columns for box in sorted(col, key=lambda b: b.y_center)]

    def _crop_original_with_margin(
        self,
        image_bgr: ImageMatrix,
        box: DetectedBox,
        image_width: int,
        image_height: int,
    ) -> ImageMatrix:
        """Recorta da imagem original com margem."""
        x1 = max(0, box.x1 - self.margin_px)
        y1 = max(0, box.y1 - self.margin_px)
        x2 = min(image_width, box.x2 + self.margin_px)
        y2 = min(image_height, box.y2 + self.margin_px)
        return image_bgr[y1:y2, x1:x2]

    def _extract_grayscale_ink(self, crop_bgr: ImageMatrix) -> tuple[ImageMatrix, ImageMatrix]:
        """
        Extrai a tinta em tons de cinza e cria uma máscara binária auxiliar.

        Usa subtração de fundo local para realçar a tinta escura sobre papel,
        preservando tons intermediários (sem converter para binário aqui).
        """
        if crop_bgr is None or crop_bgr.size == 0:
            empty = np.zeros((self.character_size, self.character_size), dtype=np.uint8)
            return empty, empty

        gray = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)

        h, w = gray.shape[:2]
        k = max(7, int(round(min(h, w) * 0.35)) | 1)  # garante ímpar
        background = cv2.GaussianBlur(gray, (k, k), 0)

        # Realça tinta escura: pixels mais escuros que o fundo local ficam positivos.
        ink = cv2.subtract(background, gray)

        # Estica contraste até o percentil 99 para evitar saturação por ruído.
        nonzero = ink[ink > 0]
        if nonzero.size > 0:
            high = float(np.percentile(nonzero, 50))
            if high > 0:
                ink = np.clip((ink.astype(np.float32) / high) * 255.0, 0, 255).astype(np.uint8)

        # Máscara binária apenas para localizar a tinta (não é a saída final).
        block_size = self._ensure_odd_at_least_3(min(self.adaptive_block_size, h, w))
        if block_size < 3 or h < 3 or w < 3:
            _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        else:
            mask = cv2.adaptiveThreshold(
                gray,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV,
                block_size,
                self.adaptive_c,
            )

        ink = cv2.bitwise_and(ink, ink, mask=mask)
        return ink, mask

    def _remove_small_components(self, binary: ImageMatrix) -> ImageMatrix:
        """Remove ruídos pequenos preservando componentes maiores de tinta."""
        if binary is None or binary.size == 0:
            return binary

        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
        cleaned = np.zeros_like(binary)
        for label in range(1, num_labels):
            if int(stats[label, cv2.CC_STAT_AREA]) >= self.min_component_area:
                cleaned[labels == label] = 255
        return cleaned

    def _trim_gray_to_mask(
        self,
        gray_ink: ImageMatrix,
        mask: ImageMatrix,
    ) -> tuple[ImageMatrix, ImageMatrix]:
        """Recorta a imagem em tons de cinza usando a máscara de tinta."""
        if gray_ink is None or gray_ink.size == 0 or mask is None or mask.size == 0:
            return gray_ink, mask

        ys, xs = np.where(mask > 0)
        if len(xs) == 0 or len(ys) == 0:
            return gray_ink, mask

        x1, x2 = int(xs.min()), int(xs.max()) + 1
        y1, y2 = int(ys.min()), int(ys.max()) + 1
        return gray_ink[y1:y2, x1:x2], mask[y1:y2, x1:x2]

    def _normalize_to_28x28(self, crop: ImageMatrix) -> ImageMatrix:
        """
        Normaliza o crop para 28x28 mantendo proporção,
        centraliza por centro de massa e reforça contraste.
        """
        target = self.character_size

        if crop is None or crop.size == 0:
            return np.zeros((target, target), dtype=np.uint8)

        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY) if len(crop.shape) == 3 else crop
        gray = gray.astype(np.uint8)

        h, w = gray.shape[:2]
        if h == 0 or w == 0:
            return np.zeros((target, target), dtype=np.uint8)

        inner = target - 4
        scale = min(inner / h, inner / w)

        new_w = max(1, int(round(w * scale)))
        new_h = max(1, int(round(h * scale)))

        interp = cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC
        resized = cv2.resize(gray, (new_w, new_h), interpolation=interp)

        # Remove ruído muito fraco antes de aumentar contraste
        resized[resized < 6] = 0

        # Expande contraste por percentil
        nz = resized[resized > 0]
        if nz.size > 0:
            high = np.percentile(nz, 95)
            if high > 0:
                resized = np.clip(
                    resized.astype(np.float32) * (255.0 / high),
                    0,
                    255,
                ).astype(np.uint8)

        # Clareia tons médios
        gamma = 0.45
        resized = np.clip(
            ((resized.astype(np.float32) / 255.0) ** gamma) * 255.0,
            0,
            255,
        ).astype(np.uint8)

        # Centraliza pelo centro de massa
        canvas = np.zeros((target, target), dtype=np.uint8)

        m = cv2.moments(resized)
        cx = int(m["m10"] / m["m00"]) if m["m00"] != 0 else new_w // 2
        cy = int(m["m01"] / m["m00"]) if m["m00"] != 0 else new_h // 2

        ox = (target // 2) - cx
        oy = (target // 2) - cy

        x1 = max(0, ox)
        y1 = max(0, oy)
        x2 = min(target, ox + new_w)
        y2 = min(target, oy + new_h)

        sx = max(0, -ox)
        sy = max(0, -oy)

        canvas[y1:y2, x1:x2] = resized[
                               sy:sy + (y2 - y1),
                               sx:sx + (x2 - x1),
                               ]

        # Engrossa levemente o traço no final
        kernel = np.ones((2, 2), np.uint8)
        canvas = cv2.dilate(canvas, kernel, iterations=1)

        # Remove ruído residual criado pela interpolação/dilatação
        canvas[canvas < 8] = 0

        return canvas

    def _is_valid_crop(self, crop: ImageMatrix) -> bool:
        """Valida o formato final esperado pelo classificador."""
        return (
            isinstance(crop, np.ndarray)
            and crop.shape == (self.character_size, self.character_size)
            and crop.dtype == np.uint8
            and bool(np.any(crop > 0))
        )

    @staticmethod
    def _ensure_odd_at_least_3(value: int) -> int:
        """Garante valor ímpar >= 3 para adaptiveThreshold."""
        value = max(3, int(value))
        return value if value % 2 != 0 else value - 1