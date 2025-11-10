#!/usr/bin/env python3
"""
OllamaClient - Klasa do komunikacji z lokalnym serwerem Ollama
"""

import os
import json
import logging
import requests
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class OllamaClient:
    """
    Klient do komunikacji z lokalnym serwerem Ollama przez HTTP API
    
    Przykład użycia:
        client = OllamaClient()
        result = client.chat(user="Hello", system="You are helpful", temperature=0.7)
        print(result['text'])
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
        timeout: int = 120,
        max_retries: int = 3
    ):
        """
        Inicjalizacja klienta Ollama
        
        Args:
            base_url: URL serwera Ollama (domyślnie z OLLAMA_URL env lub http://localhost:11434)
            default_model: Domyślny model (domyślnie z OLLAMA_MODEL env lub llama3.1:8b)
            timeout: Timeout dla requestów w sekundach
            max_retries: Maksymalna liczba prób przy błędzie
        """
        self.base_url = base_url or os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.default_model = default_model or os.getenv('OLLAMA_MODEL', 'llama3.1:8b')
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Upewnij się, że base_url nie kończy się na /
        self.base_url = self.base_url.rstrip('/')
        
        logger.info(f"OllamaClient initialized: base_url={self.base_url}, default_model={self.default_model}")
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Wykonaj request do Ollama API z retry logic
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: Endpoint API (np. '/api/chat')
            data: Dane do wysłania (dla POST)
            params: Parametry URL (dla GET)
        
        Returns:
            Odpowiedź JSON z API
        
        Raises:
            requests.exceptions.RequestException: W przypadku błędu połączenia
        """
        url = urljoin(self.base_url, endpoint)
        
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug(f"Request attempt {attempt}/{self.max_retries}: {method} {url}")
                
                if method.upper() == 'GET':
                    response = requests.get(url, params=params, timeout=self.timeout)
                elif method.upper() == 'POST':
                    response = requests.post(url, json=data, timeout=self.timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries:
                    logger.error(f"Request failed after {self.max_retries} attempts: {e}")
                    raise
                logger.warning(f"Request attempt {attempt} failed: {e}, retrying...")
                continue
    
    def chat(
        self,
        user: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Wyślij wiadomość do Ollama i otrzymaj odpowiedź (chat completion)
        
        Args:
            user: Treść wiadomości użytkownika (wymagane)
            system: System prompt (opcjonalnie)
            model: Nazwa modelu (domyślnie self.default_model)
            temperature: Temperatura (0.0-2.0, opcjonalnie)
            max_tokens: Maksymalna liczba tokenów do wygenerowania (opcjonalnie)
            stream: Czy używać streaming (domyślnie False)
        
        Returns:
            {
                'text': str - tekst odpowiedzi,
                'usage': {'input_tokens': int, 'output_tokens': int},
                'raw': dict - pełna odpowiedź z API
            }
        
        Raises:
            ValueError: Jeśli user jest pusty
            requests.exceptions.RequestException: W przypadku błędu połączenia
        """
        if not user or not user.strip():
            raise ValueError('Treść wiadomości użytkownika nie może być pusta')
        
        model = model or self.default_model
        
        # Przygotuj messages
        messages = []
        if system:
            messages.append({'role': 'system', 'content': system})
        messages.append({'role': 'user', 'content': user})
        
        # Przygotuj request data
        request_data = {
            'model': model,
            'messages': messages,
            'stream': stream,
        }
        
        # Dodaj opcjonalne parametry
        options = {}
        if temperature is not None:
            options['temperature'] = temperature
        if max_tokens is not None:
            options['num_predict'] = max_tokens
        
        if options:
            request_data['options'] = options
        
        logger.info(f"Chat request: model={model}, user_length={len(user)}, system={bool(system)}")
        
        result = self._make_request('POST', '/api/chat', data=request_data)
        
        # Wyciągnij tekst odpowiedzi
        message = result.get('message', {})
        text = message.get('content', '')
        
        # Wyciągnij usage
        usage = {
            'input_tokens': result.get('prompt_eval_count', 0),
            'output_tokens': result.get('eval_count', 0),
        }
        
        logger.info(f"Chat response: {len(text)} chars, tokens: {usage}")
        
        return {
            'text': text,
            'usage': usage,
            'raw': result,
        }
    
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generuj tekst na podstawie promptu (generate endpoint)
        
        Args:
            prompt: Prompt do wygenerowania tekstu
            model: Nazwa modelu (domyślnie self.default_model)
            temperature: Temperatura (0.0-2.0, opcjonalnie)
            max_tokens: Maksymalna liczba tokenów (opcjonalnie)
        
        Returns:
            {
                'text': str - wygenerowany tekst,
                'usage': {'input_tokens': int, 'output_tokens': int},
                'raw': dict - pełna odpowiedź z API
            }
        """
        model = model or self.default_model
        
        request_data = {
            'model': model,
            'prompt': prompt,
            'stream': False,
        }
        
        # Dodaj opcjonalne parametry
        options = {}
        if temperature is not None:
            options['temperature'] = temperature
        if max_tokens is not None:
            options['num_predict'] = max_tokens
        
        if options:
            request_data['options'] = options
        
        logger.info(f"Generate request: model={model}, prompt_length={len(prompt)}")
        
        result = self._make_request('POST', '/api/generate', data=request_data)
        
        text = result.get('response', '')
        usage = {
            'input_tokens': result.get('prompt_eval_count', 0),
            'output_tokens': result.get('eval_count', 0),
        }
        
        logger.info(f"Generate response: {len(text)} chars, tokens: {usage}")
        
        return {
            'text': text,
            'usage': usage,
            'raw': result,
        }
    
    def list_models(self) -> List[Dict[str, Any]]:
        """
        Pobierz listę dostępnych modeli
        
        Returns:
            Lista modeli z informacjami (name, size, modified_at, etc.)
        """
        logger.info("Listing available models")
        result = self._make_request('GET', '/api/tags')
        models = result.get('models', [])
        logger.info(f"Found {len(models)} models")
        return models
    
    def pull_model(self, model_name: str) -> Dict[str, Any]:
        """
        Pobierz model z Ollama (jeśli nie jest dostępny lokalnie)
        
        Args:
            model_name: Nazwa modelu do pobrania (np. 'llama3.1:8b')
        
        Returns:
            Status pobierania modelu
        
        Note:
            To jest operacja długotrwała - może zająć kilka minut
        """
        logger.info(f"Pulling model: {model_name}")
        request_data = {'name': model_name}
        
        # Pull może być długotrwały, zwiększamy timeout
        original_timeout = self.timeout
        self.timeout = 600  # 10 minut
        
        try:
            result = self._make_request('POST', '/api/pull', data=request_data)
            logger.info(f"Model {model_name} pulled successfully")
            return result
        finally:
            self.timeout = original_timeout
    
    def check_health(self) -> bool:
        """
        Sprawdź czy serwer Ollama jest dostępny
        
        Returns:
            True jeśli serwer jest dostępny, False w przeciwnym razie
        """
        try:
            self._make_request('GET', '/api/tags')
            return True
        except requests.exceptions.RequestException:
            return False

