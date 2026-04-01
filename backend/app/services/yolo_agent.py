# =============================================================================
# PLACEHOLDER — Agente YOLO
# =============================================================================
# Este arquivo define a interface que o modelo YOLO deve implementar.
# Quando o modelo estiver pronto, substitua o corpo da função abaixo
# mantendo exatamente a mesma assinatura.
#
# Responsável pela implementação: [nome do colega]
# Referência de interface: docs/fluxo.md — Contrato 3
# =============================================================================

def segment_and_normalize(image_bytes: bytes) -> list[bytes]:
    """
    Recebe a imagem original em bytes.

    Retorna lista de imagens 28x28px (bytes), cada uma contendo
    um kanji recortado e normalizado:
      - Fundo preto
      - Caractere branco centralizado
      - Ordenadas: coluna direita para esquerda, de cima para baixo

    TODO: substituir pelo modelo YOLO treinado.
    """
    raise NotImplementedError(
        "Agente YOLO ainda não integrado. Ver docs/fluxo.md para a interface esperada."
    )

def segment_and_normalize(image_bytes: bytes) -> list:
    # Simula que o YOLO encontrou 3 kanjis na foto e os recortou
    # Retornamos 3 "bytes" falsos para enganar o próximo passo
    return [b"kanji_1", b"kanji_2", b"kanji_3"]