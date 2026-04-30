# Fluxo do Sistema: Contrato Entre Componentes

Este documento define as interfaces entre o front-end, a API e os adapters de IA.

## Visao Geral

```text
[React] -> POST /translate (multipart/form-data) -> [FastAPI]
                                                     |
                                                     v
                                           ImageDecoder
                                      bytes -> np.ndarray BGR
                                                     |
                                                     v
                                  SegmentationService.segment_and_normalize()
                                                     |
                                                     v
                                  ClassificationService.classify_batch()
                                                     |
                                                     v
                                  TranslationService.translate_to_english()
                                                     |
                                                     v
                                      JSON de resposta para o front-end
```

## Contrato 1: Front-end -> Back-end

- Rota: `POST /translate`
- Content-Type: `multipart/form-data`
- Campo: `image`
- Formatos esperados: `jpg`, `jpeg`, `png`

## Contrato 2: Back-end -> Front-end

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
    "code": "NO_KANJI_FOUND",
    "message": "Nenhum kanji foi detectado na imagem."
  }
}
```

Codigos principais:

| Codigo | Situacao |
| --- | --- |
| `INVALID_IMAGE` | Arquivo vazio, corrompido, muito grande ou com MIME invalido |
| `CLASSIFIER_NOT_INTEGRATED` | Classificador retornou resposta invalida |
| `NO_KANJI_FOUND` | Nenhum segmento foi detectado |
| `TRANSLATION_FAILED` | Falha na traducao externa |

## Contrato 3: Segmentacao

- Arquivo: `backend/app/services/yolo_agent.py`
- Funcao: `segment_and_normalize(image_bgr: np.ndarray) -> list[KanjiSegment]`
- Entrada: matriz OpenCV BGR decodificada em RAM.
- Saida: lista ordenada de segmentos com crop 28x28 e bounding box.

O adapter atual e mock deterministico. ONNX, PyTorch ou Ultralytics devem entrar atras da mesma interface.

## Contrato 4: Classificacao

- Arquivo: `backend/app/services/classifier.py`
- Funcao: `classify_batch(segments: list[KanjiSegment]) -> list[ClassificationResult]`
- Entrada: batch de segmentos normalizados.
- Saida: resultados na mesma ordem dos segmentos.

O uso de batch evita overhead de chamada por kanji e prepara o caminho para inferencia vetorizada.
