"""
🗿 7. Archetypowość (który „duch humoru" działa?)

Analizujesz, z którego archetypu pochodzi żart:
- Trickster
- Cynik
- Błazen
- Filozof
- Ofiara losu
- Nihilista (Walduś 😄)

Każdy archetyp generuje inny typ twistów.
Rozbiórka polega na odkryciu:
- do którego archetypu żart należy
- czy punchline jest zgodny z tym archetypem, czy go łamie
"""
from typing import Dict, Optional, List
from .base import BaseAnalyzer


class ArchetypeAnalyzer(BaseAnalyzer):
    """Analiza archetypów humoru"""
    
    # Archetypes and their markers
    ARCHETYPES = {
        'trickster': {
            'markers': ['oszukać', 'nabrać', 'podpuścić', 'wykiwać', 'sprytnie'],
            'score_base': 7.0,
            'description': 'Podstępny żartowniś'
        },
        'cynic': {
            'markers': ['oczywiście', 'naturalnie', 'jak zwykle', 'tradycyjnie', 'pewnie'],
            'score_base': 8.0,
            'description': 'Sarkastyczny cynik'
        },
        'jester': {
            'markers': ['hehehe', 'haha', 'hehe', 'ups', 'ojej', 'ale numer'],
            'score_base': 6.0,
            'description': 'Wesołek/błazen'
        },
        'philosopher': {
            'markers': ['właściwie', 'w istocie', 'de facto', 'ontologicznie', 'metafizycznie'],
            'score_base': 7.5,
            'description': 'Filozofujący mędrzec'
        },
        'victim': {
            'markers': ['znowu', 'zawsze ja', 'dlaczego ja', 'moje życie', 'pech'],
            'score_base': 7.0,
            'description': 'Ofiara losu'
        },
        'nihilist': {
            'markers': ['bez sensu', 'nicość', 'pustka', 'wszystko jedno', 'co za różnica'],
            'score_base': 9.0,
            'description': 'Nihilista (Walduś style)'
        },
        'rebel': {
            'markers': ['nie będę', 'odmawiam', 'nie chce mi się', 'mam to gdzieś'],
            'score_base': 7.5,
            'description': 'Buntownik'
        },
    }
    
    # Polish archetypes (cultural)
    POLISH_ARCHETYPES = {
        'wujek ze Śląska': ['wujek', 'śląsk', 'ślązak', 'hasiok', 'piwo'],
        'teściowa': ['teściowa', 'teść', 'żona matka'],
        'janusz': ['janusz', 'grażyna', 'działka', 'majsterkować'],
        'student': ['sesja', 'egzamin', 'zaliczenie', 'wykład', 'indeks'],
    }
    
    def analyze(self, joke_text: str, context: Optional[Dict] = None) -> Dict:
        """
        Analiza archetypów
        
        Wykrywa:
        - Jaki archetyp dominuje?
        - Czy jest spójny z twistem?
        """
        text_lower = joke_text.lower()
        
        score = 0.0
        key_elements = []
        detected_archetypes = []
        
        # 1. Detect universal archetypes
        for archetype_name, archetype_data in self.ARCHETYPES.items():
            markers = archetype_data['markers']
            if any(marker in text_lower for marker in markers):
                score += archetype_data['score_base'] * 0.5
                detected_archetypes.append(archetype_name)
                key_elements.append(f"Archetyp: {archetype_data['description']}")
        
        # 2. Detect Polish archetypes (bonus for cultural relatability)
        for polish_archetype, markers in self.POLISH_ARCHETYPES.items():
            if any(marker in text_lower for marker in markers):
                score += 2.5
                key_elements.append(f"Polski archetyp: {polish_archetype}")
        
        # 3. Waldus-specific: nihilist + tech
        if self._is_waldus_archetype(text_lower):
            score += 2.0
            key_elements.append("Archetyp Waldus (nihilist + tech)")
        
        # 4. Consistency check
        if len(detected_archetypes) == 1:
            score += 1.0
            key_elements.append("Spójny archetyp")
        elif len(detected_archetypes) > 2:
            score -= 0.5
            key_elements.append("Za dużo archetypów (niespójność)")
        
        # Cap at 10
        score = min(10, score)
        
        explanation = self._generate_explanation(
            detected_archetypes, key_elements
        )
        
        return {
            'score': round(score, 1),
            'explanation': explanation,
            'key_elements': key_elements
        }
    
    def _is_waldus_archetype(self, text: str) -> bool:
        """Wykryj archetyp Waldus: nihilist + tech"""
        nihilist_markers = ['nicość', 'pustka', 'bez sensu', 'wszystko jedno']
        tech_markers = ['api', 'request', 'server', 'kod', 'cyfrowy']
        
        has_nihilist = any(marker in text for marker in nihilist_markers)
        has_tech = any(marker in text for marker in tech_markers)
        
        return has_nihilist and has_tech
    
    def _generate_explanation(
        self,
        detected_archetypes: List[str],
        key_elements: List[str]
    ) -> str:
        """Generate explanation"""
        parts = []
        
        if not detected_archetypes:
            parts.append("Brak wyraźnego archetypu.")
        elif len(detected_archetypes) == 1:
            parts.append(f"Spójny archetyp: {detected_archetypes[0]}.")
        else:
            parts.append(f"Mix archetypów: {', '.join(detected_archetypes)}.")
        
        # Check for Polish archetypes
        polish_count = sum(1 for el in key_elements if 'Polski archetyp' in el)
        if polish_count > 0:
            parts.append(f"Użyto {polish_count} polskich archetypów (relatable).")
        
        return " ".join(parts)

