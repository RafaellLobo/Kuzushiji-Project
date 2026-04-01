import time
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.yolo_agent import segment_and_normalize
from app.services.classifier import classify_kanji
from app.services.translator import translate_to_english

router = APIRouter(prefix="/translate", tags=["translate"])

@router.post("")
async def translate(image: UploadFile = File(...)):
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail={
            "success": False,
            "data": None,
            "error": {
                "code": "INVALID_IMAGE",
                "message": "O arquivo enviado não é uma imagem válida."
            }
        })

    start = time.time()
    image_bytes = await image.read()

    # Etapa 1: YOLO — segmentação e normalização
    try:
        kanji_images = segment_and_normalize(image_bytes)
    except NotImplementedError as e:
        return {
            "success": False,
            "data": None,
            "error": {"code": "YOLO_NOT_INTEGRATED", "message": str(e)}
        }

    # Etapa 2: Classificador — identificação de cada kanji
    characters = []
    for i, kanji_img in enumerate(kanji_images):
        try:
            result = classify_kanji(kanji_img)
        except NotImplementedError as e:
            return {
                "success": False,
                "data": None,
                "error": {"code": "CLASSIFIER_NOT_INTEGRATED", "message": str(e)}
            }

        characters.append({
            "order": i + 1,
            "old_kanji": result["old_kanji"],
            "modern_kanji": result["modern_kanji"],
            "confidence": result["confidence"],
            "bounding_box": result.get("bounding_box", None)
        })

    if not characters:
        return {
            "success": False,
            "data": None,
            "error": {
                "code": "NO_KANJI_FOUND",
                "message": "Nenhum kanji foi detectado na imagem."
            }
        }

    # Etapa 3: Tradução japonês moderno → inglês
    japanese_text = "".join(c["modern_kanji"] for c in characters)
    try:
        english_translation = translate_to_english(japanese_text)
    except Exception:
        return {
            "success": False,
            "data": None,
            "error": {"code": "TRANSLATION_FAILED", "message": "Falha ao traduzir o texto."}
        }

    elapsed = int((time.time() - start) * 1000)

    return {
        "success": True,
        "data": {
            "characters": characters,
            "japanese_text": japanese_text,
            "english_translation": english_translation,
            "processing_time_ms": elapsed
        },
        "error": None
    }
