"""
🥼 3. Deformacja znaczeniowa (semantic shift)

Analizujesz moment, w którym słowo zmienia znaczenie lub kontekst.

Przykłady:
- gry słów
- dwuznaczności
- przestawienia znaczeń
- literalizacja metafory („nie mam internetu" → „umieram jako byt cyfrowy")
"""
from typing import Dict, Optional
from .base import BaseAnalyzer
import re


class SemanticShiftAnalyzer(BaseAnalyzer):
    """Analiza deformacji znaczeniowej"""
    
    # Words with multiple meanings (homophones, polysemy)
    AMBIGUOUS_WORDS = [
        'bank', 'zamek', 'klucz', 'mysz', 'łóżko', 'kwadrans',
        'pole', 'korzeń', 'para', 'bat', 'bat', 'kod', 'błąd'
    ]
    
    # Metaphor markers
    METAPHOR_MARKERS = [
        'jak', 'jakby', 'przypomina', 'wygląda', 'brzmi',
        'jest jak', 'niczym', 'podobnie'
    ]
    
    def analyze(self, joke_text: str, context: Optional[Dict] = None) -> Dict:
        """
        Analiza semantic shift
        
        Wykrywa:
        - Gry słów
        - Dwuznaczności
        - Literalizację metafor
        """
        text_lower = joke_text.lower()
        
        score = 0.0
        key_elements = []
        
        # 1. Detect ambiguous words
        ambiguous_count = sum(
            1 for word in self.AMBIGUOUS_WORDS 
            if word in text_lower
        )
        if ambiguous_count > 0:
            score += ambiguous_count * 1.5
            key_elements.append(f"{ambiguous_count} wieloznaczne słowa")
        
        # 2. Detect metaphor markers
        metaphor_count = sum(
            1 for marker in self.METAPHOR_MARKERS 
            if marker in text_lower
        )
        if metaphor_count > 0:
            score += metaphor_count * 2.0
            key_elements.append(f"{metaphor_count} markery metafor")
        
        # 3. Detect quotation marks (often signal shift)
        quote_count = text_lower.count('"') + text_lower.count("'") + text_lower.count('„') + text_lower.count('"')
        if quote_count >= 2:
            score += 1.5
            key_elements.append("Cytaty (zmiana kontekstu)")
        
        # 4. Literalization of metaphor
        if self._detect_literalization(text_lower):
            score += 2.5
            key_elements.append("Literalizacja metafory")
        
        # 5. Parentheses (meta-commentary, shift in meaning)
        if '(' in joke_text and ')' in joke_text:
            score += 1.0
            key_elements.append("Komentarz w nawiasach")
        
        # Cap at 10
        score = min(10, score)
        
        explanation = self._generate_explanation(
            ambiguous_count, metaphor_count, quote_count
        )
        
        return {
            'score': round(score, 1),
            'explanation': explanation,
            'key_elements': key_elements
        }
    
    def _detect_literalization(self, text: str) -> bool:
        """Wykryj literalizację metafory"""
        # Common metaphors that get literalized
        metaphor_pairs = [
            ('nie mam internetu', 'umieram'),
            ('brak połączenia', 'śmierć'),
            ('offline', 'martw'),
            ('błąd', 'cierpię'),
            ('zawiesił się', 'panika'),
        ]
        
        for metaphor, literal in metaphor_pairs:
            if metaphor in text and literal in text:
                return True
        
        return False
    
    def _generate_explanation(
        self,
        ambiguous_count: int,
        metaphor_count: int,
        quote_count: int
    ) -> str:
        """Generate explanation"""
        parts = []
        
        if ambiguous_count > 0:
            parts.append(f"Użyto {ambiguous_count} wieloznacznych słów.")
        
        if metaphor_count > 0:
            parts.append(f"Wykryto {metaphor_count} metafor.")
        
        if quote_count >= 2:
            parts.append("Cytaty sygnalizują zmianę znaczenia.")
        
        if not parts:
            parts.append("Brak wyraźnych przesunięć semantycznych.")
        
        return " ".join(parts)

