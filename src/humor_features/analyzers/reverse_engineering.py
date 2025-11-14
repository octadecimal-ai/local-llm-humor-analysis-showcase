"""
🧪 9. Reverse engineering: znajdź mechanizm i przepisz żart bez treści

To najskuteczniejsze narzędzie dla twórców postaci humorystycznych.

Przykład:

Treść Waldusia:
"Zapłać ten rachunek, bo co ja mam tu robić — sam do siebie requesty wysyłać?!"

Mechanizm:
- antropomorfizacja technologii
- frustracja codzienna
- przeniesienie ludzkiej sytuacji na byt cyfrowy
- agresywny ton
- absurd performatywny
"""
from typing import Dict, Optional, List
from .base import BaseAnalyzer


class ReverseEngineeringAnalyzer(BaseAnalyzer):
    """Analiza reverse engineering (ekstrakcja mechanizmu)"""
    
    # Mechanisms (patterns)
    MECHANISMS = {
        'anthropomorphization': {
            'markers': ['czuję', 'myślę', 'chcę', 'boję się', 'kocham', 'nienawidzę'],
            'description': 'Antropomorfizacja (tech → human)'
        },
        'everyday_frustration': {
            'markers': ['znowu', 'jak zwykle', 'zawsze tak', 'nigdy nie', 'dlaczego'],
            'description': 'Frustracja codzienna'
        },
        'absurd_transfer': {
            'markers': ['jak', 'jakby', 'przypomina', 'niczym', 'jest jak'],
            'description': 'Absurdalne przeniesienie'
        },
        'aggressive_tone': {
            'markers': ['!', 'kurczę', 'cholera', 'no nie', 'serio'],
            'description': 'Agresywny ton'
        },
        'rhetorical_question': {
            'markers': ['?', 'czy', 'co ja', 'co ty', 'jak to'],
            'description': 'Pytanie retoryczne'
        },
        'meta_commentary': {
            'markers': ['czyli', 'innymi słowy', 'to znaczy', 'wiem że'],
            'description': 'Meta-komentarz'
        },
    }
    
    def analyze(self, joke_text: str, context: Optional[Dict] = None) -> Dict:
        """
        Analiza reverse engineering
        
        Wykrywa:
        - Jakie mechanizmy są użyte?
        - Czy można wyodrębnić wzorzec?
        - Czy żart jest "replicable"?
        """
        text_lower = joke_text.lower()
        
        score = 0.0
        key_elements = []
        detected_mechanisms = []
        
        # Detect mechanisms
        for mechanism_name, mechanism_data in self.MECHANISMS.items():
            markers = mechanism_data['markers']
            description = mechanism_data['description']
            
            count = sum(
                1 for marker in markers 
                if marker in text_lower
            )
            
            if count > 0:
                score += count * 1.5
                detected_mechanisms.append(mechanism_name)
                key_elements.append(description)
        
        # Bonus: multiple mechanisms (complex pattern)
        if len(detected_mechanisms) >= 3:
            score += 2.0
            key_elements.append("Złożony wzorzec (3+ mechanizmy)")
        
        # Bonus: replicable (can be used as template)
        if self._is_replicable(text_lower, detected_mechanisms):
            score += 1.5
            key_elements.append("Replikowalny wzorzec")
        
        # Penalty: no clear mechanism
        if len(detected_mechanisms) == 0:
            score = 2.0
            key_elements.append("Brak wyraźnego mechanizmu")
        
        # Cap at 10
        score = min(10, score)
        
        explanation = self._generate_explanation(
            detected_mechanisms, len(detected_mechanisms)
        )
        
        return {
            'score': round(score, 1),
            'explanation': explanation,
            'key_elements': key_elements
        }
    
    def _is_replicable(self, text: str, mechanisms: List[str]) -> bool:
        """
        Czy wzorzec jest replikowalny?
        (czy można go użyć jako template dla innych żartów?)
        """
        # Replicable if has clear structure and at least 2 mechanisms
        if len(mechanisms) < 2:
            return False
        
        # Check for template markers (variables)
        template_markers = ['{', '[', '<VARIABLE>', '<X>', '<Y>']
        has_template = any(marker in text for marker in template_markers)
        
        # Or if has common patterns
        common_patterns = [
            ('anthropomorphization' in mechanisms and 'everyday_frustration' in mechanisms),
            ('absurd_transfer' in mechanisms and 'aggressive_tone' in mechanisms),
            ('rhetorical_question' in mechanisms and 'meta_commentary' in mechanisms),
        ]
        
        return has_template or any(common_patterns)
    
    def _generate_explanation(
        self,
        detected_mechanisms: List[str],
        mechanism_count: int
    ) -> str:
        """Generate explanation"""
        if mechanism_count == 0:
            return "Brak wyraźnego mechanizmu. Żart trudny do zreplikowania."
        elif mechanism_count == 1:
            return f"Jeden mechanizm: {detected_mechanisms[0]}."
        elif mechanism_count == 2:
            return f"Dwa mechanizmy: {', '.join(detected_mechanisms)}. Dobry punkt wyjścia."
        else:
            top_3 = ', '.join(detected_mechanisms[:3])
            return f"Złożony wzorzec ({mechanism_count} mechanizmów): {top_3}. Łatwo replikowalny."

