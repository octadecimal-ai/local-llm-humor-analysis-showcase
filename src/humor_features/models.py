"""
Modele danych dla AIJokeAnalyzer
"""
from pydantic import BaseModel, Field
from typing import Dict, Optional, List
from enum import Enum


class TheoryType(str, Enum):
    """9 teorii humoru"""
    SETUP_PUNCHLINE = "setup_punchline"
    INCONGRUITY = "incongruity"
    SEMANTIC_SHIFT = "semantic_shift"
    TIMING = "timing"
    ABSURD_ESCALATION = "absurd_escalation"
    PSYCHOANALYSIS = "psychoanalysis"
    ARCHETYPE = "archetype"
    HUMOR_ATOMS = "humor_atoms"
    REVERSE_ENGINEERING = "reverse_engineering"


class AnalyzeRequest(BaseModel):
    """Request do analizy żartu"""
    joke_text: str = Field(..., min_length=5, max_length=1000, description="Tekst żartu")
    context: Optional[Dict] = Field(default=None, description="Kontekst (strona, sytuacja)")
    persona: Optional[str] = Field(default="waldus", description="Persona bota")


class TheoryScore(BaseModel):
    """Wynik dla pojedynczej teorii"""
    score: float = Field(..., ge=0, le=10, description="Ocena 0-10")
    explanation: str = Field(..., description="Wyjaśnienie oceny")
    key_elements: List[str] = Field(default_factory=list, description="Kluczowe elementy")


class AnalyzeResponse(BaseModel):
    """Odpowiedź z analizy żartu"""
    joke_text: str
    theory_scores: Dict[str, TheoryScore] = Field(..., description="Oceny dla każdej teorii")
    dominant_theory: str = Field(..., description="Dominująca teoria")
    overall_score: float = Field(..., ge=0, le=10, description="Ogólna ocena")
    
    # Dodatkowe metryki
    reach_estimate: int = Field(..., ge=0, le=100, description="Szacowany zasięg %")
    monetization_score: int = Field(..., ge=0, le=100, description="Potencjał monetyzacji")
    recommended_improvements: List[str] = Field(default_factory=list, description="Sugerowane poprawki")
    
    # Segmentacja
    target_segments: List[str] = Field(default_factory=list, description="Segmenty docelowe")
    
    class Config:
        json_schema_extra = {
            "example": {
                "joke_text": "Automatyzacja z AI? Brzmi jak moja była...",
                "theory_scores": {
                    "incongruity": {
                        "score": 8.5,
                        "explanation": "Silny kontrast: AI/technologia vs relacje",
                        "key_elements": ["automatyzacja", "AI", "była"]
                    }
                },
                "dominant_theory": "incongruity",
                "overall_score": 7.8,
                "reach_estimate": 67,
                "monetization_score": 76,
                "recommended_improvements": ["Wzmocnić punchline"],
                "target_segments": ["Tech Enthusiasts", "Early Adopters"]
            }
        }

