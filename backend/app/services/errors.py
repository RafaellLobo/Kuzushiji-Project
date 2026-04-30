from __future__ import annotations


class PipelineError(Exception):
    status_code = 200

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message

    def to_response(self) -> dict[str, object]:
        return {
            "success": False,
            "data": None,
            "error": {"code": self.code, "message": self.message},
        }


class InvalidImageError(PipelineError):
    status_code = 400

    def __init__(self, message: str = "O arquivo enviado nao e uma imagem valida.") -> None:
        super().__init__("INVALID_IMAGE", message)


class NoKanjiFoundError(PipelineError):
    def __init__(self) -> None:
        super().__init__("NO_KANJI_FOUND", "Nenhum kanji foi detectado na imagem.")


class ClassifierNotIntegratedError(PipelineError):
    def __init__(self, message: str = "Classificador ainda nao integrado.") -> None:
        super().__init__("CLASSIFIER_NOT_INTEGRATED", message)


class TranslationFailedError(PipelineError):
    def __init__(self, message: str = "Falha ao traduzir o texto.") -> None:
        super().__init__("TRANSLATION_FAILED", message)
