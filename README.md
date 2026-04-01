# Kanji Translator

Sistema de tradução de kanjis antigos para inglês, utilizando visão computacional e processamento de linguagem natural.

## Fluxo geral

```
Usuário envia foto → YOLO segmenta os kanjis → Classificador identifica cada caractere → Tradução para inglês
```

Para entender o fluxo completo, veja [`docs/fluxo.md`](docs/fluxo.md).

---

## Estrutura do repositório

```
kanji-translator/
├── frontend/        → Interface React (Vite)
├── backend/         → API FastAPI (Python)
└── docs/            → Documentação do projeto
```

---

## Como rodar localmente

### Pré-requisitos
- Node.js 18+
- Python 3.10+

### Front-end
```bash
cd frontend
npm install
npm run dev
```

### Back-end
```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`  
A documentação automática em `http://localhost:8000/docs`

---

## Integrações pendentes

| Componente | Responsável | Status |
|---|---|---|
| Modelo YOLO (segmentação) | — | 🟡 A implementar |
| Agente classificador | — | 🔴 A integrar |
| API de tradução | — | 🟢 Estruturado |

---

## Variáveis de ambiente

Copie os arquivos `.env.example` e renomeie para `.env` em cada pasta:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```
