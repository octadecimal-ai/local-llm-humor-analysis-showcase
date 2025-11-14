#!/usr/bin/env python3
"""
Testy jednostkowe dla serwisu Joke Analyser
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Dodaj ścieżkę do src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from modules.joke_analyser.models import (
    JokeAnalysisRequest,
    JokeAnalysisResponse,
    TechniqueScore
)
from modules.joke_analyser.service import JokeAnalyserService


class TestJokeAnalysisRequest:
    """Testy dla modelu JokeAnalysisRequest"""
    
    def test_required_joke(self):
        """Test że joke jest wymagane"""
        request = JokeAnalysisRequest(joke="Dlaczego programista nie lubi natury? Bo ma za dużo bugów.")
        assert request.joke == "Dlaczego programista nie lubi natury? Bo ma za dużo bugów."
        assert request.techniques is None
    
    def test_with_techniques(self):
        """Test z listą technik"""
        request = JokeAnalysisRequest(
            joke="Test żart",
            techniques=["incongruity", "setup_punchline"]
        )
        assert len(request.techniques) == 2
        assert "incongruity" in request.techniques
        assert "setup_punchline" in request.techniques


class TestTechniqueScore:
    """Testy dla modelu TechniqueScore"""
    
    def test_technique_score(self):
        """Test tworzenia TechniqueScore"""
        score = TechniqueScore(
            technique="incongruity",
            score=0.85,
            explanation="Analiza techniki incongruity dla żartu..."
        )
        assert score.technique == "incongruity"
        assert score.score == 0.85
        assert score.explanation is not None


class TestJokeAnalysisResponse:
    """Testy dla modelu JokeAnalysisResponse"""
    
    def test_success_response(self):
        """Test odpowiedzi sukcesu"""
        techniques = [
            TechniqueScore(technique="incongruity", score=0.8, explanation="Test")
        ]
        response = JokeAnalysisResponse(
            success=True,
            joke="Test żart",
            overall_score=0.8,
            techniques=techniques,
            sentiment="positive",
            keywords=["programista", "bug"],
            analysis_time=0.5
        )
        assert response.success is True
        assert response.overall_score == 0.8
        assert len(response.techniques) == 1
        assert response.sentiment == "positive"
        assert len(response.keywords) == 2
    
    def test_error_response(self):
        """Test odpowiedzi błędu"""
        response = JokeAnalysisResponse(
            success=False,
            joke="Test żart",
            error="Model not loaded"
        )
        assert response.success is False
        assert response.error == "Model not loaded"


class TestJokeAnalyserService:
    """Testy dla klasy JokeAnalyserService"""
    
    def test_available_techniques(self):
        """Test dostępnych technik"""
        service = JokeAnalyserService.__new__(JokeAnalyserService)
        assert len(service.AVAILABLE_TECHNIQUES) == 9
        assert "incongruity" in service.AVAILABLE_TECHNIQUES
        assert "setup_punchline" in service.AVAILABLE_TECHNIQUES
    
    @patch('modules.joke_analyser.service.spacy.load')
    @patch('modules.joke_analyser.service.AutoModel.from_pretrained')
    @patch('modules.joke_analyser.service.AutoTokenizer.from_pretrained')
    def test_init(self, mock_tokenizer, mock_model, mock_spacy):
        """Test inicjalizacji serwisu"""
        # Mock tokenizer
        mock_tokenizer_instance = Mock()
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        
        # Mock model
        mock_model_instance = Mock()
        mock_model_instance.to.return_value = mock_model_instance
        mock_model_instance.eval.return_value = None
        mock_model.from_pretrained.return_value = mock_model_instance
        
        # Mock spaCy
        mock_nlp = Mock()
        mock_spacy.return_value = mock_nlp
        
        with patch('modules.joke_analyser.service.torch') as mock_torch:
            mock_torch.cuda.is_available.return_value = False
            
            service = JokeAnalyserService()
            
            assert service.herbert_tokenizer is not None
            assert service.herbert_model is not None
            assert service.spacy_nlp is not None
    
    @pytest.mark.asyncio
    @patch('modules.joke_analyser.service.spacy.load')
    @patch('modules.joke_analyser.service.AutoModel.from_pretrained')
    @patch('modules.joke_analyser.service.AutoTokenizer.from_pretrained')
    async def test_analyze_success(self, mock_tokenizer, mock_model, mock_spacy):
        """Test udanej analizy żartu"""
        # Mock tokenizer
        mock_tokenizer_instance = Mock()
        mock_tokenizer_instance.return_value = {"input_ids": Mock()}
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        
        # Mock model
        mock_model_instance = Mock()
        mock_output = Mock()
        mock_output.last_hidden_state = Mock()
        mock_output.last_hidden_state.mean.return_value = Mock()
        mock_output.last_hidden_state.mean.return_value.mean.return_value = Mock()
        mock_output.last_hidden_state.mean.return_value.mean.return_value.item.return_value = 0.5
        mock_model_instance.return_value = mock_output
        mock_model_instance.to.return_value = mock_model_instance
        mock_model_instance.eval.return_value = None
        mock_model.from_pretrained.return_value = mock_model_instance
        
        # Mock spaCy
        mock_nlp = Mock()
        mock_doc = Mock()
        mock_token1 = Mock()
        mock_token1.lemma_ = "programista"
        mock_token1.pos_ = "NOUN"
        mock_token2 = Mock()
        mock_token2.lemma_ = "bug"
        mock_token2.pos_ = "NOUN"
        mock_doc.__iter__ = Mock(return_value=iter([mock_token1, mock_token2]))
        mock_nlp.return_value = mock_doc
        mock_spacy.return_value = mock_nlp
        
        with patch('modules.joke_analyser.service.torch') as mock_torch:
            mock_torch.cuda.is_available.return_value = False
            mock_torch.no_grad.return_value.__enter__ = Mock()
            mock_torch.no_grad.return_value.__exit__ = Mock(return_value=None)
            
            service = JokeAnalyserService()
            request = JokeAnalysisRequest(joke="Dlaczego programista nie lubi natury? Bo ma za dużo bugów.")
            
            response = await service.analyze(request)
            
            assert response.success is True
            assert response.joke == request.joke
            assert response.overall_score is not None
            assert response.techniques is not None
            assert response.sentiment is not None
            assert response.keywords is not None
    
    @pytest.mark.asyncio
    @patch('modules.joke_analyser.service.spacy.load')
    @patch('modules.joke_analyser.service.AutoModel.from_pretrained')
    @patch('modules.joke_analyser.service.AutoTokenizer.from_pretrained')
    async def test_extract_keywords(self, mock_tokenizer, mock_model, mock_spacy):
        """Test wyciągania słów kluczowych"""
        # Mock spaCy
        mock_nlp = Mock()
        mock_doc = Mock()
        mock_tokens = []
        for word, pos in [("programista", "NOUN"), ("lubi", "VERB"), ("bug", "NOUN")]:
            token = Mock()
            token.lemma_ = word
            token.pos_ = pos
            mock_tokens.append(token)
        mock_doc.__iter__ = Mock(return_value=iter(mock_tokens))
        mock_nlp.return_value = mock_doc
        mock_spacy.return_value = mock_nlp
        
        # Mock tokenizer i model (minimalne)
        mock_tokenizer.from_pretrained.return_value = Mock()
        mock_model_instance = Mock()
        mock_model_instance.to.return_value = mock_model_instance
        mock_model_instance.eval.return_value = None
        mock_model.from_pretrained.return_value = mock_model_instance
        
        with patch('modules.joke_analyser.service.torch') as mock_torch:
            mock_torch.cuda.is_available.return_value = False
            mock_torch.no_grad.return_value.__enter__ = Mock()
            mock_torch.no_grad.return_value.__exit__ = Mock(return_value=None)
            
            service = JokeAnalyserService()
            keywords = await service._extract_keywords("Test żart")
            
            assert len(keywords) > 0
            assert all(isinstance(kw, str) for kw in keywords)

