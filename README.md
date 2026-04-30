# Kanji Translator (Kuzushiji)

Sistema full-stack para traduzir documentos historicos japoneses (Kuzushiji) para japones moderno e ingles usando visao computacional e NLP.

## Fluxo Geral

```text
Usuario envia foto -> FastAPI decodifica em RAM -> Segmentacao -> Classificacao em batch -> Traducao
```

Para entender o contrato completo, veja [`docs/fluxo.md`](docs/fluxo.md).

## Estrutura do Repositorio

```text
kanji-translator/
├── frontend/                  # Interface React (Vite)
│   └── src/
│       ├── components/        # Componentes visuais isolados
│       ├── hooks/             # Logica de negocio e integracao com API/camera
│       └── assets/            # Imagens e estilos estaticos
├── backend/                   # API FastAPI
│   └── app/
│       ├── routes/            # Endpoints HTTP
│       ├── services/          # Pipeline em RAM, adapters de IA e tradutor
│       └── models/            # Pesos locais ignorados pelo Git
└── docs/                      # Documentacao do projeto
```

## Como Rodar Localmente

### Pre-requisitos

- Node.js 18+
- Python 3.10+

### Front-end

```bash
cd frontend/APLICAÇÃO_WEB/aplication_web
npm install
npm run dev
```

### Back-end

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

A API fica em `http://localhost:8000`.
A documentacao automatica fica em `http://localhost:8000/docs`.

## Integracoes Pendentes

| Componente | Status |
| --- | --- |
| Modelo YOLO / segmentacao | Adapter mock ativo |
| Classificador | Adapter mock ativo |
| Traducao | Async HTTP client estruturado |

## Variaveis de Ambiente

Copie os arquivos `.env.example` e renomeie para `.env` em cada pasta:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```
