"""
HumorFeatureExtractor - ekstrahuje features z żartów bez scoring logic
"""
import time
import spacy
from typing import Dict, List, Optional
from .feature_models import (
    ExtractRequest,
    ExtractResponse,
    HumorFeatures,
    StructuralFeatures,
    KeywordFeatures,
    LinguisticFeatures,
    AtomicFeatures,
    SemanticFeatures,
    TimingFeatures,
    NarrativeFeatures,
    AbsurdityFeatures,
)


class HumorFeatureExtractor:
    """
    Ekstraktor features z żartów używający NLP (spaCy)
    Zwraca tylko raw features, scoring jest w PHP (Laravel)
    """
    
    def __init__(self, model_name: str = "pl_core_news_lg"):
        """
        Initialize extractor z polskim modelem spaCy
        
        Args:
            model_name: Nazwa modelu spaCy (default: pl_core_news_lg)
        """
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            raise RuntimeError(
                f"Model spaCy '{model_name}' nie jest zainstalowany. "
                f"Zainstaluj: python -m spacy download {model_name}"
            )
        
        # Słowniki dla keyword detection
        self._load_dictionaries()
    
    def _load_dictionaries(self):
        """Załaduj słowniki dla keyword detection"""
        self.tech_words = {
            'api', 'bug', 'git', 'commit', 'merge', 'deploy', 'server',
            'frontend', 'backend', 'fullstack', 'database', 'sql', 'orm',
            'framework', 'library', 'package', 'npm', 'composer', 'pip',
            'docker', 'kubernetes', 'ci/cd', 'devops', 'agile', 'scrum',
        }
        
        self.emotion_words = {
            'radość', 'smutek', 'złość', 'strach', 'zaskoczenie', 'wstyd',
            'szczęście', 'frustracja', 'ekscytacja', 'nuda', 'ciekawość',
        }
        
        self.regional_markers = {
            'janusz', 'grażyna', 'seba', 'karyna', 'brajanek', 'dżesika',
            'polska', 'polski', 'polak', 'warsaw', 'warsaw', 'kraków',
        }
        
        self.archetypes = {
            'bohater', 'antybohater', 'mentor', 'błazen', 'męczennik',
            'buntownik', 'nieudacznik', 'geniusz', 'outsider', 'celebryta',
        }
        
        self.taboo_markers = {
            'śmierć', 'seks', 'polityka', 'religia', 'drugs', 'alkohol',
            'choroba', 'przemoc', 'dyskryminacja',
        }
        
        self.surprise_words = {
            'nagle', 'niespodziewanie', 'okazuje się', 'ale', 'jednak',
            'przecież', 'wcale', 'wcale nie', 'w sumie', 'właściwie',
        }
        
        self.exaggeration_words = {
            'nigdy', 'zawsze', 'wszyscy', 'nikt', 'wszystko', 'nic',
            'kompletnie', 'totalnie', 'absolutnie', 'mega', 'ultra',
        }
        
        self.impossibility_markers = {
            'niemożliwe', 'absurdalne', 'nierealne', 'fantastyczne',
            'magiczne', 'cudowne', 'niewiarygodne',
        }
    
    async def extract(self, request: ExtractRequest) -> ExtractResponse:
        """
        Ekstrahuj features z żartu
        
        Args:
            request: ExtractRequest z tekstem żartu
            
        Returns:
            ExtractResponse z wyekstraktowanymi features
        """
        start_time = time.time()
        
        joke_text = request.joke_text
        doc = self.nlp(joke_text)
        
        # Ekstraktuj features z każdej kategorii
        structural = self._extract_structural(doc, joke_text)
        keywords = self._extract_keywords(doc, joke_text)
        linguistic = self._extract_linguistic(doc)
        atomic = self._extract_atomic(joke_text)
        semantic = self._extract_semantic(doc)
        timing = self._extract_timing(doc, joke_text)
        narrative = self._extract_narrative(doc)
        absurdity = self._extract_absurdity(doc, joke_text)
        
        # Złóż wszystko w HumorFeatures
        features = HumorFeatures(
            joke_text=joke_text,
            structural=structural,
            keywords=keywords,
            linguistic=linguistic,
            atomic=atomic,
            semantic=semantic,
            timing=timing,
            narrative=narrative,
            absurdity=absurdity,
            language="pl",
            char_count=len(joke_text),
            word_count=len([t for t in doc if not t.is_space]),
        )
        
        end_time = time.time()
        extraction_time_ms = (end_time - start_time) * 1000
        
        return ExtractResponse(
            features=features,
            extraction_time_ms=round(extraction_time_ms, 2)
        )
    
    def _extract_structural(self, doc, text: str) -> StructuralFeatures:
        """Ekstraktuj cechy strukturalne (setup-punchline)"""
        sentences = list(doc.sents)
        sentence_count = len(sentences)
        sentence_lengths = [len(sent) for sent in sentences]
        avg_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
        
        # Variance for rhythm detection
        variance = 0.0
        if len(sentence_lengths) > 1:
            variance = sum((l - avg_length) ** 2 for l in sentence_lengths) / len(sentence_lengths)
        
        # Check for question
        has_question = '?' in text
        
        # Simple punchline detection: ostatnie zdanie
        has_clear_punchline = sentence_count >= 2
        setup_length = sum(sentence_lengths[:-1]) if sentence_count > 1 else 0
        punchline_length = sentence_lengths[-1] if sentence_lengths else 0
        
        return StructuralFeatures(
            sentence_count=sentence_count,
            has_question=has_question,
            sentence_lengths=sentence_lengths,
            avg_sentence_length=round(avg_length, 1),
            length_variance=round(variance, 1),
            has_clear_punchline=has_clear_punchline,
            setup_length=setup_length,
            punchline_length=punchline_length,
        )
    
    def _extract_keywords(self, doc, text: str) -> KeywordFeatures:
        """Ekstraktuj słowa kluczowe i markery"""
        text_lower = text.lower()
        words_lower = [t.text.lower() for t in doc if not t.is_space and not t.is_punct]
        
        tech = [w for w in words_lower if w in self.tech_words]
        emotion = [w for w in words_lower if w in self.emotion_words]
        regional = [w for w in words_lower if w in self.regional_markers]
        archetypes_found = [w for w in words_lower if w in self.archetypes]
        taboo = [w for w in words_lower if w in self.taboo_markers]
        surprise = [w for w in words_lower if w in self.surprise_words]
        
        return KeywordFeatures(
            tech_words=tech,
            emotion_words=emotion,
            regional_markers=regional,
            archetypes=archetypes_found,
            taboo_markers=taboo,
            surprise_words=surprise,
        )
    
    def _extract_linguistic(self, doc) -> LinguisticFeatures:
        """Ekstraktuj cechy lingwistyczne (POS tags, entities)"""
        # POS tags count
        pos_tags = {}
        for token in doc:
            if not token.is_space and not token.is_punct:
                pos = token.pos_
                pos_tags[pos] = pos_tags.get(pos, 0) + 1
        
        # Named entities
        entities = [
            {'text': ent.text, 'label': ent.label_}
            for ent in doc.ents
        ]
        
        # Comparisons (szukaj 'niż', 'jak', 'bardziej')
        comparisons = sum(1 for t in doc if t.text.lower() in ['niż', 'jak', 'bardziej', 'mniej'])
        
        # Negations
        negations = sum(1 for t in doc if t.text.lower() in ['nie', 'nigdy', 'wcale', 'żaden'])
        
        # Questions and exclamations
        questions = sum(1 for t in doc if t.text == '?')
        exclamations = sum(1 for t in doc if t.text == '!')
        
        return LinguisticFeatures(
            pos_tags=pos_tags,
            entities=entities,
            comparisons_count=comparisons,
            negations_count=negations,
            questions_count=questions,
            exclamations_count=exclamations,
        )
    
    def _extract_atomic(self, text: str) -> AtomicFeatures:
        """Ekstraktuj atomy humorystyczne"""
        emoji_count = sum(1 for c in text if ord(c) > 0x1F300)
        exclamation_count = text.count('!')
        caps_words = [w for w in text.split() if w.isupper() and len(w) > 1]
        
        # Repetitions (simple: znajdź słowa występujące >1 raz)
        words = text.lower().split()
        word_counts = {}
        for w in words:
            word_counts[w] = word_counts.get(w, 0) + 1
        repetitions = [w for w, count in word_counts.items() if count > 1]
        
        # Sound words (onomatopeje - prosty detection)
        sound_patterns = ['ha', 'he', 'hi', 'ho', 'chu', 'bum', 'pif', 'paf']
        sound_words = [w for w in words if any(p in w for p in sound_patterns)]
        
        # Hyperboles (z exaggeration_words)
        hyperboles = [w for w in words if w in self.exaggeration_words]
        
        return AtomicFeatures(
            emoji_count=emoji_count,
            exclamation_count=exclamation_count,
            caps_words_count=len(caps_words),
            repetitions=repetitions[:5],  # Limit do 5
            sound_words=sound_words,
            hyperboles=hyperboles,
        )
    
    def _extract_semantic(self, doc) -> SemanticFeatures:
        """Ekstraktuj cechy semantyczne"""
        # Polysemy: słowa z wieloma znaczeniami (simplified - check word length and frequency)
        polysemy_candidates = [
            t.text.lower() for t in doc 
            if not t.is_stop and not t.is_punct and len(t.text) <= 5
        ]
        
        # Metaphors: szukaj porównań i przenośni (simple heuristic)
        metaphors = [
            t.text for t in doc 
            if t.dep_ in ['nmod', 'amod'] and t.text.lower() not in ['ten', 'ta', 'to']
        ]
        
        # Wordplay candidates: słowa podobnie brzmiące
        wordplay = []
        words = [t.text.lower() for t in doc if not t.is_space and not t.is_punct]
        for i, w1 in enumerate(words):
            for w2 in words[i+1:]:
                if len(w1) > 3 and len(w2) > 3 and w1[:3] == w2[:3] and w1 != w2:
                    wordplay.append(f"{w1}/{w2}")
        
        # Semantic fields (based on dominant POS and keywords)
        semantic_fields = []
        if any(t.pos_ == 'VERB' and 'comp' in t.text.lower() for t in doc):
            semantic_fields.append('technologia')
        if any(t.pos_ == 'ADJ' and t.text.lower() in self.emotion_words for t in doc):
            semantic_fields.append('emocje')
        
        return SemanticFeatures(
            polysemy_words=list(set(polysemy_candidates))[:10],
            metaphors=list(set(metaphors))[:5],
            wordplay_candidates=wordplay[:5],
            semantic_fields=semantic_fields,
        )
    
    def _extract_timing(self, doc, text: str) -> TimingFeatures:
        """Ekstraktuj cechy temporalne"""
        words = [t for t in doc if not t.is_space and not t.is_punct]
        word_count = len(words)
        
        # Syllable count (approximate for Polish: avg 2.5 syllables per word)
        syllable_count = int(word_count * 2.5)
        
        # Reading time (avg 200 words/min)
        reading_time_sec = (word_count / 200) * 60
        
        # Rhythm score based on sentence length variance
        sentences = list(doc.sents)
        if len(sentences) > 1:
            lengths = [len(list(s)) for s in sentences]
            avg = sum(lengths) / len(lengths)
            variance = sum((l - avg) ** 2 for l in lengths) / len(lengths)
            rhythm_score = min(1.0, variance / 100)  # Normalize
        else:
            rhythm_score = 0.0
        
        # Pause indicators (punkty, przecinki, ...)
        pause_indicators = text.count(',') + text.count('.') + text.count(';') + text.count(':')
        
        return TimingFeatures(
            word_count=word_count,
            syllable_count=syllable_count,
            reading_time_sec=round(reading_time_sec, 1),
            rhythm_score=round(rhythm_score, 2),
            pause_indicators=pause_indicators,
        )
    
    def _extract_narrative(self, doc) -> NarrativeFeatures:
        """Ekstraktuj cechy narracyjne"""
        # Perspective (1st/3rd person based on pronouns)
        first_person = sum(1 for t in doc if t.text.lower() in ['ja', 'mnie', 'mój', 'moja'])
        third_person = sum(1 for t in doc if t.text.lower() in ['on', 'ona', 'jego', 'jej'])
        
        if first_person > third_person:
            perspective = '1st person'
        elif third_person > first_person:
            perspective = '3rd person'
        else:
            perspective = 'neutral'
        
        # Emotional arc (based on sentiment - simplified)
        positive_words = sum(1 for t in doc if t.text.lower() in ['dobrze', 'super', 'świetnie', 'wspaniale'])
        negative_words = sum(1 for t in doc if t.text.lower() in ['źle', 'słabo', 'kiepsko', 'fatalnie'])
        
        if positive_words > negative_words:
            emotional_arc = 'positive'
        elif negative_words > positive_words:
            emotional_arc = 'negative'
        else:
            emotional_arc = 'neutral'
        
        # Conflict (szukaj 'ale', 'jednak', 'niestety')
        conflict_present = any(t.text.lower() in ['ale', 'jednak', 'niestety', 'problem'] for t in doc)
        
        # Resolution (szukaj 'więc', 'dlatego', 'w końcu')
        resolution_present = any(t.text.lower() in ['więc', 'dlatego', 'w końcu', 'okazało się'] for t in doc)
        
        # Character count (based on proper nouns and pronouns)
        characters = len([ent for ent in doc.ents if ent.label_ == 'PER'])
        characters += len(set([t.text.lower() for t in doc if t.pos_ == 'PRON']))
        
        return NarrativeFeatures(
            narrative_perspective=perspective,
            emotional_arc=emotional_arc,
            conflict_present=conflict_present,
            resolution_present=resolution_present,
            character_count=min(characters, 10),  # Cap at 10
        )
    
    def _extract_absurdity(self, doc, text: str) -> AbsurdityFeatures:
        """Ekstraktuj cechy absurdu"""
        text_lower = text.lower()
        words_lower = [t.text.lower() for t in doc if not t.is_space and not t.is_punct]
        
        # Contradictions (szukaj 'ale', 'jednak' + negations)
        contradictions = sum(
            1 for t in doc 
            if t.text.lower() in ['ale', 'jednak'] and 
            any(t2.text.lower() in ['nie', 'nigdy'] for t2 in doc[t.i:t.i+5])
        )
        
        # Impossibility markers
        impossibilities = [w for w in words_lower if w in self.impossibility_markers]
        
        # Exaggeration words
        exaggerations = [w for w in words_lower if w in self.exaggeration_words]
        
        # Logical breaks (heuristic: questions + negations + contradictions)
        logical_breaks = sum([
            text.count('?'),
            sum(1 for w in words_lower if w in ['nie', 'nigdy']),
            contradictions,
        ])
        
        return AbsurdityFeatures(
            contradiction_count=contradictions,
            impossibility_markers=impossibilities,
            exaggeration_words=exaggerations,
            logical_breaks=logical_breaks,
        )

