"""
Image description module
Rozpoznawanie i opisywanie obrazków używając modelu BLIP
"""

from .describe import describe_image, load_model, load_image_from_path, download_image

__all__ = ['describe_image', 'load_model', 'load_image_from_path', 'download_image']

