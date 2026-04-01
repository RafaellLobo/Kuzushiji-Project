# Fluxo do sistema — contrato entre componentes

Este documento define a interface entre cada parte do sistema.
**Todos os integrantes devem seguir esses contratos ao implementar seus módulos.**

---

## Visão geral

```
[React] → POST /translate (multipart/form-data) → [FastAPI]
                                                        ↓
                                              yolo_agent.segment_and_normalize()
                                                        ↓
                                              classifier.classify_kanji()  (por kanji)
                                                        ↓
                                              translator.translate_to_english()
                                                        ↓
                                         ← JSON de resposta ← [FastAPI]
```

---

## Contrato 1 — Front-end → Back-end

**Rota:** `POST /translate`
**Content-Type:** `multipart/form-data`
**Campo:** `image` (arquivo de imagem: jpg, png)

---

## Contrato 2 — Back-end → Front-end (resposta JSON)

### Sucesso
```json
{
  "success": true,
  "data": {
    "characters": [
      {
        "order": 1,
        "old_kanji": "龍",
        "modern_kanji": "竜",
        "confidence": 0.97,
        "bounding_box": { "x": 120, "y": 45, "w": 28, "h": 28 }
      }
    ],
    "japanese_text": "竜",
    "english_translation": "Dragon",
    "processing_time_ms": 1243
  },
  "error": null
}
```

### Erro
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "YOLO_NOT_INTEGRATED",
    "message": "O agente de segmentação ainda não foi integrado."
  }
}
```

### Códigos de erro possíveis
| Código | Situação |
|---|---|
| `YOLO_NOT_INTEGRATED` | Placeholder do YOLO ainda ativo |
| `CLASSIFIER_NOT_INTEGRATED` | Placeholder do classificador ainda ativo |
| `NO_KANJI_FOUND` | Nenhum kanji detectado na imagem |
| `TRANSLATION_FAILED` | Falha na API de tradução |
| `INVALID_IMAGE` | Arquivo enviado não é uma imagem válida |

---

## Contrato 3 — Interface do agente YOLO

**Arquivo:** `backend/app/services/yolo_agent.py`
**Função:** `segment_and_normalize(image_bytes: bytes) -> list[bytes]`

- **Entrada:** imagem original em bytes
- **Saída:** lista de imagens 28x28px em bytes, cada uma com:
  - Fundo preto
  - Caractere branco centralizado
  - Ordenadas: coluna da direita para esquerda, de cima para baixo

---

## Contrato 4 — Interface do agente classificador

**Arquivo:** `backend/app/services/classifier.py`
**Função:** `classify_kanji(image_28x28: bytes) -> dict`

- **Entrada:** imagem 28x28px normalizada (bytes)
- **Saída:**
```json
{
  "old_kanji": "龍",
  "modern_kanji": "竜",
  "confidence": 0.97,
  "bounding_box": { "x": 120, "y": 45, "w": 28, "h": 28 }
}
```
