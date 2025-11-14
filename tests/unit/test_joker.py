#!/usr/bin/env python3
"""
Testy jednostkowe dla serwisu Joker
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Dodaj ścieżkę do src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from modules.joker.models import JokeRequest, JokeResponse
from modules.joker.service import JokerService


class TestJokeRequest:
    """Testy dla modelu JokeRequest"""
    
    def test_default_values(self):
        """Test domyślnych wartości"""
        request = JokeRequest()
        assert request.topic is None
        assert request.style == "sarcastic"
        assert request.length == "medium"
        assert request.temperature == 0.8
        assert request.max_tokens == 200
    
    def test_custom_values(self):
        """Test niestandardowych wartości"""
        request = JokeRequest(
            topic="programista",
            style="witty",
            length="short",
            temperature=0.9,
            max_tokens=150
        )
        assert request.topic == "programista"
        assert request.style == "witty"
        assert request.length == "short"
        assert request.temperature == 0.9
        assert request.max_tokens == 150
    
    def test_temperature_validation(self):
        """Test walidacji temperatury"""
        # Temperatura poniżej minimum
        with pytest.raises(Exception):
            JokeRequest(temperature=-0.1)
        
        # Temperatura powyżej maksimum
        with pytest.raises(Exception):
            JokeRequest(temperature=2.1)
    
    def test_max_tokens_validation(self):
        """Test walidacji max_tokens"""
        # Za mało tokenów
        with pytest.raises(Exception):
            JokeRequest(max_tokens=49)
        
        # Za dużo tokenów
        with pytest.raises(Exception):
            JokeRequest(max_tokens=501)


class TestJokeResponse:
    """Testy dla modelu JokeResponse"""
    
    def test_success_response(self):
        """Test odpowiedzi sukcesu"""
        response = JokeResponse(
            success=True,
            joke="Dlaczego programista nie lubi natury? Bo ma za dużo bugów.",
            topic="programista",
            style="sarcastic",
            generation_time=1.5,
            model="piotradamczyk/bielik-7b-v0.1"
        )
        assert response.success is True
        assert response.joke is not None
        assert response.topic == "programista"
        assert response.generation_time == 1.5
    
    def test_error_response(self):
        """Test odpowiedzi błędu"""
        response = JokeResponse(
            success=False,
            error="Model not loaded"
        )
        assert response.success is False
        assert response.error == "Model not loaded"
        assert response.joke is None


class TestJokerService:
    """Testy dla klasy JokerService"""
    
    @patch('modules.joker.service.AutoTokenizer')
    @patch('modules.joker.service.AutoModelForCausalLM')
    def test_init_with_transformers(self, mock_model, mock_tokenizer):
        """Test inicjalizacji z Transformers"""
        mock_tokenizer_instance = Mock()
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        
        mock_model_instance = Mock()
        mock_model_instance.to.return_value = mock_model_instance
        mock_model.from_pretrained.return_value = mock_model_instance
        
        with patch('modules.joker.service.torch') as mock_torch:
            mock_torch.cuda.is_available.return_value = False
            
            service = JokerService()
            
            assert service.tokenizer is not None
            assert service.model is not None
            mock_tokenizer.from_pretrained.assert_called_once()
            mock_model.from_pretrained.assert_called_once()
    
    def test_build_prompt_with_topic(self):
        """Test budowania promptu z tematem"""
        service = JokerService.__new__(JokerService)
        request = JokeRequest(topic="programista", style="sarcastic", length="medium")
        
        prompt = service._build_prompt(request)
        
        assert "Temat: programista" in prompt
        assert "Styl: sarcastic" in prompt
        assert "Długość: medium" in prompt
        assert "Wygeneruj żart:" in prompt
    
    def test_build_prompt_without_topic(self):
        """Test budowania promptu bez tematu"""
        service = JokerService.__new__(JokerService)
        request = JokeRequest(style="witty", length="short")
        
        prompt = service._build_prompt(request)
        
        assert "Temat:" not in prompt
        assert "Styl: witty" in prompt
        assert "Długość: short" in prompt
    
    @pytest.mark.asyncio
    @patch('modules.joker.service.AutoTokenizer')
    @patch('modules.joker.service.AutoModelForCausalLM')
    async def test_generate_success(self, mock_model, mock_tokenizer):
        """Test udanego generowania żartu"""
        # Mock tokenizer
        mock_tokenizer_instance = Mock()
        mock_tokenizer_instance.return_value = {"input_ids": Mock()}
        mock_tokenizer_instance.decode.return_value = "Wygenerowany żart"
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        
        # Mock model
        mock_model_instance = Mock()
        mock_output = Mock()
        mock_output.logits = Mock()
        mock_model_instance.generate.return_value = Mock()
        mock_model_instance.to.return_value = mock_model_instance
        mock_model.from_pretrained.return_value = mock_model_instance
        
        with patch('modules.joker.service.torch') as mock_torch:
            mock_torch.cuda.is_available.return_value = False
            
            service = JokerService()
            request = JokeRequest(topic="programista", style="sarcastic")
            
            response = await service.generate(request)
            
            assert response.success is True
            assert response.topic == "programista"
            assert response.style == "sarcastic"
            assert response.model is not None
    
    @pytest.mark.asyncio
    @patch('modules.joker.service.AutoTokenizer')
    @patch('modules.joker.service.AutoModelForCausalLM')
    async def test_generate_error(self, mock_model, mock_tokenizer):
        """Test generowania z błędem"""
        mock_tokenizer.from_pretrained.side_effect = Exception("Model not found")
        
        with patch('modules.joker.service.torch') as mock_torch:
            mock_torch.cuda.is_available.return_value = False
            
            with pytest.raises(Exception):
                service = JokerService()
                request = JokeRequest(topic="programista")
                await service.generate(request)

