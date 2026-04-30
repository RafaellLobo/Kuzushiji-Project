from __future__ import annotations

import cv2
import numpy as np

from app.services.contracts import ImageMatrix
from app.services.errors import InvalidImageError


class ImageDecoder:
    def __init__(self, max_bytes: int = 10 * 1024 * 1024) -> None:
        self.max_bytes = max_bytes

    def decode(self, image_bytes: bytes, content_type: str | None) -> ImageMatrix:
        if not content_type or not content_type.startswith("image/"):
            raise InvalidImageError()

        if not image_bytes:
            raise InvalidImageError("Imagem vazia.")

        if len(image_bytes) > self.max_bytes:
            raise InvalidImageError("Imagem excede o limite de 10MB.")

        encoded_image = np.frombuffer(image_bytes, dtype=np.uint8)
        decoded_image = cv2.imdecode(encoded_image, cv2.IMREAD_COLOR)

        if decoded_image is None:
            raise InvalidImageError("Nao foi possivel decodificar a imagem enviada.")

        return decoded_image
