from __future__ import annotations

import csv
import logging
import os
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from app.services.contracts import ClassificationResult, KanjiSegment

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")

MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "classifier.h5"
CLASSMAP_PATH = Path(__file__).resolve().parents[1] / "models" / "k49_classmap.csv"
EXPECTED_CLASS_COUNT = 49
UNKNOWN_CHARACTER = "?"

_default_service: "ClassificationService | None" = None


class ClassificationService:
    """Real classifier service backed by TensorFlow/Keras."""

    def __init__(
        self,
        confidence_threshold: float = 0.5,
        model_path: Path | None = None,
        classmap_path: Path | None = None,
    ) -> None:
        self.confidence_threshold = confidence_threshold
        self.model_path = Path(model_path).resolve() if model_path else MODEL_PATH
        self.classmap_path = Path(classmap_path).resolve() if classmap_path else CLASSMAP_PATH

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Modelo do classificador nao encontrado em: {self.model_path}"
            )

        if not self.classmap_path.exists():
            raise FileNotFoundError(
                f"Classmap do classificador nao encontrado em: {self.classmap_path}"
            )

        try:
            import tensorflow as tf
            from tensorflow.keras.models import load_model

        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "TensorFlow nao esta instalado. Adicione a dependencia do TensorFlow "
                "ao ambiente do backend para carregar classifier.h5."
            ) from exc

        tf.get_logger().setLevel("ERROR")
        logging.getLogger("absl").setLevel(logging.ERROR)

        self.model = load_model(self.model_path, compile=False)
        self.class_labels = self._load_class_labels(self.classmap_path)

    def debug_predict_crop(self, crop: np.ndarray, top_k: int = 5) -> list[tuple[str, float]]:
        if crop.shape != (28, 28):
            raise ValueError(f"Esperado crop 28x28, recebido {crop.shape}")

        batch = crop.astype(np.float32) / 255.0
        batch = np.expand_dims(batch, axis=0)
        batch = np.expand_dims(batch, axis=-1)

        probs = self.model.predict(batch, verbose=0)[0]

        top_indexes = np.argsort(probs)[::-1][:top_k]

        results = []
        for idx in top_indexes:
            results.append((self.class_labels[int(idx)], float(probs[int(idx)])))

        return results

    def classify_batch(self, segments: list[KanjiSegment]) -> list[ClassificationResult]:
        if not segments:
            return []

        batch = self._prepare_batch(segments)
        predictions = self.model.predict(batch, verbose=0)
        predictions = np.asarray(predictions, dtype=np.float32)

        if predictions.ndim != 2 or predictions.shape != (len(segments), EXPECTED_CLASS_COUNT):
            raise ValueError(
                "Saida invalida do classificador: esperado shape "
                f"({len(segments)}, {EXPECTED_CLASS_COUNT}), recebido {predictions.shape}."
            )

        results: list[ClassificationResult] = []

        for segment, probabilities in zip(segments, predictions):
            predicted_index = int(np.argmax(probabilities))
            confidence = float(np.max(probabilities))
            predicted_char = self.class_labels[predicted_index]

            if confidence < self.confidence_threshold:
                predicted_char = UNKNOWN_CHARACTER

            results.append(
                ClassificationResult(
                    old_kanji=predicted_char,
                    modern_kanji=predicted_char,
                    confidence=confidence,
                    bounding_box=segment.bounding_box,
                )
            )

        return results

    def _prepare_batch(self, segments: list[KanjiSegment]) -> np.ndarray:
        crops = np.stack([segment.crop for segment in segments], axis=0)
        if crops.shape != (len(segments), 28, 28):
            raise ValueError(
                "Entrada invalida do classificador: esperado batch de crops com shape "
                f"({len(segments)}, 28, 28), recebido {crops.shape}."
            )

        batch = crops.astype(np.float32) / 255.0
        batch = np.expand_dims(batch, axis=-1)

        if batch.shape != (len(segments), 28, 28, 1):
            raise ValueError(
                "Entrada invalida do classificador: esperado batch final com shape "
                f"({len(segments)}, 28, 28, 1), recebido {batch.shape}."
            )
        #
        plt.imshow(crops[0], cmap='gray')
        plt.title(f"Isso parece um KMINST real? {crops[0].shape}")
        plt.show()

        return batch

    def _load_class_labels(self, classmap_path: Path) -> list[str]:
        with classmap_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            fieldnames = set(reader.fieldnames or [])
            required_columns = {"index", "codepoint", "char"}

            if not required_columns.issubset(fieldnames):
                raise ValueError(
                    "Classmap invalido: colunas obrigatorias ausentes. "
                    f"Esperado {sorted(required_columns)}, recebido {sorted(fieldnames)}."
                )

            indexed_chars: dict[int, str] = {}

            for row in reader:
                class_index = int(row["index"])
                class_char = row["char"]

                if not class_char:
                    raise ValueError(
                        f"Classmap invalido: char vazio para index {class_index}."
                    )

                indexed_chars[class_index] = class_char

        if len(indexed_chars) != EXPECTED_CLASS_COUNT:
            raise ValueError(
                f"Classmap invalido: esperado {EXPECTED_CLASS_COUNT} classes, "
                f"recebido {len(indexed_chars)}."
            )

        expected_indexes = set(range(EXPECTED_CLASS_COUNT))
        if set(indexed_chars) != expected_indexes:
            raise ValueError(
                "Classmap invalido: indexes devem cobrir exatamente o intervalo 0-48."
            )

        return [indexed_chars[index] for index in range(EXPECTED_CLASS_COUNT)]


def classify_batch(segments: list[KanjiSegment]) -> list[ClassificationResult]:
    return _get_default_service().classify_batch(segments)


def _get_default_service() -> ClassificationService:
    global _default_service

    if _default_service is None:
        _default_service = ClassificationService()

    return _default_service

