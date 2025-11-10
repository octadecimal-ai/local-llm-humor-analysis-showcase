#!/usr/bin/env python3
"""
Przykład użycia OllamaClient
"""

import sys
import os

# Dodaj ścieżkę do src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ollama.client import OllamaClient


def main():
    """Przykład użycia OllamaClient"""
    
    # Utwórz klienta
    client = OllamaClient()
    
    # Sprawdź czy serwer jest dostępny
    if not client.check_health():
        print("❌ Ollama serwer nie jest dostępny!")
        print("   Uruchom: ollama serve")
        return
    
    print("✅ Ollama serwer jest dostępny")
    print()
    
    # Lista dostępnych modeli
    print("📋 Dostępne modele:")
    models = client.list_models()
    for model in models[:5]:  # Pokaż pierwsze 5
        print(f"   - {model.get('name', 'unknown')}")
    print()
    
    # Przykład chat
    print("💬 Przykład chat:")
    try:
        result = client.chat(
            user="Powiedz mi krótko, co to jest Python?",
            system="Jesteś pomocnym asystentem. Odpowiadaj po polsku.",
            temperature=0.7,
            max_tokens=100
        )
        print(f"   Odpowiedź: {result['text']}")
        print(f"   Tokens: {result['usage']}")
    except Exception as e:
        print(f"   ❌ Błąd: {e}")
    
    print()
    
    # Przykład generate
    print("✍️  Przykład generate:")
    try:
        result = client.generate(
            prompt="Napisz krótki wiersz o programowaniu:",
            temperature=0.8,
            max_tokens=50
        )
        print(f"   Wygenerowany tekst: {result['text']}")
        print(f"   Tokens: {result['usage']}")
    except Exception as e:
        print(f"   ❌ Błąd: {e}")


if __name__ == '__main__':
    main()

