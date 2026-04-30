# Contexto do Projeto: Kuzushiji Translator

## 1. Visao Geral e Arquitetura Base

Sistema full-stack para traduzir kanjis historicos japoneses (Kuzushiji) para japones moderno e ingles.

- Front-end: React.js (Vite), Tailwind CSS, componentes isolados e custom hooks.
- Back-end: Python, FastAPI, rotas finas e services especializados.
- Processamento: imagem decodificada em RAM com `numpy.frombuffer` e `cv2.imdecode`, sem I/O de disco.

## 2. Responsabilidades

### Front-end (`/frontend`)

- `/src/components/`: componentes visuais como `CameraView`, `DropzoneView` e `ResultsView`.
- `/src/hooks/`: integracao com camera e API, como `useTranslation` e `useCamera`.

### Back-end (`/backend`)

- `/app/main.py`: cria o FastAPI, configura CORS e inicializa o pipeline no lifespan.
- `/app/routes/translate.py`: rota `POST /translate`; recebe bytes e delega ao pipeline.
- `/app/services/image_decoder.py`: valida MIME, tamanho, bytes vazios e decode OpenCV.
- `/app/services/translation_pipeline.py`: orquestra decode, segmentacao, classificacao em batch e traducao.
- `/app/services/yolo_agent.py`: adapter de segmentacao; recebe `np.ndarray` BGR e retorna segmentos.
- `/app/services/classifier.py`: adapter de classificacao em batch.
- `/app/services/translator.py`: traducao async com `httpx.AsyncClient` compartilhado.
- `/app/services/contracts.py`: contratos tipados do pipeline.

## 3. Status Atual

- Comunicacao front/back mantida via `POST /translate`.
- Processamento continua 100% em RAM, sem pasta `/temp`.
- Adapters mock estao isolados em `yolo_agent.py` e `classifier.py` ate a integracao real dos modelos `.pt` ou `.onnx`.
- Modelos grandes devem ficar em `backend/app/models` e permanecer fora do Git.

## 4. Proximos Passos

1. Substituir o mock de `SegmentationService` por um adapter real ONNX, PyTorch ou Ultralytics.
2. Substituir o mock de `ClassificationService` por inferencia em batch.
3. Adicionar benchmark de latencia com imagens reais pequenas e medias.
