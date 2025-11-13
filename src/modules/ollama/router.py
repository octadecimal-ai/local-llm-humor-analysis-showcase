"""
Router FastAPI dla Ollama
Migracja z Flask: /ollama/chat
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import logging
import sys
import os

# Dodaj ścieżkę do src do PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from api.config import config
from api.dependencies import get_logger
from ollama.client import OllamaClient

logger = get_logger(__name__)
router = APIRouter()

# Inicjalizacja klienta Ollama
ollama_client = OllamaClient(
    base_url=config.OLLAMA_BASE_URL,
    default_model=config.OLLAMA_DEFAULT_MODEL
)


class OllamaChatRequest(BaseModel):
    """Request model dla chat Ollama"""
    user: str
    system: Optional[str] = None
    task: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000


class OllamaChatResponse(BaseModel):
    """Response model dla chat Ollama"""
    success: bool
    response: Optional[str] = None
    usage: Optional[dict] = None
    model: Optional[str] = None
    error: Optional[str] = None


@router.post("/chat", response_model=OllamaChatResponse)
async def chat(
    request: OllamaChatRequest,
    logger: logging.Logger = Depends(get_logger)
):
    """
    Wykonaj zapytanie do Ollama z przekazanym promptem
    
    - **user**: Wiadomość użytkownika (wymagane)
    - **system**: Opcjonalny system prompt
    - **task**: Opcjonalne dodatkowe instrukcje
    - **model**: Opcjonalna nazwa modelu
    - **temperature**: Temperatura (domyślnie 0.7)
    - **max_tokens**: Maksymalna liczba tokenów (domyślnie 1000)
    """
    try:
        user_message = request.user
        if request.task:
            user_message = f"{user_message}\n\nZADANIE:\n{request.task}"
        
        logger.info(f"Wysyłanie zapytania do Ollama (model={request.model or ollama_client.default_model})")
        result = ollama_client.chat(
            user=user_message,
            system=request.system,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return OllamaChatResponse(
            success=True,
            response=result['text'],
            usage=result['usage'],
            model=result['raw'].get('model', request.model or ollama_client.default_model)
        )
    except ValueError as e:
        logger.error(f"Błąd walidacji zapytania do Ollama: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Błąd podczas komunikacji z Ollama: {e}")
        raise HTTPException(status_code=500, detail=str(e))

