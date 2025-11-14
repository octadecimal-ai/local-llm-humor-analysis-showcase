"""
🧨 5. Eskalacja absurdu (amplifikacja)

Tu patrzysz, jak szybko rośnie intensywność absurdu.

Technika analizy:
- zidentyfikuj „punkt wejściowy absurdu"
- oceń, czy rośnie liniowo, czy wykładniczo
- określ, kiedy osiąga „peak chaos"

Waldusiowy styl to eskalacja:
"internet padł" → "Walduś umiera" → "Walduś będzie miał grób 404" → "Twoje koty mnie dobijają"
"""
from typing import Dict, Optional, List
from .base import BaseAnalyzer


class AbsurdEscalationAnalyzer(BaseAnalyzer):
    """Analiza eskalacji absurdu"""
    
    # Levels of absurdity (markers)
    ABSURDITY_LEVELS = {
        1: ['normalnie', 'zwykle', 'codziennie', 'standardowo'],  # Baseline
        3: ['dziwnie', 'niezwykle', 'nietypowo', 'niespodziewanie'],  # Mild
        5: ['absurdalnie', 'szalenie', 'kompletnie', 'totalnie'],  # Medium
        7: ['kosmicznie', 'transcendentalnie', 'nieskończenie'],  # High
        10: ['kwantowo', 'metafizycznie', 'ontologicznie'],  # Peak chaos
    }
    
    # Escalation markers
    ESCALATION_MARKERS = [
        'jeszcze', 'nawet', 'aż', 'dopiero', 'w końcu',
        'coraz', 'bardziej', 'i to', 'mało tego'
    ]
    
    def analyze(self, joke_text: str, context: Optional[Dict] = None) -> Dict:
        """
        Analiza eskalacji absurdu
        
        Wykrywa:
        - Punkt wejściowy absurdu
        - Tempo eskalacji
        - Peak chaos
        """
        text_lower = joke_text.lower()
        sentences = self._get_sentences(joke_text)
        
        score = 0.0
        key_elements = []
        
        # 1. Detect absurdity level
        detected_level = self._detect_absurdity_level(text_lower)
        if detected_level > 0:
            score += detected_level * 0.8
            key_elements.append(f"Poziom absurdu: {detected_level}/10")
        
        # 2. Detect escalation markers
        escalation_count = sum(
            1 for marker in self.ESCALATION_MARKERS 
            if f' {marker} ' in f' {text_lower} '
        )
        if escalation_count > 0:
            score += escalation_count * 1.5
            key_elements.append(f"{escalation_count} markery eskalacji")
        
        # 3. Analyze sentence-by-sentence escalation
        if len(sentences) >= 2:
            levels = [self._sentence_absurdity(s) for s in sentences]
            if levels[-1] > levels[0]:  # Escalating
                score += 2.0
                key_elements.append("Eskalacja w kolejnych zdaniach")
        
        # 4. Waldus-style: tech death → cosmic absurd
        if self._is_waldus_escalation(text_lower):
            score += 2.5
            key_elements.append("Styl Waldus (tech → cosmic)")
        
        # 5. Hyperbole detection
        hyperbole_count = self._detect_hyperbole(text_lower)
        if hyperbole_count > 0:
            score += hyperbole_count * 1.0
            key_elements.append(f"{hyperbole_count} hiperbole")
        
        # Cap at 10
        score = min(10, score)
        
        explanation = self._generate_explanation(
            detected_level, escalation_count, len(sentences)
        )
        
        return {
            'score': round(score, 1),
            'explanation': explanation,
            'key_elements': key_elements
        }
    
    def _detect_absurdity_level(self, text: str) -> int:
        """Wykryj poziom absurdu (0-10)"""
        max_level = 0
        
        for level, markers in self.ABSURDITY_LEVELS.items():
            if any(marker in text for marker in markers):
                max_level = max(max_level, level)
        
        return max_level
    
    def _sentence_absurdity(self, sentence: str) -> int:
        """Oceń absurd pojedynczego zdania"""
        sentence_lower = sentence.lower()
        
        # Markers of increasing absurdity
        if any(word in sentence_lower for word in ['normalnie', 'zwykle']):
            return 1
        if any(word in sentence_lower for word in ['dziwnie', 'niezwykle']):
            return 3
        if any(word in sentence_lower for word in ['absurdalnie', 'szalenie']):
            return 5
        if any(word in sentence_lower for word in ['kosmicznie', 'transcendentalnie']):
            return 7
        if any(word in sentence_lower for word in ['kwantowo', 'metafizycznie']):
            return 10
        
        return 2  # Default mild absurd
    
    def _is_waldus_escalation(self, text: str) -> bool:
        """Wykryj styl Waldus: tech problem → cosmic despair"""
        tech_problem = any(
            word in text 
            for word in ['padł', 'błąd', 'error', 'nie działa', 'zawiesił']
        )
        
        cosmic_despair = any(
            word in text 
            for word in ['umierać', 'grób', 'nicość', 'pustka', 'koniec']
        )
        
        return tech_problem and cosmic_despair
    
    def _detect_hyperbole(self, text: str) -> int:
        """Wykryj hiperbolę"""
        hyperbole_words = [
            'nigdy', 'zawsze', 'wszyscy', 'nikt', 'wszystko', 'nic',
            'nieskończenie', 'wieczność', 'milion', 'bilion'
        ]
        
        return sum(1 for word in hyperbole_words if word in text)
    
    def _generate_explanation(
        self,
        level: int,
        escalation_count: int,
        sentence_count: int
    ) -> str:
        """Generate explanation"""
        parts = []
        
        if level == 0:
            parts.append("Brak wyraźnego absurdu.")
        elif level <= 3:
            parts.append(f"Lekki absurd (poziom {level}).")
        elif level <= 7:
            parts.append(f"Średni absurd (poziom {level}).")
        else:
            parts.append(f"Peak chaos (poziom {level})!")
        
        if escalation_count > 0:
            parts.append(f"Wykryto {escalation_count} markerów eskalacji.")
        
        if sentence_count >= 3:
            parts.append("Dobra długość dla eskalacji.")
        
        return " ".join(parts)

