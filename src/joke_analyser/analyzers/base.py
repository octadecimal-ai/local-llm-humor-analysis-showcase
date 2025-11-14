"""
BaseAnalyzer - klasa bazowa dla wszystkich analizerów
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import spacy


class BaseAnalyzer(ABC):
    """Klasa bazowa dla analizerów teorii humoru"""
    
    def __init__(self):
        """Initialize analyzer"""
        self.nlp = None
        self._load_models()
    
    def _load_models(self):
        """Load NLP models (lazy loading)"""
        try:
            self.nlp = spacy.load("pl_core_news_lg")
        except OSError:
            # Fallback to smaller model
            try:
                self.nlp = spacy.load("pl_core_news_sm")
            except OSError:
                print("Warning: spaCy Polish model not found. Install with: python -m spacy download pl_core_news_lg")
                self.nlp = None
    
    @abstractmethod
    def analyze(self, joke_text: str, context: Optional[Dict] = None) -> Dict:
        """
        Analizuj żart według danej teorii
        
        Returns:
            {
                'score': float,  # 0-10
                'explanation': str,
                'key_elements': List[str]
            }
        """
        pass
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenizuj tekst"""
        if self.nlp:
            doc = self.nlp(text)
            return [token.text for token in doc]
        return text.split()
    
    def _get_sentences(self, text: str) -> List[str]:
        """Podziel na zdania"""
        if self.nlp:
            doc = self.nlp(text)
            return [sent.text.strip() for sent in doc.sents]
        # Fallback: split on . ! ?
        import re
        return [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    
    def _get_pos_tags(self, text: str) -> List[tuple]:
        """Get POS tags"""
        if self.nlp:
            doc = self.nlp(text)
            return [(token.text, token.pos_) for token in doc]
        return []
    
    def _calculate_text_length(self, text: str) -> int:
        """Oblicz długość tekstu (znaki)"""
        return len(text)
    
    def _calculate_sentence_count(self, text: str) -> int:
        """Oblicz liczbę zdań"""
        return len(self._get_sentences(text))
    
    def _calculate_word_count(self, text: str) -> int:
        """Oblicz liczbę słów"""
        return len(self._tokenize(text))

