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
