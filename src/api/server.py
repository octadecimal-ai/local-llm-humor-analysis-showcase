#!/usr/bin/env python3
"""
Flask API server for image description
Provides REST API endpoint for describing images
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Dodaj ścieżkę do src do PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from image.describe import describe_image, load_model
from ollama.client import OllamaClient
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Ollama client
ollama_client = OllamaClient()

# Load model at startup
logger.info("Initializing image description service...")
try:
    load_model()
    logger.info("Service ready")
except Exception as e:
    logger.error(f"Failed to initialize service: {e}")
    raise


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'image-description'
    })


@app.route('/describe', methods=['POST'])
def describe():
    """
    Describe an image
    
    Request body:
    {
        "image_url": "https://example.com/image.jpg",
        "max_length": 50  # optional
    }
    
    Response:
    {
        "success": true,
        "description": "a cat sitting on a chair",
        "image_url": "https://example.com/image.jpg"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'image_url' not in data:
            return jsonify({
                'success': False,
                'error': 'image_url is required'
            }), 400
        
        image_url = data['image_url']
        max_length = data.get('max_length', 50)
        
        logger.info(f"Describing image: {image_url}")
        description = describe_image(image_url, max_length)
        
        return jsonify({
            'success': True,
            'description': description,
            'image_url': image_url
        })
        
    except Exception as e:
        logger.error(f"Error describing image: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/ollama/chat', methods=['POST'])
def ollama_chat():
    """
    Wykonaj zapytanie do Ollama z przekazanym promptem.
    
    Request body:
    {
        "system": "opcjonalny system prompt",
        "user": "pole wymagane - wiadomość użytkownika",
        "task": "opcjonalne dodatkowe instrukcje",
        "model": "opcjonalna nazwa modelu",
        "temperature": 0.7,
        "max_tokens": 1000
    }
    """
    try:
        data = request.get_json() or {}
        
        user_message = data.get('user')
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Pole "user" jest wymagane'
            }), 400
        
        system_prompt = data.get('system')
        task_prompt = data.get('task')
        if task_prompt:
            user_message = f"{user_message}\n\nZADANIE:\n{task_prompt}"
        
        model = data.get('model')
        temperature = data.get('temperature')
        max_tokens = data.get('max_tokens')
        
        logger.info("Wysyłam zapytanie do Ollama (model=%s)", model or ollama_client.default_model)
        result = ollama_client.chat(
            user=user_message,
            system=system_prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return jsonify({
            'success': True,
            'response': result['text'],
            'usage': result['usage'],
            'model': result['raw'].get('model', model or ollama_client.default_model)
        })
        
    except ValueError as e:
        logger.error("Błąd walidacji zapytania do Ollama: %s", e)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error("Błąd podczas komunikacji z Ollama: %s", e)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    host = os.getenv('HOST', '127.0.0.1')
    
    logger.info(f"Starting image description API server on {host}:{port}")
    app.run(host=host, port=port, debug=False)

