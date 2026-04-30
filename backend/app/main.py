from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import translate
from app.services.translation_pipeline import build_translation_pipeline
from app.services.translator import TranslationService


@asynccontextmanager
async def lifespan(app: FastAPI):
    timeout = httpx.Timeout(connect=2.0, read=8.0, write=2.0, pool=2.0)
    async with httpx.AsyncClient(timeout=timeout) as http_client:
        translation_service = TranslationService(http_client=http_client)
        app.state.translation_pipeline = build_translation_pipeline(translation_service)
        yield


app = FastAPI(title="Kuzushiji API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(translate.router)

@app.get("/")
def read_root():
    return {"message": "API do Projeto Kuzushiji rodando perfeitamente!"}
