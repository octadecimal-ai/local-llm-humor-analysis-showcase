#!/usr/bin/env python3
"""
Image Description Service using BLIP
Describes images using Salesforce BLIP model
"""

import sys
import json
import requests
from io import BytesIO
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import os
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Model configuration
MODEL_NAME = os.getenv('BLIP_MODEL', 'Salesforce/blip-image-captioning-base')
DEVICE_NAME = os.getenv('DEVICE', 'cpu')  # 'cpu' or 'cuda'

# Global model instance (loaded once)
processor = None
model = None
device = None  # Device where model is loaded


def load_model():
    """Load BLIP model and processor (lazy loading)"""
    global processor, model, device
    
    if processor is None or model is None:
        logger.info(f"Loading BLIP model: {MODEL_NAME}")
        try:
            processor = BlipProcessor.from_pretrained(MODEL_NAME)
            model = BlipForConditionalGeneration.from_pretrained(MODEL_NAME)
            
            # Move to device if available
            device_name = DEVICE_NAME
            if device_name == 'cuda':
                try:
                    import torch
                    if torch.cuda.is_available():
                        model = model.to(device_name)
                        device = device_name
                        logger.info("Using GPU acceleration")
                    else:
                        logger.warning("CUDA not available, using CPU")
                        device = 'cpu'
                except:
                    logger.warning("CUDA not available, using CPU")
                    device = 'cpu'
            else:
                device = 'cpu'
            
            logger.info(f"Model loaded successfully on {device}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    else:
        logger.debug("Model already loaded")


def load_image_from_path(file_path: str) -> Image.Image:
    """Load image from file path"""
    try:
        logger.info(f"Loading image from file: {file_path}")
        image = Image.open(file_path)
        # Convert to RGB if necessary (for RGBA, etc.)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return image
    except Exception as e:
        logger.error(f"Error loading image from {file_path}: {e}")
        raise


def download_image(url: str) -> Image.Image:
    """Download image from URL (legacy - kept for compatibility)"""
    try:
        response = requests.get(url, timeout=10, stream=True)
        response.raise_for_status()
        
        image = Image.open(BytesIO(response.content))
        # Convert to RGB if necessary (for RGBA, etc.)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
    except Exception as e:
        logger.error(f"Error downloading image from {url}: {e}")
        raise


def describe_image(image_path_or_url: str, max_length: int = 50) -> str:
    """
    Describe an image using BLIP model
    
    Args:
        image_path_or_url: Path to image file or URL of the image to describe
        max_length: Maximum length of generated caption
    
    Returns:
        String description of the image
    """
    try:
        # Load model if not already loaded
        load_model()
        
        # Load image - sprawdź czy to ścieżka do pliku czy URL
        # Usuń cudzysłowy jeśli są (z escapeshellarg w PHP)
        clean_path = image_path_or_url.strip().strip("'").strip('"')
        
        if os.path.exists(clean_path):
            logger.info(f"Loading image from file: {clean_path}")
            image = load_image_from_path(clean_path)
        else:
            logger.info(f"Downloading image from URL: {clean_path}")
            image = download_image(clean_path)
        
        # Process image
        logger.debug("Processing image with BLIP")
        inputs = processor(image, return_tensors="pt")
        
        # Move inputs to same device as model
        if device and device != 'cpu':
            inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Generate caption
        logger.debug("Generating caption")
        out = model.generate(**inputs, max_length=max_length)
        
        # Decode caption
        caption = processor.decode(out[0], skip_special_tokens=True)
        
        logger.info(f"Generated caption: {caption}")
        return caption
        
    except Exception as e:
        logger.error(f"Error describing image: {e}")
        raise


def main():
    """Main function - CLI interface"""
    if len(sys.argv) < 2:
        print(json.dumps({
            'error': 'Image path or URL required',
            'usage': 'python describe_image.py <image_path_or_url> [max_length]'
        }), file=sys.stderr)
        sys.exit(1)
    
    image_path_or_url = sys.argv[1]
    max_length = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    
    # Usuń cudzysłowy jeśli są (z escapeshellarg w PHP)
    clean_path = image_path_or_url.strip().strip("'").strip('"')
    
    try:
        description = describe_image(clean_path, max_length)
        result = {
            'success': True,
            'description': description,
            'image_path_or_url': clean_path
        }
        print(json.dumps(result))
        
    except Exception as e:
        error_result = {
            'success': False,
            'error': str(e),
            'image_path_or_url': image_path_or_url
        }
        print(json.dumps(error_result), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

