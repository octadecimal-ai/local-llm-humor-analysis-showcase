"""
🔍 8. Analiza mikro-komponentów humoru (tzw. atomy humorystyczne)

Można rozłożyć tekst na mikro-elementy:
- hiperbola
- kontrast
- anty-klimaks
- atak personalny
- metafora gwałtownie zmieniona w literalność
- samobójczy żart
- absurd syntaktyczny
- zmiana rejestru (np. z oficjalnego na uliczny)

Każdy żart jest miksem tych atomów.
"""
from typing import Dict, Optional, List
from .base import BaseAnalyzer


class HumorAtomsAnalyzer(BaseAnalyzer):
    """Analiza atomów humorystycznych (mikro-komponenty)"""
    
    # Humor atoms and their markers
    HUMOR_ATOMS = {
        'hyperbole': {
            'markers': ['nigdy', 'zawsze', 'wszystko', 'nic', 'wieczność', 'milion', 'nieskończenie'],
            'weight': 1.0
        },
        'contrast': {
            'markers': ['ale', 'jednak', 'z drugiej strony', 'natomiast', 'przeciwnie'],
            'weight': 1.5
        },
        'anticlimax': {
            'markers': ['okazuje się', 'w rzeczywistości', 'niestety', 'niespodziewanie'],
            'weight': 1.5
        },
        'self_deprecation': {
            'markers': ['głupi', 'idiota', 'debil', 'nieudacznik', 'fail', 'porażka'],
            'weight': 1.2
        },
        'sarcasm': {
            'markers': ['oczywiście', 'naturalnie', 'jak zwykle', 'pewnie', 'tradycyjnie'],
            'weight': 1.8
        },
        'absurd_syntax': {
            'markers': ['???', '!?', '...?!', '!!!'],
            'weight': 1.0
        },
        'register_shift': {
            'markers': ['kurczę', 'cholera', 'ziomek', 'stary', 'koles'],
            'weight': 1.5
        },
    }
    
    def analyze(self, joke_text: str, context: Optional[Dict] = None) -> Dict:
        """
        Analiza atomów humorystycznych
        
        Wykrywa:
        - Jakie atomy są użyte?
        - Ile ich jest?
        - Czy są zbalansowane?
        """
        text_lower = joke_text.lower()
        
        score = 0.0
        key_elements = []
        detected_atoms = []
        
        # Detect each humor atom
        for atom_name, atom_data in self.HUMOR_ATOMS.items():
            markers = atom_data['markers']
            weight = atom_data['weight']
            
            count = sum(
                1 for marker in markers 
                if marker in text_lower
            )
            
            if count > 0:
                score += count * weight
                detected_atoms.append(atom_name)
                key_elements.append(f"{atom_name}: {count}x")
        
        # Bonus: multiple atoms (mix)
        if len(detected_atoms) >= 3:
            score += 1.5
            key_elements.append("Mix wielu atomów")
        
        # Penalty: no atoms detected
        if len(detected_atoms) == 0:
            score = 1.0
            key_elements.append("Brak wykrytych atomów")
        
        # Cap at 10
        score = min(10, score)
        
        explanation = self._generate_explanation(
            detected_atoms, len(detected_atoms)
        )
        
        return {
            'score': round(score, 1),
            'explanation': explanation,
            'key_elements': key_elements
        }
    
    def _generate_explanation(
        self,
        detected_atoms: List[str],
        atom_count: int
    ) -> str:
        """Generate explanation"""
        if atom_count == 0:
            return "Brak wykrytych atomów humorystycznych."
        elif atom_count == 1:
            return f"Jeden atom: {detected_atoms[0]}."
        elif atom_count == 2:
            return f"Dwa atomy: {', '.join(detected_atoms)}."
        else:
            return f"Mix {atom_count} atomów: {', '.join(detected_atoms[:3])}..."

