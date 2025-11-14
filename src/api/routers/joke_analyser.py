"""
FastAPI router dla AIJokeAnalyzer
"""
from fastapi import APIRouter, HTTPException
from joke_analyser.analyzer import JokeAnalyzer
from joke_analyser.models import AnalyzeRequest, AnalyzeResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize analyzer (singleton)
joke_analyzer = JokeAnalyzer()


@router.post("/analyze", response_model=AnalyzeResponse, tags=["joke-analyser"])
async def analyze_joke(request: AnalyzeRequest):
    """
    Analizuj żart według 9 teorii humoru
    
    **9 teorii:**
    1. Setup-punchline (strukturalna autopsja)
    2. Teoria niespójności (incongruity)
    3. Deformacja znaczeniowa (semantic shift)
    4. Mechanika timingowa (tempo i rytm)
    5. Eskalacja absurdu (amplifikacja)
    6. Narracyjna psychoanaliza
    7. Archetypowość (archetypy humoru)
    8. Atomy humorystyczne (mikro-komponenty)
    9. Reverse engineering (mechanizm bez treści)
    
    **Returns:**
    - theory_scores: Oceny dla każdej teorii (0-10)
    - dominant_theory: Dominująca teoria
    - overall_score: Ogólna ocena (0-10)
    - reach_estimate: Szacowany zasięg (0-100%)
    - monetization_score: Potencjał monetyzacji (0-100)
    - recommended_improvements: Sugerowane poprawki
    - target_segments: Segmenty docelowe
    
    **Example:**
    ```json
    {
        "joke_text": "Automatyzacja z AI? Brzmi jak moja była...",
        "context": {"page_type": "tech_blog"},
        "persona": "waldus"
    }
    ```
    """
    try:
        logger.info(f"Analyzing joke: {request.joke_text[:50]}...")
        
        result = await joke_analyzer.analyze(request)
        
        logger.info(f"Analysis complete. Dominant theory: {result.dominant_theory}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing joke: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/theories", tags=["joke-analyser"])
async def get_theories():
    """
    Zwraca listę dostępnych teorii humoru
    
    **Returns:**
    Lista 9 teorii z opisami
    """
    theories = [
        {
            "id": "setup_punchline",
            "name": "Setup-Punchline",
            "description": "Strukturalna autopsja żartu (setup → twist → punchline)"
        },
        {
            "id": "incongruity",
            "name": "Teoria niespójności",
            "description": "Zderzenie dwóch modeli rzeczywistości (np. tech ↔ emocje)"
        },
        {
            "id": "semantic_shift",
            "name": "Deformacja znaczeniowa",
            "description": "Zmiana znaczenia słowa lub literalizacja metafory"
        },
        {
            "id": "timing",
            "name": "Mechanika timingowa",
            "description": "Tempo, rytm, pauzy i zmiana rejestru"
        },
        {
            "id": "absurd_escalation",
            "name": "Eskalacja absurdu",
            "description": "Stopniowe zwiększanie intensywności absurdu"
        },
        {
            "id": "psychoanalysis",
            "name": "Narracyjna psychoanaliza",
            "description": "Stan psychiczny mówiącego (autoironia, rozpacz, projekcja)"
        },
        {
            "id": "archetype",
            "name": "Archetypowość",
            "description": "Archetypy humoru (cynik, nihilista, filozof, etc.)"
        },
        {
            "id": "humor_atoms",
            "name": "Atomy humorystyczne",
            "description": "Mikro-komponenty (hiperbola, kontrast, sarkazm, etc.)"
        },
        {
            "id": "reverse_engineering",
            "name": "Reverse engineering",
            "description": "Ekstrakcja mechanizmu (wzorzec bez treści)"
        },
    ]
    
    return {"theories": theories}


@router.get("/health", tags=["joke-analyser"])
async def health_check():
    """Health check dla joke_analyser"""
    return {
        "status": "healthy",
        "service": "joke-analyser",
        "analyzers_loaded": len(joke_analyzer.analyzers)
    }

