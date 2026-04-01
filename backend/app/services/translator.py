# =============================================================================
# Módulo de tradução — Japonês moderno → Inglês
# =============================================================================
# Usando MyMemory API (gratuita, sem necessidade de chave).
# Para produção, considere substituir por DeepL ou Google Translate.
# =============================================================================

import httpx

def translate_to_english(japanese_text: str) -> str:
    """
    Recebe texto em japonês moderno.
    Retorna tradução em inglês.
    """
    url = "https://api.mymemory.translated.net/get"
    params = {"q": japanese_text, "langpair": "ja|en"}

    response = httpx.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()
    return data["responseData"]["translatedText"]
