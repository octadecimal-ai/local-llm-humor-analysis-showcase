#!/usr/bin/env python3
"""
FastAPI server dla ai-local-core
Modularna architektura z możliwością włączania/wyłączania modułów
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
import os

# Dodaj ścieżkę do src do PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.config import config
from api.dependencies import get_logger

# Setup logging
logging.basicConfig(
    level=logging.INFO if not config.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = get_logger(__name__)

# Inicjalizacja FastAPI
app = FastAPI(
    title=config.SERVICE_NAME,
    description="Lokalne serwisy AI dla Waldus API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # W produkcji ograniczyć do konkretnych domen
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": config.SERVICE_NAME,
        "version": "2.0.0"
    }


# Warunkowe włączanie modułów
if config.ENABLE_IMAGE_DESCRIPTION:
    try:
        from modules.image.router import router as image_router
        app.include_router(image_router, prefix="/describe", tags=["Image"])
        logger.info("✅ Moduł Image Description włączony")
    except Exception as e:
        logger.error(f"❌ Błąd włączania modułu Image Description: {e}")

if config.ENABLE_OLLAMA:
    try:
        from modules.ollama.router import router as ollama_router
        app.include_router(ollama_router, prefix="/ollama", tags=["Ollama"])
        logger.info("✅ Moduł Ollama włączony")
    except Exception as e:
        logger.error(f"❌ Błąd włączania modułu Ollama: {e}")

if config.ENABLE_JOKER:
    try:
        from modules.joker.router import router as joker_router
        app.include_router(joker_router, prefix="/joker", tags=["Joker"])
        logger.info("✅ Moduł Joker włączony")
    except Exception as e:
        logger.error(f"❌ Błąd włączania modułu Joker: {e}")

if config.ENABLE_JOKE_ANALYSER:
    try:
        from api.routers.joke_analyser import router as analyser_router
        app.include_router(analyser_router, prefix="/joke-analyser", tags=["Joke Analyser"])
        logger.info("✅ Moduł Joke Analyser włączony")
    except Exception as e:
        logger.error(f"❌ Błąd włączania modułu Joke Analyser: {e}")


# Globalny handler błędów
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Nieoczekiwany błąd: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Wewnętrzny błąd serwera",
            "detail": str(exc) if config.DEBUG else None
        }
    )


if __name__ == "__main__":
    import uvicorn
    logger.info(f"🚀 Uruchamianie {config.SERVICE_NAME} na {config.HOST}:{config.PORT}")
    uvicorn.run(
        "api.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level="info"
    )

