"""
Modele Pydantic dla HumorFeatureExtractor
Zwracają tylko raw features, bez scoring logic
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ExtractRequest(BaseModel):
    """Request do ekstrakcji features z żartu"""
    joke_text: str = Field(..., description="Tekst żartu do analizy")
    context: Optional[Dict] = Field(default=None, description="Opcjonalny kontekst (np. URL, temat)")


class StructuralFeatures(BaseModel):
    """Cechy strukturalne żartu (setup-punchline)"""
    sentence_count: int
    has_question: bool
    sentence_lengths: List[int]
    avg_sentence_length: float
    length_variance: float
    has_clear_punchline: bool
    setup_length: int
    punchline_length: int


class KeywordFeatures(BaseModel):
    """Słowa kluczowe i markery"""
    tech_words: List[str]
    emotion_words: List[str]
    regional_markers: List[str]
    archetypes: List[str]
    taboo_markers: List[str]
    surprise_words: List[str]


class LinguisticFeatures(BaseModel):
    """Cechy lingwistyczne (NLP)"""
    pos_tags: Dict[str, int]  # {'NOUN': 5, 'VERB': 3, ...}
    entities: List[Dict[str, str]]  # [{'text': 'Polska', 'label': 'GPE'}, ...]
    comparisons_count: int
    negations_count: int
    questions_count: int
    exclamations_count: int


class AtomicFeatures(BaseModel):
    """Atomy humorystyczne (mikro-komponenty)"""
    emoji_count: int
    exclamation_count: int
    caps_words_count: int
    repetitions: List[str]
    sound_words: List[str]  # onomatopeje
    hyperboles: List[str]


class SemanticFeatures(BaseModel):
    """Cechy semantyczne (znaczeniowe)"""
    polysemy_words: List[str]  # słowa wieloznaczne
    metaphors: List[str]
    wordplay_candidates: List[str]
    semantic_fields: List[str]  # pola semantyczne (np. 'technologia', 'emocje')


class TimingFeatures(BaseModel):
    """Cechy temporalne (timing, rytm)"""
    word_count: int
    syllable_count: int
    reading_time_sec: float
    rhythm_score: float  # 0-1, based on sentence length variance
    pause_indicators: int  # kropki, przecinki, ...


class NarrativeFeatures(BaseModel):
    """Cechy narracyjne (psychoanaliza)"""
    narrative_perspective: str  # '1st person', '3rd person', etc.
    emotional_arc: str  # 'positive', 'negative', 'neutral', 'reversal'
    conflict_present: bool
    resolution_present: bool
    character_count: int


class AbsurdityFeatures(BaseModel):
    """Cechy absurdu i eskalacji"""
    contradiction_count: int
    impossibility_markers: List[str]
    exaggeration_words: List[str]
    logical_breaks: int


class HumorFeatures(BaseModel):
    """Wszystkie wyekstraktowane features dla żartu"""
    joke_text: str
    
    # 9 kategorii features (odpowiadają 9 teoriom)
    structural: StructuralFeatures
    keywords: KeywordFeatures
    linguistic: LinguisticFeatures
    atomic: AtomicFeatures
    semantic: SemanticFeatures
    timing: TimingFeatures
    narrative: NarrativeFeatures
    absurdity: AbsurdityFeatures
    
    # Metadata
    language: str = "pl"
    char_count: int
    word_count: int


class ExtractResponse(BaseModel):
    """Response z wyekstraktowanymi features"""
    features: HumorFeatures
    extraction_time_ms: float

