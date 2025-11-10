#!/usr/bin/env python3
"""
Text Translation Service
Translates text from English to Polish (or other languages)
Uses deep-translator library (simple, no model download needed)
"""

import sys
import json
import os
import logging

try:
    from deep_translator import GoogleTranslator
    DEEP_TRANSLATOR_AVAILABLE = True
except ImportError:
    DEEP_TRANSLATOR_AVAILABLE = False
    logging.warning("deep-translator not available, will try transformers as fallback")

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global translator instance (loaded once)
translator = None
current_target_language = None

# Language codes for deep-translator
LANGUAGE_MAP = {
    'pl': 'pl',  # Polish
    'de': 'de',  # German
    'fr': 'fr',  # French
    'es': 'es',  # Spanish
    'it': 'it',  # Italian
}

# Fallback: Model mapping for transformers (if deep-translator fails)
MODEL_MAP = {
    'pl': 'helsinki-nlp/opus-mt-en-pl',
    'de': 'helsinki-nlp/opus-mt-en-de',
    'fr': 'helsinki-nlp/opus-mt-en-fr',
    'es': 'helsinki-nlp/opus-mt-en-es',
    'it': 'helsinki-nlp/opus-mt-en-it',
}

# Default device for transformers
DEVICE = int(os.getenv('DEVICE_ID', -1))  # -1 for CPU, 0+ for GPU


def load_translator(target_language: str = 'pl'):
    """Load translation translator (lazy loading)"""
    global translator, current_target_language
    
    if translator is None or current_target_language != target_language:
        # Priorytet: użyj deep-translator (prostsze, bez pobierania modeli)
        if DEEP_TRANSLATOR_AVAILABLE:
            lang_code = LANGUAGE_MAP.get(target_language, 'pl')
            logger.info(f"Using deep-translator (GoogleTranslator) for {target_language}")
            translator = GoogleTranslator(source='en', target=lang_code)
            current_target_language = target_language
            logger.info(f"Translator initialized for {target_language}")
        elif TRANSFORMERS_AVAILABLE:
            # Fallback: użyj transformers (wymaga pobrania modelu)
            model_name = MODEL_MAP.get(target_language, MODEL_MAP['pl'])
            logger.info(f"Loading translation model with transformers: {model_name}")
            try:
                import os
                os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
                translator = pipeline(
                    "translation",
                    model=model_name,
                    device=DEVICE,
                    trust_remote_code=True
                )
                current_target_language = target_language
                logger.info(f"Translation model loaded successfully on device {DEVICE}")
            except Exception as e:
                logger.error(f"Error loading translation model: {e}")
                raise
        else:
            raise ImportError("Neither deep-translator nor transformers available. Install: pip install deep-translator")
    else:
        logger.debug(f"Translator already loaded for: {current_target_language}")


def translate_text(text: str, target_language: str = 'pl') -> str:
    """
    Translate text from English to target language
    
    Args:
        text: English text to translate
        target_language: Target language code (pl, de, fr, etc.)
    
    Returns:
        Translated text
    
    Limits:
        - GoogleTranslator: max 5000 characters per request
        - Rate limits: ~10 requests/second (informal limit)
        - For texts > 5000 chars: automatically splits into chunks
    """
    try:
        # Load translator if not loaded
        load_translator(target_language)
        
        # Sprawdź długość tekstu i obsłuż limit 5000 znaków
        MAX_CHARS = 5000
        text_length = len(text)
        
        if text_length > MAX_CHARS:
            logger.warning(f"Text too long ({text_length} chars), splitting into chunks")
            # Podziel tekst na zdania lub fragmenty
            chunks = []
            current_chunk = ""
            
            # Podziel na zdania (separatory: . ! ?)
            sentences = text.replace('. ', '.\n').replace('! ', '!\n').replace('? ', '?\n').split('\n')
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                # Jeśli pojedyncze zdanie jest za długie, skróć
                if len(sentence) > MAX_CHARS:
                    logger.warning(f"Sentence too long ({len(sentence)} chars), truncating")
                    sentence = sentence[:MAX_CHARS]
                
                # Sprawdź czy możemy dodać do obecnego chunka
                if len(current_chunk) + len(sentence) + 1 <= MAX_CHARS:
                    if current_chunk:
                        current_chunk += " " + sentence
                    else:
                        current_chunk = sentence
                else:
                    # Zapisz obecny chunk i zacznij nowy
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = sentence
            
            # Dodaj ostatni chunk jeśli jest
            if current_chunk:
                chunks.append(current_chunk)
            
            # Przetłumacz każdy chunk osobno
            translated_chunks = []
            for i, chunk in enumerate(chunks):
                logger.debug(f"Translating chunk {i+1}/{len(chunks)} ({len(chunk)} chars)")
                if DEEP_TRANSLATOR_AVAILABLE and isinstance(translator, GoogleTranslator):
                    translated_chunk = translator.translate(chunk)
                elif TRANSFORMERS_AVAILABLE:
                    result = translator(chunk, max_length=512)
                    translated_chunk = result[0]['translation_text'] if isinstance(result, list) else result.get('translation_text', chunk)
                else:
                    raise RuntimeError("No translation method available")
                translated_chunks.append(translated_chunk)
                # Małe opóźnienie między requestami aby uniknąć rate limits
                if i < len(chunks) - 1:  # Nie dodawaj opóźnienia po ostatnim chunku
                    import time
                    time.sleep(0.1)
            
            # Połącz przetłumaczone chunki
            translated = " ".join(translated_chunks)
            logger.info(f"Translation completed (split into {len(chunks)} chunks): {text_length} -> {len(translated)} chars")
            return translated
        
        # Normalne tłumaczenie dla tekstów <= 5000 znaków
        logger.debug(f"Translating text to {target_language}: {text[:50]}... ({text_length} chars)")
        
        if DEEP_TRANSLATOR_AVAILABLE and isinstance(translator, GoogleTranslator):
            # Użyj deep-translator (GoogleTranslator)
            translated = translator.translate(text)
        elif TRANSFORMERS_AVAILABLE:
            # Użyj transformers pipeline
            result = translator(text, max_length=512)
            translated = result[0]['translation_text'] if isinstance(result, list) else result.get('translation_text', text)
        else:
            raise RuntimeError("No translation method available")
        
        logger.info(f"Translation completed: {text_length} -> {len(translated)} chars")
        return translated
        
    except Exception as e:
        logger.error(f"Error translating text: {e}")
        raise


def main():
    """Main function - CLI interface"""
    if len(sys.argv) < 2:
        print(json.dumps({
            'error': 'Text to translate required',
            'usage': 'python translate_text.py <text> [target_language]',
            'supported_languages': list(MODEL_MAP.keys())
        }), file=sys.stderr)
        sys.exit(1)
    
    text = sys.argv[1]
    target_language = sys.argv[2] if len(sys.argv) > 2 else 'pl'
    
    # Validate language
    if target_language not in MODEL_MAP:
        error_result = {
            'success': False,
            'error': f'Unsupported language: {target_language}',
            'supported_languages': list(MODEL_MAP.keys())
        }
        print(json.dumps(error_result), file=sys.stderr)
        sys.exit(1)
    
    try:
        translated = translate_text(text, target_language)
        result = {
            'success': True,
            'original': text,
            'translated': translated,
            'source_language': 'en',
            'target_language': target_language
        }
        print(json.dumps(result))
        
    except Exception as e:
        error_result = {
            'success': False,
            'error': str(e),
            'text': text,
            'target_language': target_language
        }
        print(json.dumps(error_result), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

