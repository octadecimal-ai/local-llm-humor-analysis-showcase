#!/usr/bin/env python3
"""
Ollama LLM Integration
Komunikacja z lokalnym serwerem Ollama przez HTTP API
"""

import sys
import json
import os
import logging
import requests
from typing import Optional, Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default Ollama configuration
DEFAULT_OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
DEFAULT_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')


def complete(prompt_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wywołaj Ollama API i zwróć odpowiedź
    
    Args:
        prompt_data: {
            'system': str (opcjonalnie),
            'user': str (wymagane),
            'temperature': float (opcjonalnie, domyślnie 0.7),
            'max_tokens': int (opcjonalnie, domyślnie 1000),
            'model': str (opcjonalnie, domyślnie z env)
        }
    
    Returns:
        {
            'text': str,
            'usage': {'input_tokens': int, 'output_tokens': int},
            'raw': dict
        }
    """
    try:
        ollama_url = os.getenv('OLLAMA_URL', DEFAULT_OLLAMA_URL)
        model = prompt_data.get('model', os.getenv('OLLAMA_MODEL', DEFAULT_MODEL))
        
        # Przygotuj prompt
        messages = []
        
        # Dodaj system message jeśli istnieje
        if prompt_data.get('system'):
            messages.append({
                'role': 'system',
                'content': prompt_data['system']
            })
        
        # Dodaj user message (wymagane)
        user_content = prompt_data.get('user', '')
        if not user_content:
            raise ValueError('Brak treści wiadomości użytkownika')
        
        messages.append({
            'role': 'user',
            'content': user_content
        })
        
        # Przygotuj request data
        request_data = {
            'model': model,
            'messages': messages,
            'stream': False,  # Chcemy pełną odpowiedź, nie stream
        }
        
        # Opcjonalne parametry
        if 'temperature' in prompt_data:
            request_data['options'] = {
                'temperature': prompt_data['temperature']
            }
        
        # Ollama nie ma bezpośredniego max_tokens, ale możemy użyć num_predict
        if 'max_tokens' in prompt_data:
            if 'options' not in request_data:
                request_data['options'] = {}
            request_data['options']['num_predict'] = prompt_data['max_tokens']
        
        # Wywołaj API
        url = f"{ollama_url}/api/chat"
        logger.info(f"Calling Ollama API: {url}, model: {model}")
        logger.debug(f"Request data: {json.dumps(request_data, indent=2)}")
        
        response = requests.post(url, json=request_data, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        
        # Wyciągnij tekst odpowiedzi
        message = result.get('message', {})
        text = message.get('content', '')
        
        # Wyciągnij usage (Ollama zwraca w `prompt_eval_count` i `eval_count`)
        usage = {
            'input_tokens': result.get('prompt_eval_count', 0),
            'output_tokens': result.get('eval_count', 0),
        }
        
        logger.info(f"Ollama response received: {len(text)} chars, tokens: {usage}")
        
        return {
            'text': text,
            'usage': usage,
            'raw': result,
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Ollama API request failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Error in Ollama complete: {e}")
        raise


def validate_prompt(prompt_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Waliduj prompt przed wysłaniem
    
    Args:
        prompt_data: Dane promptu do walidacji
    
    Returns:
        {'valid': bool, 'errors': list}
    """
    errors = []
    
    # Sprawdź wymagane pola
    if not prompt_data.get('user'):
        errors.append('Brak treści wiadomości użytkownika')
    
    # Sprawdź długość
    user_content = prompt_data.get('user', '')
    if len(user_content) > 200000:
        errors.append('Wiadomość użytkownika za długa (max 200k znaków)')
    
    system_content = prompt_data.get('system', '')
    if len(system_content) > 200000:
        errors.append('System prompt za długi (max 200k znaków)')
    
    # Sprawdź temperature
    if 'temperature' in prompt_data:
        temp = prompt_data['temperature']
        if not isinstance(temp, (int, float)) or temp < 0 or temp > 2:
            errors.append('Temperature musi być między 0 a 2 (Ollama pozwala do 2)')
    
    # Sprawdź max_tokens
    if 'max_tokens' in prompt_data:
        max_tokens = prompt_data['max_tokens']
        if not isinstance(max_tokens, int) or max_tokens < 1 or max_tokens > 8192:
            errors.append('Max tokens musi być między 1 a 8192')
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
    }


def main():
    """Main function - CLI interface"""
    if len(sys.argv) < 2:
        print(json.dumps({
            'error': 'Prompt data required',
            'usage': 'python ollama_complete.py <json_prompt_data>',
        }), file=sys.stderr)
        sys.exit(1)
    
    try:
        # Parsuj JSON prompt data
        prompt_json = sys.argv[1]
        # Usuń cudzysłowy jeśli są (z escapeshellarg w PHP)
        clean_json = prompt_json.strip().strip("'").strip('"')
        prompt_data = json.loads(clean_json)
        
        # Waliduj prompt
        validation = validate_prompt(prompt_data)
        if not validation['valid']:
            result = {
                'success': False,
                'error': 'Invalid prompt',
                'validation_errors': validation['errors'],
            }
            print(json.dumps(result), file=sys.stderr)
            sys.exit(1)
        
        # Wywołaj Ollama
        result = complete(prompt_data)
        
        # Zwróć wynik
        output = {
            'success': True,
            'text': result['text'],
            'usage': result['usage'],
            'raw': result['raw'],
        }
        print(json.dumps(output, ensure_ascii=False))
        
    except json.JSONDecodeError as e:
        result = {
            'success': False,
            'error': f'Invalid JSON: {str(e)}',
        }
        print(json.dumps(result), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        result = {
            'success': False,
            'error': str(e),
        }
        print(json.dumps(result), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

