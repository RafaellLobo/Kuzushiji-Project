# Instruções para agentes — Kuzushiji Translator

## Contexto do projeto

Sistema Full-Stack para traduzir documentos históricos japoneses em Kuzushiji para japonês moderno e inglês.

Stack:

- Front-end: React + Vite + Tailwind CSS.
- Back-end: Python 3.10+ com FastAPI.
- Visão Computacional: OpenCV, NumPy e YOLO/Ultralytics.
- Pipeline: segmentação YOLO -> classificação de caracteres -> tradução.

## Princípios obrigatórios

- Preserve a arquitetura existente.
- Não crie arquitetura nova sem necessidade.
- Não altere contratos públicos sem justificar.
- Não altere rotas, schemas ou fluxo principal sem necessidade real.
- Priorize mudanças pequenas, seguras e testáveis.
- O back-end deve manter Zero I/O de Disco no fluxo de inferência.
- Não use cv2.imread no pipeline da API.
- Não use cv2.imwrite no pipeline da API.
- Não salve uploads, crops ou imagens temporárias em disco.
- O processamento de imagem deve acontecer em RAM usando NumPy/OpenCV.

## Fluxo esperado do back-end

POST /translate
-> ImageDecoder
-> SegmentationService.segment_and_normalize(image_bgr)
-> ClassificationService.classify_batch(segments)
-> TranslationService

## Contrato crítico da segmentação

Preserve esta assinatura:

segment_and_normalize(image_bgr: ImageMatrix) -> list[KanjiSegment]

## Requisitos para YOLO

- O YOLO deve receber matriz OpenCV BGR já carregada em RAM.
- O modelo deve ser carregado uma única vez no **init** do SegmentationService.
- Nunca carregue o modelo a cada request.
- O peso local deve ficar em backend/app/models/best.pt.
- Não aceite caminho de modelo vindo do usuário/request.
- Detecte bounding boxes reais dos caracteres.
- Recorte cada caractere diretamente da matriz em RAM.
- Cada crop final deve ser:
  - shape: (28, 28)
  - dtype: np.uint8
  - fundo preto: 0
  - caractere branco: 255
- Não retorne imagens, arquivos, paths ou base64.
- Retorne list[KanjiSegment].
- Se não houver detecções válidas, retorne lista vazia.

## Ordenação japonesa

Os caracteres devem ser retornados em leitura japonesa vertical:

1. Colunas da direita para a esquerda.
2. Dentro de cada coluna, caracteres de cima para baixo.
3. Agrupe colunas usando o centro X das bounding boxes.
4. Ordene colunas por X decrescente.
5. Ordene caracteres dentro da coluna por Y crescente.

## Código legado

Ao adaptar scripts externos:

- remova main();
- remova prints;
- remova criação de pastas;
- remova cv2.imread;
- remova cv2.imwrite;
- não faça I/O de disco;
- transforme a lógica em serviço reutilizável dentro do pipeline FastAPI;
- use logging quando necessário.
