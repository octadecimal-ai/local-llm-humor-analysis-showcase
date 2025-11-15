"""
FastAPI router dla HumorFeatureExtractor
Endpoint: /humor-features/extract
"""
from fastapi import APIRouter, HTTPException
from .feature_models import ExtractRequest, ExtractResponse
from .extractor import HumorFeatureExtractor

router = APIRouter()

# Initialize extractor (singleton)
try:
    extractor = HumorFeatureExtractor()
except RuntimeError as e:
    extractor = None
    print(f"⚠️  HumorFeatureExtractor nie został zainicjalizowany: {e}")


@router.post("/extract", response_model=ExtractResponse)
async def extract_humor_features(request: ExtractRequest):
    """
    Ekstrahuj humor features z żartu (bez scoring)
    
    **Args:**
    - joke_text: Tekst żartu do analizy
    - context: Opcjonalny kontekst (dict)
    
    **Returns:**
    - features: HumorFeatures z 9 kategoriami features
    - extraction_time_ms: Czas ekstrakcji w ms
    
    **Example:**
    ```json
    {
      "joke_text": "Dlaczego programista poszedł do lasu? Bo szukał drzewa binarnego!",
      "context": {"source": "reddit", "topic": "tech_humor"}
    }
    ```
    """
    if extractor is None:
        raise HTTPException(
            status_code=500,
            detail="HumorFeatureExtractor nie jest dostępny. Sprawdź instalację spaCy i modelu pl_core_news_lg."
        )
    
    try:
        response = await extractor.extract(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Błąd podczas ekstrakcji features: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check dla humor features extractor"""
    return {
        "status": "healthy" if extractor is not None else "unhealthy",
        "service": "humor_features_extractor",
        "version": "1.0.0"
    }

