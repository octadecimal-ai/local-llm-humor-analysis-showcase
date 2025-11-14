"""
🎭 2. Teoria niespójności (incongruity)

Najważniejsza teoria humoru.

Analiza polega na:
- zidentyfikowaniu dwóch modeli rzeczywistości, które żart zderza
- opisaniu gdzie jest zgrzyt między nimi
- określeniu dlaczego mózg tego nie odrzuca jako błąd, tylko przekształca w humor

Przykłady niespójności:
- wysokie ↔ niskie (patos / przyziemność)
- ludzkie ↔ nieludzkie (np. Walduś: „byt cyfrowy z dramatem człowieka")
- logiczne ↔ chaotyczne
- powaga ↔ absurd
"""
from typing import Dict, List, Optional
from .base import BaseAnalyzer


class IncongruityAnalyzer(BaseAnalyzer):
    """Analiza teorii niespójności (incongruity)"""
    
    # Domain pairs (niespójności)
    INCONGRUITY_PAIRS = [
        # Wysokie ↔ Niskie
        (['filozofia', 'egzystencja', 'metafizyka', 'transcendencja', 'ontologia'],
         ['kebab', 'piwo', 'przeciek', 'kanał', 'kibel']),
        
        # Technologia ↔ Człowiek
        (['api', 'serwer', 'request', 'endpoint', 'database', 'ai', 'algorytm', 'kod'],
         ['miłość', 'smutek', 'śmierć', 'strach', 'tęsknota', 'samotność']),
        
        # Profesjonalne ↔ Codzienne
        (['synergize', 'leverage', 'optimize', 'innovate', 'disrupt', 'blockchain'],
         ['rano', 'kawa', 'autobus', 'kolejka', 'śniadanie']),
        
        # Cyfrowe ↔ Fizyczne
        (['cyfrowy', 'wirtualny', 'online', 'internet', 'cloud'],
         ['ciało', 'fizyczny', 'dotyk', 'zapach', 'głód']),
        
        # Nauka ↔ Absurd
        (['quantum', 'einstein', 'relatywność', 'teoria', 'badania'],
         ['losowo', 'przypadek', 'chaos', 'bez sensu']),
    ]
    
    # Contrast markers
    CONTRAST_MARKERS = [
        'ale', 'jednak', 'zamiast', 'niż', 'mimo', 'choć', 
        'podczas gdy', 'z drugiej strony', 'przeciwnie'
    ]
    
    # Anthropomorphization markers (tech → human)
    ANTHROPO_MARKERS = [
        'czuję', 'myślę', 'cierpię', 'umierać', 'żyć', 
        'tęsknię', 'kocham', 'nienawidzę', 'boję się'
    ]
    
    def analyze(self, joke_text: str, context: Optional[Dict] = None) -> Dict:
        """
        Analiza niespójności w żarcie
        
        Wykrywa:
        1. Jakie dwa modele rzeczywistości są zderzane?
        2. Gdzie jest zgrzyt?
        3. Dlaczego to humor, a nie błąd?
        """
        text_lower = joke_text.lower()
        
        score = 0.0
        key_elements = []
        detected_pairs = []
        
        # 1. Detect domain clashes
        for high_domain, low_domain in self.INCONGRUITY_PAIRS:
            high_count = sum(1 for word in high_domain if word in text_lower)
            low_count = sum(1 for word in low_domain if word in text_lower)
            
            if high_count > 0 and low_count > 0:
                score += 2.5
                detected_pairs.append(f"{high_domain[0]}↔{low_domain[0]}")
                key_elements.append(f"Clash: {high_domain[0]} + {low_domain[0]}")
        
        # 2. Detect contrast markers
        contrast_count = sum(
            1 for marker in self.CONTRAST_MARKERS 
            if f' {marker} ' in f' {text_lower} '
        )
        if contrast_count > 0:
            score += 1.5
            key_elements.append(f"{contrast_count} marker kontrastu")
        
        # 3. Anthropomorphization (tech → human emotions)
        anthropo_count = sum(
            1 for marker in self.ANTHROPO_MARKERS 
            if marker in text_lower
        )
        if anthropo_count > 0:
            score += 2.0
            key_elements.append("Antropomorfizacja")
        
        # 4. Semantic distance (words that don't belong together)
        semantic_clash = self._detect_semantic_clash(text_lower)
        if semantic_clash:
            score += 1.5
            key_elements.append("Zderzenie semantyczne")
        
        # 5. Waldus-style: tech + existential crisis
        if self._is_waldus_style(text_lower):
            score += 1.5
            key_elements.append("Styl Waldus (tech + egzystencja)")
        
        # Cap at 10
        score = min(10, score)
        
        explanation = self._generate_explanation(
            detected_pairs, contrast_count, anthropo_count
        )
        
        return {
            'score': round(score, 1),
            'explanation': explanation,
            'key_elements': key_elements
        }
    
    def _detect_semantic_clash(self, text: str) -> bool:
        """
        Wykryj słowa, które nie powinny być razem
        (wysoka entropia semantyczna)
        """
        # Pairs that clash semantically
        clash_pairs = [
            ('api', 'śmierć'),
            ('request', 'płacz'),
            ('server', 'samotność'),
            ('kod', 'miłość'),
            ('algorytm', 'smutek'),
            ('database', 'rozpacz'),
            ('endpoint', 'egzystencja'),
            ('quantum', 'kebab'),
        ]
        
        for word1, word2 in clash_pairs:
            if word1 in text and word2 in text:
                return True
        
        return False
    
    def _is_waldus_style(self, text: str) -> bool:
        """
        Wykryj styl Waldusia: tech + human suffering
        """
        tech_words = ['api', 'request', 'server', 'internet', 'kod', 'cyfrowy']
        suffer_words = ['śmierć', 'umierać', 'cierpię', 'samotność', 'rozpacz']
        
        has_tech = any(word in text for word in tech_words)
        has_suffer = any(word in text for word in suffer_words)
        
        return has_tech and has_suffer
    
    def _generate_explanation(
        self,
        detected_pairs: List[str],
        contrast_count: int,
        anthropo_count: int
    ) -> str:
        """Generate explanation"""
        parts = []
        
        if detected_pairs:
            parts.append(f"Wykryto {len(detected_pairs)} zderzenie domen: {', '.join(detected_pairs)}.")
        
        if contrast_count > 0:
            parts.append(f"Użyto {contrast_count} markerów kontrastu.")
        
        if anthropo_count > 0:
            parts.append("Antropomorfizacja (tech → emocje).")
        
        if not parts:
            parts.append("Brak wyraźnych niespójności. Może być za spójny.")
        
        return " ".join(parts)

