#!/usr/bin/env python3
"""
Testy jednostkowe dla modułu translation
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Dodaj ścieżkę do src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


class TestTranslation:
    """Testy dla modułu translation"""
    
    @patch('translation.translate.DEEP_TRANSLATOR_AVAILABLE', True)
    @patch('translation.translate.GoogleTranslator')
    def test_translate_text_pl(self, mock_translator_class):
        """Test tłumaczenia na polski"""
        # Mock translator jako instancja klasy
        mock_translator = MagicMock()
        mock_translator.translate.return_value = "Witaj świecie"
        mock_translator_class.return_value = mock_translator
        
        # Mock isinstance żeby zwracał True dla GoogleTranslator
        with patch('translation.translate.isinstance') as mock_isinstance:
            mock_isinstance.return_value = True
            
            from translation.translate import translate_text
            result = translate_text("Hello world", "pl")
            
            assert result == "Witaj świecie"
            mock_translator.translate.assert_called_once_with("Hello world")
    
    @patch('translation.translate.DEEP_TRANSLATOR_AVAILABLE', True)
    @patch('translation.translate.GoogleTranslator')
    def test_translate_text_de(self, mock_translator_class):
        """Test tłumaczenia na niemiecki"""
        mock_translator = MagicMock()
        mock_translator.translate.return_value = "Hallo Welt"
        mock_translator_class.return_value = mock_translator
        
        with patch('translation.translate.isinstance') as mock_isinstance:
            mock_isinstance.return_value = True
            
            from translation.translate import translate_text
            result = translate_text("Hello world", "de")
            
            assert result == "Hallo Welt"
    
    def test_translate_text_empty(self):
        """Test tłumaczenia pustego tekstu"""
        from translation.translate import translate_text
        # Pusty tekst powinien zwrócić pusty string
        result = translate_text("", "pl")
        assert result == ""

