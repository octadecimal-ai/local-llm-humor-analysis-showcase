"""
Router FastAPI dla opisu obrazków
Migracja z Flask: /describe
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from typing import Optional
import logging
import sys
import os

# Dodaj ścieżkę do src do PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from api.config import config
from api.dependencies import get_logger
from image.describe import describe_image, load_model

logger = get_logger(__name__)
router = APIRouter()

# Załaduj model przy starcie
logger.info("Inicjalizacja modułu Image Description...")
try:
    load_model()
    logger.info("✅ Moduł Image Description gotowy")
except Exception as e:
    logger.error(f"❌ Błąd inicjalizacji modułu Image Description: {e}")


class ImageDescriptionRequest(BaseModel):
    """Request model dla opisu obrazka"""
    image_url: HttpUrl
    max_length: Optional[int] = 50


class ImageDescriptionResponse(BaseModel):
    """Response model dla opisu obrazka"""
    success: bool
    description: Optional[str] = None
    image_url: str
    error: Optional[str] = None


@router.post("/", response_model=ImageDescriptionResponse)
async def describe(
    request: ImageDescriptionRequest,
    logger: logging.Logger = Depends(get_logger)
):
    """
    Opisz obrazek
    
    - **image_url**: URL obrazka do opisu
    - **max_length**: Maksymalna długość opisu (domyślnie 50)
    """
    try:
        logger.info(f"Opisywanie obrazka: {request.image_url}")
        description = describe_image(str(request.image_url), request.max_length)
        
        return ImageDescriptionResponse(
            success=True,
            description=description,
            image_url=str(request.image_url)
        )
    except Exception as e:
        logger.error(f"Błąd opisywania obrazka: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Błąd opisywania obrazka: {str(e)}"
        )

