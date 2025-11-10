#!/usr/bin/env python3
"""
Testy jednostkowe dla OllamaClient
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Dodaj ścieżkę do src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from ollama.client import OllamaClient
from ollama.exceptions import OllamaError, OllamaConnectionError


class TestOllamaClient:
    """Testy dla klasy OllamaClient"""
    
    def test_init_default(self):
        """Test inicjalizacji z domyślnymi wartościami"""
        client = OllamaClient()
        assert client.base_url == 'http://localhost:11434'
        assert client.default_model == 'llama3.1:8b'
        assert client.timeout == 120
        assert client.max_retries == 3
    
    def test_init_custom(self):
        """Test inicjalizacji z niestandardowymi wartościami"""
        client = OllamaClient(
            base_url='http://example.com:8080',
            default_model='test-model',
            timeout=60,
            max_retries=5
        )
        assert client.base_url == 'http://example.com:8080'
        assert client.default_model == 'test-model'
        assert client.timeout == 60
        assert client.max_retries == 5
    
    def test_init_env_vars(self, monkeypatch):
        """Test inicjalizacji z zmiennymi środowiskowymi"""
        monkeypatch.setenv('OLLAMA_URL', 'http://env-test:11434')
        monkeypatch.setenv('OLLAMA_MODEL', 'env-model')
        
        client = OllamaClient()
        assert client.base_url == 'http://env-test:11434'
        assert client.default_model == 'env-model'
    
    def test_init_base_url_trailing_slash(self):
        """Test że base_url nie kończy się na /"""
        client = OllamaClient(base_url='http://example.com/')
        assert client.base_url == 'http://example.com'
    
    @patch('ollama.client.requests.post')
    def test_chat_success(self, mock_post):
        """Test udanego chat completion"""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'message': {'content': 'Hello! How can I help you?'},
            'prompt_eval_count': 10,
            'eval_count': 5
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        client = OllamaClient()
        result = client.chat(user="Hello")
        
        assert result['text'] == 'Hello! How can I help you?'
        assert result['usage']['input_tokens'] == 10
        assert result['usage']['output_tokens'] == 5
        assert 'raw' in result
        
        # Sprawdź że request został wykonany
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert '/api/chat' in call_args[0][0]
        assert call_args[1]['json']['messages'][0]['role'] == 'user'
        assert call_args[1]['json']['messages'][0]['content'] == 'Hello'
    
    @patch('ollama.client.requests.post')
    def test_chat_with_system(self, mock_post):
        """Test chat z system prompt"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'message': {'content': 'Response'},
            'prompt_eval_count': 15,
            'eval_count': 8
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        client = OllamaClient()
        result = client.chat(
            user="Hello",
            system="You are helpful",
            temperature=0.7,
            max_tokens=100
        )
        
        assert result['text'] == 'Response'
        
        # Sprawdź że system message został dodany
        call_args = mock_post.call_args
        messages = call_args[1]['json']['messages']
        assert len(messages) == 2
        assert messages[0]['role'] == 'system'
        assert messages[0]['content'] == 'You are helpful'
        assert messages[1]['role'] == 'user'
        
        # Sprawdź opcje
        assert call_args[1]['json']['options']['temperature'] == 0.7
        assert call_args[1]['json']['options']['num_predict'] == 100
    
    def test_chat_empty_user(self):
        """Test chat z pustym user message"""
        client = OllamaClient()
        with pytest.raises(ValueError, match='nie może być pusta'):
            client.chat(user="")
    
    def test_chat_empty_user_whitespace(self):
        """Test chat z user message zawierającym tylko białe znaki"""
        client = OllamaClient()
        with pytest.raises(ValueError, match='nie może być pusta'):
            client.chat(user="   ")
    
    @patch('ollama.client.requests.post')
    def test_generate_success(self, mock_post):
        """Test udanego generate"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'response': 'Generated text',
            'prompt_eval_count': 5,
            'eval_count': 10
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        client = OllamaClient()
        result = client.generate(prompt="Write a poem")
        
        assert result['text'] == 'Generated text'
        assert result['usage']['input_tokens'] == 5
        assert result['usage']['output_tokens'] == 10
        
        # Sprawdź że request został wykonany
        call_args = mock_post.call_args
        assert '/api/generate' in call_args[0][0]
        assert call_args[1]['json']['prompt'] == 'Write a poem'
    
    @patch('ollama.client.requests.get')
    def test_list_models_success(self, mock_get):
        """Test listowania modeli"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'models': [
                {'name': 'llama3.1:8b', 'size': 1000000},
                {'name': 'phi3:medium', 'size': 500000}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        client = OllamaClient()
        models = client.list_models()
        
        assert len(models) == 2
        assert models[0]['name'] == 'llama3.1:8b'
        assert models[1]['name'] == 'phi3:medium'
        
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert '/api/tags' in call_args[0][0]
    
    @patch('ollama.client.requests.post')
    def test_pull_model(self, mock_post):
        """Test pobierania modelu"""
        mock_response = Mock()
        mock_response.json.return_value = {'status': 'success'}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        client = OllamaClient()
        original_timeout = client.timeout
        
        result = client.pull_model('test-model')
        
        assert result['status'] == 'success'
        
        # Sprawdź że timeout został przywrócony po zakończeniu
        assert client.timeout == original_timeout
        
        # Sprawdź że request został wykonany
        call_args = mock_post.call_args
        assert '/api/pull' in call_args[0][0]
        assert call_args[1]['json']['name'] == 'test-model'
    
    @patch('ollama.client.requests.get')
    def test_check_health_success(self, mock_get):
        """Test sprawdzania dostępności serwera - sukces"""
        mock_response = Mock()
        mock_response.json.return_value = {'models': []}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        client = OllamaClient()
        assert client.check_health() is True
    
    @patch('ollama.client.requests.get')
    def test_check_health_failure(self, mock_get):
        """Test sprawdzania dostępności serwera - błąd"""
        from requests.exceptions import RequestException
        mock_get.side_effect = RequestException("Connection error")
        
        client = OllamaClient()
        assert client.check_health() is False
    
    @patch('ollama.client.requests.post')
    def test_retry_logic(self, mock_post):
        """Test retry logic przy błędzie"""
        from requests.exceptions import RequestException
        
        # Pierwsze 2 próby kończą się błędem, trzecia sukcesem
        mock_response = Mock()
        mock_response.json.return_value = {
            'message': {'content': 'Success'},
            'prompt_eval_count': 0,
            'eval_count': 0
        }
        mock_response.raise_for_status = Mock()
        
        mock_post.side_effect = [
            RequestException("Error 1"),
            RequestException("Error 2"),
            mock_response
        ]
        
        client = OllamaClient(max_retries=3)
        result = client.chat(user="Test")
        
        assert result['text'] == 'Success'
        assert mock_post.call_count == 3
    
    @patch('ollama.client.requests.post')
    def test_retry_exhausted(self, mock_post):
        """Test gdy wszystkie próby się nie powiodły"""
        from requests.exceptions import RequestException
        mock_post.side_effect = RequestException("Connection error")
        
        client = OllamaClient(max_retries=2)
        
        with pytest.raises(RequestException, match='Connection error'):
            client.chat(user="Test")
        
        assert mock_post.call_count == 2

