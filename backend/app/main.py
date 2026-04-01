from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.translate import router as translate_router

app = FastAPI(
    title="Kanji Translator API",
    description="API para tradução de kanjis antigos para inglês.",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # porta padrão do Vite
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(translate_router)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Kanji Translator API rodando."}
