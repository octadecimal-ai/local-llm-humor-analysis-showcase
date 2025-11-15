"""
Konfiguracja aplikacji FastAPI
Wspiera modularną architekturę z możliwością włączania/wyłączania modułów
"""

from pydantic_settings import BaseSettings
from typing import Optional


class ServiceConfig(BaseSettings):
    """Konfiguracja serwisu"""
    
    # Podstawowe ustawienia
    SERVICE_NAME: str = "ai-local-core"
    HOST: str = "127.0.0.1"
    PORT: int = 5001
    DEBUG: bool = False
    
    # Włączanie/wyłączanie modułów
    ENABLE_IMAGE_DESCRIPTION: bool = True
    ENABLE_OLLAMA: bool = True
    ENABLE_JOKER: bool = False
    ENABLE_JOKE_ANALYSER: bool = False
    ENABLE_HUMOR_FEATURES: bool = False  # Nowy: feature extraction bez scoring
    
    # Konfiguracja modułów
    # Image Description
    IMAGE_MODEL_NAME: str = "Salesforce/blip-image-captioning-base"
    
    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_DEFAULT_MODEL: str = "llama2"
    
    # Joker (Bielik 7B)
    JOKER_MODEL_PATH: Optional[str] = None  # Ścieżka do modelu lokalnego
    JOKER_MODEL_NAME: str = "bielik-7b-v0.1"
    JOKER_USE_GPU: bool = True
    JOKER_QUANTIZATION: str = "int8"  # int4, int8, fp16
    
    # Joke Analyser
    JOKE_ANALYSER_MODEL_NAME: str = "allegro/herbert-base-cased"
    JOKE_ANALYSER_USE_GPU: bool = False  # CPU wystarczy
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Globalna instancja konfiguracji
config = ServiceConfig()

