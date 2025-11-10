"""
Ollama client module
Komunikacja z lokalnym serwerem Ollama przez HTTP API
"""

from .complete import complete, validate_prompt
from .client import OllamaClient

__all__ = ['complete', 'validate_prompt', 'OllamaClient']

