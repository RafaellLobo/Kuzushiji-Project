# 📜 Kanji Translator (Kuzushiji)

Sistema Full-Stack de tradução de documentos históricos japoneses (Kuzushiji) para o inglês e japonês moderno, utilizando Visão Computacional e Processamento de Linguagem Natural.

## 🔄 Fluxo Geral

O projeto foi desenhado para processar os dados em etapas isoladas:

```text
Usuário envia foto → YOLO segmenta os kanjis → Classificador identifica cada caractere → Tradução para inglês
```

Para entender o fluxo completo, veja [`docs/fluxo.md`](docs/fluxo.md).

---

## Estrutura do repositório

```
kanji-translator/
├── frontend/                  # Interface React (Vite)
│   ├── src/
│   │   ├── components/        # Componentes visuais isolados (Views)
│   │   ├── hooks/             # Lógica de negócio isolada
│   │   └── assets/            # Imagens e estilos estáticos
├── backend/                   # API FastAPI (Python)
│   ├── app/
│   │   ├── routes/            # Definição dos Endpoints (ex: /translate)
│   │   ├── services/          # Lógica pesada da IA (YOLO, Classificador)
│   │   └── temp/              # Armazenamento temporário de arquivos para a IA
└── docs/                      # Documentação do projeto
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
source .venv/Scripts/activate        # No Linux/Mac use: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`  
A documentação automática em `http://localhost:8000/docs`

---

## Integrações pendentes

| Componente                | Responsável | Status           |
| ------------------------- | ----------- | ---------------- |
| Modelo YOLO (segmentação) | —           | 🟡 A implementar |
| Agente classificador      | —           | 🔴 A integrar    |
| API de tradução           | —           | 🟢 Estruturado   |

---

## Variáveis de ambiente

Copie os arquivos `.env.example` e renomeie para `.env` em cada pasta:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```
