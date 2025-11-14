"""
🧩 1. Model setup–punchline (strukturalna autopsja żartu)

Rozbijasz żart na:
- Setup – budowanie oczekiwania (normalna sytuacja)
- Twist – złamanie oczekiwania (coś nielogicznego lub niespodziewanego)
- Punchline – logiczna konsekwencja twistu, ale z absurdalnym przeskokiem
"""
from typing import Dict, List, Optional
from .base import BaseAnalyzer
import re


class SetupPunchlineAnalyzer(BaseAnalyzer):
    """Analiza struktury setup-punchline"""
    
    # Markers dla setupu (normalna sytuacja)
    SETUP_MARKERS = [
        'kiedy', 'gdy', 'jeśli', 'zawsze', 'często', 'zazwyczaj',
        'normalnie', 'zwykle', 'wczoraj', 'dziś', 'rano'
    ]
    
    # Markers dla twistu (zmiana kierunku)
    TWIST_MARKERS = [
        'ale', 'jednak', 'niestety', 'okazuje się', 'nagle', 
        'wtedy', 'to', 'więc', 'zamiast', 'niż'
    ]
    
    # Punctuation markers (często przed punchline)
    PUNCHLINE_PUNCTUATION = ['—', '...', ':', '–', '!']
    
    def analyze(self, joke_text: str, context: Optional[Dict] = None) -> Dict:
        """
        Analiza setup-punchline structure
        
        Pytania:
        1. Jakie oczekiwanie buduje setup?
        2. Jak punchline je łamie?
        3. Dlaczego ten twist jest zabawny, a nie tylko losowy?
        """
        sentences = self._get_sentences(joke_text)
        
        # Identify structure
        has_setup = self._detect_setup(joke_text, sentences)
        has_twist = self._detect_twist(joke_text)
        has_punchline = self._detect_punchline(joke_text, sentences)
        
        # Calculate score
        score = 0.0
        key_elements = []
        
        if has_setup:
            score += 3.0
            key_elements.append("Setup wykryty")
        
        if has_twist:
            score += 3.0
            key_elements.append("Twist wykryty")
        
        if has_punchline:
            score += 3.0
            key_elements.append("Punchline wykryty")
        
        # Bonus: clear structure
        if len(sentences) >= 2:
            score += 1.0
            key_elements.append(f"Struktura: {len(sentences)} zdania")
        
        # Analyze timing (czy punchline na końcu?)
        if sentences and self._is_punchline_at_end(sentences):
            score += 0.5
            key_elements.append("Punchline na końcu")
        
        # Penalty: za krótki (< 50 znaków)
        if len(joke_text) < 50:
            score -= 1.0
        
        # Penalty: za długi (> 300 znaków)
        if len(joke_text) > 300:
            score -= 0.5
        
        score = max(0, min(10, score))
        
        explanation = self._generate_explanation(
            has_setup, has_twist, has_punchline, len(sentences)
        )
        
        return {
            'score': round(score, 1),
            'explanation': explanation,
            'key_elements': key_elements
        }
    
    def _detect_setup(self, text: str, sentences: List[str]) -> bool:
        """Wykryj setup (budowanie oczekiwania)"""
        text_lower = text.lower()
        
        # Check for setup markers
        for marker in self.SETUP_MARKERS:
            if marker in text_lower:
                return True
        
        # Check first sentence (często jest setupem)
        if sentences and len(sentences[0]) > 20:
            return True
        
        return False
    
    def _detect_twist(self, text: str) -> bool:
        """Wykryj twist (złamanie oczekiwania)"""
        text_lower = text.lower()
        
        for marker in self.TWIST_MARKERS:
            if f' {marker} ' in f' {text_lower} ':
                return True
        
        return False
    
    def _detect_punchline(self, text: str, sentences: List[str]) -> bool:
        """Wykryj punchline"""
        # Check for punctuation before last part
        for punct in self.PUNCHLINE_PUNCTUATION:
            if punct in text:
                return True
        
        # Check if last sentence is shorter (często punchline)
        if len(sentences) >= 2:
            last_len = len(sentences[-1])
            prev_len = len(sentences[-2])
            if last_len < prev_len * 0.7:  # Ostatnie 30% krótsze
                return True
        
        # Check for question mark followed by answer
        if '?' in text:
            parts = text.split('?')
            if len(parts) >= 2 and len(parts[1].strip()) > 10:
                return True
        
        return False
    
    def _is_punchline_at_end(self, sentences: List[str]) -> bool:
        """Czy punchline jest na końcu?"""
        if len(sentences) < 2:
            return False
        
        # Last sentence should be shorter or have exclamation
        last = sentences[-1]
        if '!' in last or len(last) < 80:
            return True
        
        return False
    
    def _generate_explanation(
        self, 
        has_setup: bool, 
        has_twist: bool, 
        has_punchline: bool,
        sentence_count: int
    ) -> str:
        """Generate explanation"""
        parts = []
        
        if has_setup and has_twist and has_punchline:
            parts.append("Pełna struktura setup-twist-punchline.")
        elif has_setup and has_punchline:
            parts.append("Struktura setup-punchline bez wyraźnego twista.")
        elif has_setup:
            parts.append("Setup wykryty, ale brak wyraźnego punchline.")
        else:
            parts.append("Brak wyraźnej struktury setup-punchline.")
        
        if sentence_count == 1:
            parts.append("Żart w jednym zdaniu (może być za krótki).")
        elif sentence_count >= 3:
            parts.append(f"Żart w {sentence_count} zdaniach (dobra struktura).")
        
        return " ".join(parts)

