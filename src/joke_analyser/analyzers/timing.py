"""
🎢 4. Mechanika timingowa (tempo i rytm)

Tu analizujesz:
- pauzy (gdzie pojawia się cięcie)
- szybkość, z jaką zmienia się kontekst
- to, czy punchline wchodzi „przed chwilą, kiedy go oczekujesz" czy „sekundę po"

W tekście szczególnie działa:
- długość zdań (krótkie = punch)
- kolejność informacji
- zaskoczenie poprzez zmianę rejestru
"""
from typing import Dict, Optional, List
from .base import BaseAnalyzer


class TimingAnalyzer(BaseAnalyzer):
    """Analiza mechaniki timingowej"""
    
    def analyze(self, joke_text: str, context: Optional[Dict] = None) -> Dict:
        """
        Analiza timing i rytmu
        
        Wykrywa:
        - Pauzy (punctuation)
        - Tempo (długość zdań)
        - Rytm (zmiana długości)
        """
        sentences = self._get_sentences(joke_text)
        
        score = 0.0
        key_elements = []
        
        # 1. Analyze sentence lengths
        if sentences:
            lengths = [len(s) for s in sentences]
            avg_length = sum(lengths) / len(lengths)
            
            # Rhythm: variation in sentence length
            if len(lengths) >= 2:
                variation = max(lengths) - min(lengths)
                if variation > 30:  # Significant variation
                    score += 2.0
                    key_elements.append("Zmienne długości zdań (rytm)")
            
            # Short punchline (last sentence shorter)
            if len(lengths) >= 2 and lengths[-1] < avg_length * 0.7:
                score += 2.5
                key_elements.append("Krótki punchline (uderzenie)")
        
        # 2. Detect pauses (punctuation)
        pause_marks = ['—', '...', '–', ';', ':']
        pause_count = sum(joke_text.count(mark) for mark in pause_marks)
        if pause_count > 0:
            score += pause_count * 1.5
            key_elements.append(f"{pause_count} pauzy")
        
        # 3. Exclamation marks (emphasis, tempo change)
        exclamation_count = joke_text.count('!')
        if exclamation_count > 0:
            score += exclamation_count * 1.0
            key_elements.append(f"{exclamation_count} wykrzykniki")
        
        # 4. Questions (tempo shift)
        question_count = joke_text.count('?')
        if question_count > 0:
            score += question_count * 0.5
            key_elements.append(f"{question_count} pytania")
        
        # 5. Register shift (formal → informal)
        if self._detect_register_shift(joke_text):
            score += 2.0
            key_elements.append("Zmiana rejestru")
        
        # Cap at 10
        score = min(10, score)
        
        explanation = self._generate_explanation(
            len(sentences), pause_count, exclamation_count
        )
        
        return {
            'score': round(score, 1),
            'explanation': explanation,
            'key_elements': key_elements
        }
    
    def _detect_register_shift(self, text: str) -> bool:
        """Wykryj zmianę rejestru (formalny → nieformalny)"""
        text_lower = text.lower()
        
        # Formal markers
        formal_words = [
            'proszę', 'uprzejmie', 'szanowny', 'poważanie',
            'niniejszy', 'rzeczony', 'stosowny'
        ]
        
        # Informal markers
        informal_words = [
            'kurczę', 'cholera', 'hej', 'ej', 'co do', 'spoko',
            'ziomek', 'stary', 'koles', 'no', 'tak jakby'
        ]
        
        has_formal = any(word in text_lower for word in formal_words)
        has_informal = any(word in text_lower for word in informal_words)
        
        return has_formal and has_informal
    
    def _generate_explanation(
        self,
        sentence_count: int,
        pause_count: int,
        exclamation_count: int
    ) -> str:
        """Generate explanation"""
        parts = []
        
        if sentence_count == 1:
            parts.append("Jeden ciągły bieg (może brakować pauzy).")
        elif sentence_count >= 3:
            parts.append(f"{sentence_count} zdań (dobry rytm).")
        
        if pause_count > 0:
            parts.append(f"Wykryto {pause_count} pauzy (timing).")
        
        if exclamation_count > 0:
            parts.append(f"Wykrzykniki dodają energii.")
        
        if not parts:
            parts.append("Brak wyraźnych elementów timingowych.")
        
        return " ".join(parts)

