"""
🧠 6. Narracyjna psychoanaliza

Analizujesz, jaki stan psychiczny mówiącego jest fundamentem żartu.

Zadajesz pytania:
1. Kto mówi?
2. Z jakiego powodu jest to dla niego zabawne?
3. Co próbuje ukryć lub odreagować?

Walduś jest zabawny, bo jego żart jest równocześnie:
- autoironią
- pretensją
- wyrzutem
- rozpaczą
- meta-komentarzem do własnej nicości
"""
from typing import Dict, Optional
from .base import BaseAnalyzer


class PsychoanalysisAnalyzer(BaseAnalyzer):
    """Analiza psychoanalityczna humoru"""
    
    # Psychological states
    PSYCHOLOGICAL_STATES = {
        'despair': ['rozpacz', 'beznadziejność', 'pustek', 'nicość', 'koniec'],
        'anger': ['wkurza', 'denerwuje', 'wścieka', 'frustruje', 'irytuje'],
        'sadness': ['smutek', 'żal', 'tęsknota', 'samotność', 'melancholia'],
        'fear': ['strach', 'lęk', 'obawa', 'panika', 'przerażenie'],
        'self-deprecation': ['głupi', 'idiota', 'debil', 'nieudacznik', 'fail'],
        'projection': ['to nie ja', 'to ty', 'to oni', 'wina nie moja'],
    }
    
    # Defense mechanisms
    DEFENSE_MECHANISMS = [
        'przecież', 'właściwie', 'w sumie', 'no dobra',
        'może', 'chyba', 'jakby', 'niby'
    ]
    
    def analyze(self, joke_text: str, context: Optional[Dict] = None) -> Dict:
        """
        Analiza psychoanalityczna
        
        Wykrywa:
        - Stan psychiczny mówiącego
        - Mechanizmy obronne
        - Projekcję, racjonalizację
        """
        text_lower = joke_text.lower()
        
        score = 0.0
        key_elements = []
        detected_states = []
        
        # 1. Detect psychological states
        for state_name, markers in self.PSYCHOLOGICAL_STATES.items():
            if any(marker in text_lower for marker in markers):
                score += 2.0
                detected_states.append(state_name)
                key_elements.append(f"Stan: {state_name}")
        
        # 2. Detect defense mechanisms
        defense_count = sum(
            1 for marker in self.DEFENSE_MECHANISMS 
            if f' {marker} ' in f' {text_lower} '
        )
        if defense_count > 0:
            score += defense_count * 1.5
            key_elements.append(f"{defense_count} mechanizmów obronnych")
        
        # 3. Self-reference (ja, mnie, moje)
        self_ref_count = (
            text_lower.count(' ja ') + 
            text_lower.count(' mnie ') + 
            text_lower.count(' moje ')
        )
        if self_ref_count > 0:
            score += self_ref_count * 0.5
            key_elements.append(f"Auto-referencja ({self_ref_count}x)")
        
        # 4. Projection (blame others)
        if self._detect_projection(text_lower):
            score += 2.0
            key_elements.append("Projekcja (przerzucenie winy)")
        
        # 5. Meta-commentary (komentarz o sobie)
        if self._detect_meta_commentary(text_lower):
            score += 2.5
            key_elements.append("Meta-komentarz")
        
        # Cap at 10
        score = min(10, score)
        
        explanation = self._generate_explanation(
            detected_states, defense_count, self_ref_count
        )
        
        return {
            'score': round(score, 1),
            'explanation': explanation,
            'key_elements': key_elements
        }
    
    def _detect_projection(self, text: str) -> bool:
        """Wykryj projekcję (przerzucenie winy)"""
        projection_patterns = [
            'to ty', 'to twoja', 'to wasz', 'to ich',
            'wina nie moja', 'nie ja', 'to nie ze mną'
        ]
        
        return any(pattern in text for pattern in projection_patterns)
    
    def _detect_meta_commentary(self, text: str) -> bool:
        """Wykryj meta-komentarz (komentarz o sobie/żarcie)"""
        meta_patterns = [
            'wiem że', 'zdaję sobie sprawę', 'rozumiem że',
            'to znaczy', 'czyli', 'innymi słowy'
        ]
        
        return any(pattern in text for pattern in meta_patterns)
    
    def _generate_explanation(
        self,
        detected_states: list,
        defense_count: int,
        self_ref_count: int
    ) -> str:
        """Generate explanation"""
        parts = []
        
        if detected_states:
            parts.append(f"Wykryto stany: {', '.join(detected_states)}.")
        
        if defense_count > 0:
            parts.append(f"{defense_count} mechanizmów obronnych.")
        
        if self_ref_count > 2:
            parts.append("Silna auto-referencja (narcyzm?).")
        
        if not parts:
            parts.append("Brak wyraźnych elementów psychoanalitycznych.")
        
        return " ".join(parts)

