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
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    host = os.getenv('HOST', '127.0.0.1')
    
    logger.info(f"Starting image description API server on {host}:{port}")
    app.run(host=host, port=port, debug=False)

