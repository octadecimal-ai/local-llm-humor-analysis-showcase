"""
JokeAnalyzer - główny analyzer używający 9 teorii humoru
"""
from typing import Dict, List
from .models import AnalyzeRequest, AnalyzeResponse, TheoryScore, TheoryType
from .analyzers import (
    SetupPunchlineAnalyzer,
    IncongruityAnalyzer,
    SemanticShiftAnalyzer,
    TimingAnalyzer,
    AbsurdEscalationAnalyzer,
    PsychoanalysisAnalyzer,
    ArchetypeAnalyzer,
    HumorAtomsAnalyzer,
    ReverseEngineeringAnalyzer,
)


class JokeAnalyzer:
    """
    Główny analyzer używający 9 teorii humoru
    
    9 teorii:
    1. Setup-punchline (strukturalna autopsja)
    2. Teoria niespójności (incongruity)
    3. Deformacja znaczeniowa (semantic shift)
    4. Mechanika timingowa (tempo i rytm)
    5. Eskalacja absurdu (amplifikacja)
    6. Narracyjna psychoanaliza
    7. Archetypowość (archetypy humoru)
    8. Atomy humorystyczne (mikro-komponenty)
    9. Reverse engineering (mechanizm bez treści)
    """
    
    def __init__(self):
        """Initialize all 9 analyzers"""
        self.analyzers = {
            TheoryType.SETUP_PUNCHLINE: SetupPunchlineAnalyzer(),
            TheoryType.INCONGRUITY: IncongruityAnalyzer(),
            TheoryType.SEMANTIC_SHIFT: SemanticShiftAnalyzer(),
            TheoryType.TIMING: TimingAnalyzer(),
            TheoryType.ABSURD_ESCALATION: AbsurdEscalationAnalyzer(),
            TheoryType.PSYCHOANALYSIS: PsychoanalysisAnalyzer(),
            TheoryType.ARCHETYPE: ArchetypeAnalyzer(),
            TheoryType.HUMOR_ATOMS: HumorAtomsAnalyzer(),
            TheoryType.REVERSE_ENGINEERING: ReverseEngineeringAnalyzer(),
        }
        
        # Weights for different goals
        self.weights = {
            'reach': {
                TheoryType.SETUP_PUNCHLINE: 0.35,
                TheoryType.ARCHETYPE: 0.30,
                TheoryType.INCONGRUITY: 0.20,
                TheoryType.TIMING: 0.15,
            },
            'monetization': {
                TheoryType.PSYCHOANALYSIS: 0.40,
                TheoryType.ARCHETYPE: 0.25,
                TheoryType.INCONGRUITY: 0.20,
                TheoryType.ABSURD_ESCALATION: 0.15,
            },
            'viral': {
                TheoryType.ABSURD_ESCALATION: 0.40,
                TheoryType.ARCHETYPE: 0.25,
                TheoryType.SEMANTIC_SHIFT: 0.20,
                TheoryType.TIMING: 0.15,
            },
        }
    
    async def analyze(self, request: AnalyzeRequest) -> AnalyzeResponse:
        """
        Analizuj żart według wszystkich 9 teorii
        
        Args:
            request: AnalyzeRequest z tekstem żartu
            
        Returns:
            AnalyzeResponse z wynikami analizy
        """
        joke_text = request.joke_text
        context = request.context
        
        # Run all analyzers
        theory_scores = {}
        raw_scores = {}
        
        for theory_type, analyzer in self.analyzers.items():
            result = analyzer.analyze(joke_text, context)
            
            theory_scores[theory_type.value] = TheoryScore(
                score=result['score'],
                explanation=result['explanation'],
                key_elements=result.get('key_elements', [])
            )
            
            raw_scores[theory_type] = result['score']
        
        # Calculate overall score (weighted average)
        overall_score = sum(raw_scores.values()) / len(raw_scores)
        
        # Determine dominant theory
        dominant_theory = max(raw_scores, key=raw_scores.get).value
        
        # Calculate reach estimate (based on reach weights)
        reach_estimate = self._calculate_weighted_score(raw_scores, 'reach')
        
        # Calculate monetization score (based on monetization weights)
        monetization_score = self._calculate_weighted_score(raw_scores, 'monetization')
        
        # Generate recommendations
        recommended_improvements = self._generate_recommendations(
            raw_scores, theory_scores
        )
        
        # Determine target segments
        target_segments = self._determine_segments(raw_scores)
        
        return AnalyzeResponse(
            joke_text=joke_text,
            theory_scores=theory_scores,
            dominant_theory=dominant_theory,
            overall_score=round(overall_score, 1),
            reach_estimate=reach_estimate,
            monetization_score=monetization_score,
            recommended_improvements=recommended_improvements,
            target_segments=target_segments,
        )
    
    def _calculate_weighted_score(
        self, 
        raw_scores: Dict[TheoryType, float], 
        goal: str
    ) -> int:
        """
        Calculate weighted score for a specific goal
        
        Args:
            raw_scores: Raw scores from analyzers
            goal: 'reach', 'monetization', or 'viral'
            
        Returns:
            Score 0-100
        """
        if goal not in self.weights:
            return 50
        
        weights = self.weights[goal]
        
        weighted_sum = 0.0
        for theory_type, weight in weights.items():
            score = raw_scores.get(theory_type, 0.0)
            weighted_sum += score * weight
        
        # Convert to 0-100 scale
        result = int(weighted_sum * 10)
        return max(0, min(100, result))
    
    def _generate_recommendations(
        self,
        raw_scores: Dict[TheoryType, float],
        theory_scores: Dict[str, TheoryScore]
    ) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Find weak theories (score < 5)
        for theory_type, score in raw_scores.items():
            if score < 5.0:
                recommendations.append(
                    f"Wzmocnić {theory_type.value}: obecnie {score}/10"
                )
        
        # Specific recommendations
        if raw_scores.get(TheoryType.SETUP_PUNCHLINE, 0) < 6:
            recommendations.append("Dodać wyraźniejszy setup-punchline")
        
        if raw_scores.get(TheoryType.INCONGRUITY, 0) < 6:
            recommendations.append("Zwiększyć niespójność (zderzenie domen)")
        
        if raw_scores.get(TheoryType.TIMING, 0) < 6:
            recommendations.append("Poprawić timing (krótszy punchline)")
        
        # If too many recommendations, prioritize
        if len(recommendations) > 5:
            recommendations = recommendations[:5]
        
        return recommendations
    
    def _determine_segments(
        self,
        raw_scores: Dict[TheoryType, float]
    ) -> List[str]:
        """Determine target user segments"""
        segments = []
        
        # Segment A: Tech Enthusiasts
        if (raw_scores.get(TheoryType.INCONGRUITY, 0) >= 7 and
            raw_scores.get(TheoryType.PSYCHOANALYSIS, 0) >= 6):
            segments.append("Tech Enthusiasts")
        
        # Segment B: Early Adopters
        if (raw_scores.get(TheoryType.ARCHETYPE, 0) >= 7 and
            raw_scores.get(TheoryType.INCONGRUITY, 0) >= 6):
            segments.append("Early Adopters")
        
        # Segment C: Curious Normies
        if (raw_scores.get(TheoryType.SETUP_PUNCHLINE, 0) >= 7 and
            raw_scores.get(TheoryType.ARCHETYPE, 0) >= 6):
            segments.append("Curious Normies")
        
        # Segment D: Young Demographics
        if raw_scores.get(TheoryType.ABSURD_ESCALATION, 0) >= 8:
            segments.append("Young Demographics (18-34)")
        
        # Default
        if not segments:
            segments.append("General Audience")
        
        return segments

