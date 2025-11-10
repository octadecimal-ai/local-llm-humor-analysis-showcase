"""
Wyjątki dla modułu Ollama
"""


class OllamaError(Exception):
    """Bazowy wyjątek dla błędów Ollama"""
    pass


class OllamaConnectionError(OllamaError):
    """Błąd połączenia z serwerem Ollama"""
    pass


class OllamaModelNotFoundError(OllamaError):
    """Model nie został znaleziony"""
    pass


class OllamaTimeoutError(OllamaError):
    """Timeout podczas oczekiwania na odpowiedź"""
    pass


class OllamaValidationError(OllamaError):
    """Błąd walidacji danych wejściowych"""
    pass

