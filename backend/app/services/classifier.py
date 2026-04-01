# =============================================================================
# PLACEHOLDER — Agente classificador de kanjis
# =============================================================================
# Este arquivo define a interface que o classificador deve implementar.
# Quando o agente estiver pronto, substitua o corpo da função abaixo
# mantendo exatamente a mesma assinatura.
#
# Responsável pela integração: [nome do colega]
# Referência de interface: docs/fluxo.md — Contrato 4
# =============================================================================

def classify_kanji(image_28x28: bytes) -> dict:
    """
    Recebe uma imagem 28x28px normalizada (bytes).

    Retorna dicionário com:
      {
        "old_kanji":    str,    ex: "龍"
        "modern_kanji": str,    ex: "竜"
        "confidence":   float,  ex: 0.97  (entre 0.0 e 1.0)
        "bounding_box": dict    ex: {"x": 120, "y": 45, "w": 28, "h": 28}  (opcional)
      }

    TODO: integrar agente classificador já treinado.
    """
    raise NotImplementedError(
        "Classificador ainda não integrado. Ver docs/fluxo.md para a interface esperada."
    )

def classify_kanji(image_28x28: bytes) -> dict:
    # Simula a Inteligência Artificial classificando cada recorte do YOLO
    if image_28x28 == b"kanji_1":
        return {"old_kanji": "春", "modern_kanji": "春", "confidence": 0.99, "bounding_box": [0, 0, 28, 28]}
    elif image_28x28 == b"kanji_2":
        return {"old_kanji": "夜", "modern_kanji": "夜", "confidence": 0.95, "bounding_box": [30, 0, 28, 28]}
    else:
        return {"old_kanji": "夢", "modern_kanji": "夢", "confidence": 0.98, "bounding_box": [60, 0, 28, 28]}