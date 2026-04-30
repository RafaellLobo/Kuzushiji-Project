from __future__ import annotations

import cv2
import numpy as np
import pytest

from app.services.errors import InvalidImageError
from app.services.image_decoder import ImageDecoder


def encode_test_image() -> bytes:
    image = np.zeros((32, 32, 3), dtype=np.uint8)
    success, encoded = cv2.imencode(".jpg", image)
    assert success
    return encoded.tobytes()


def test_decode_rejects_non_image_content_type() -> None:
    decoder = ImageDecoder()

    with pytest.raises(InvalidImageError) as exc_info:
        decoder.decode(b"not an image", "text/plain")

    assert exc_info.value.code == "INVALID_IMAGE"


def test_decode_rejects_corrupted_image() -> None:
    decoder = ImageDecoder()

    with pytest.raises(InvalidImageError) as exc_info:
        decoder.decode(b"corrupted", "image/jpeg")

    assert exc_info.value.code == "INVALID_IMAGE"


def test_decode_valid_image_returns_numpy_matrix() -> None:
    decoder = ImageDecoder()

    decoded = decoder.decode(encode_test_image(), "image/jpeg")

    assert isinstance(decoded, np.ndarray)
    assert decoded.shape == (32, 32, 3)
