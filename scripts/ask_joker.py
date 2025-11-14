#!/usr/bin/env python3
"""
Skrypt CLI do testowania endpointu Joker
Umożliwia wysyłanie żądań do /joker/generate
"""

import sys
import os
import json
import argparse
import requests
from typing import Optional

# Domyślne ustawienia
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5001
DEFAULT_URL = f"http://{DEFAULT_HOST}:{DEFAULT_PORT}"


def generate_joke(
    url: str,
    topic: Optional[str] = None,
    style: str = "sarcastic",
    length: str = "medium",
    temperature: float = 0.8,
    max_tokens: int = 200
) -> dict:
    """
    Wygeneruj żart używając endpointu Joker
    
    Args:
        url: URL serwera (np. http://127.0.0.1:5001)
        topic: Temat żartu (opcjonalne)
        style: Styl żartu (sarcastic, witty, absurd) - domyślnie sarcastic
        length: Długość (short, medium, long) - domyślnie medium
        temperature: Temperatura generowania (0.0-2.0) - domyślnie 0.8
        max_tokens: Maksymalna liczba tokenów (50-500) - domyślnie 200
    
    Returns:
        dict: Odpowiedź z serwera
    """
    endpoint = f"{url}/joker/generate"
    
    payload = {
        "style": style,
        "length": length,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    if topic:
        payload["topic"] = topic
    
    try:
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120  # Długi timeout dla generowania
        )
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": f"Nie można połączyć się z serwerem {url}. Upewnij się, że serwer jest uruchomiony."
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Timeout - generowanie trwa zbyt długo"
        }
    except requests.exceptions.HTTPError as e:
        try:
            error_data = response.json()
            return error_data
        except:
            return {
                "success": False,
                "error": f"Błąd HTTP {e.response.status_code}: {e.response.text}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Nieoczekiwany błąd: {str(e)}"
        }


def check_health(url: str) -> bool:
    """
    Sprawdź czy serwis Joker jest dostępny
    
    Args:
        url: URL serwera
    
    Returns:
        bool: True jeśli serwis jest dostępny
    """
    try:
        response = requests.get(f"{url}/joker/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def main():
    """Główna funkcja CLI"""
    parser = argparse.ArgumentParser(
        description="Testowanie endpointu Joker - generowanie żartów",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:

  # Podstawowe użycie z tematem
  python scripts/ask_joker.py --topic "programista"

  # Z niestandardowym stylem
  python scripts/ask_joker.py --topic "koty" --style "witty"

  # Krótki żart
  python scripts/ask_joker.py --topic "Python" --length "short"

  # Z niestandardową temperaturą i max_tokens
  python scripts/ask_joker.py --topic "AI" --temperature 0.9 --max-tokens 150

  # Bez tematu (ogólny żart)
  python scripts/ask_joker.py --style "absurd"

  # Z niestandardowym URL serwera
  python scripts/ask_joker.py --topic "test" --url http://127.0.0.1:5001
        """
    )
    
    parser.add_argument(
        "--topic",
        type=str,
        help="Temat żartu (opcjonalne)"
    )
    
    parser.add_argument(
        "--style",
        type=str,
        choices=["sarcastic", "witty", "absurd"],
        default="sarcastic",
        help="Styl żartu (domyślnie: sarcastic)"
    )
    
    parser.add_argument(
        "--length",
        type=str,
        choices=["short", "medium", "long"],
        default="medium",
        help="Długość żartu (domyślnie: medium)"
    )
    
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.8,
        help="Temperatura generowania 0.0-2.0 (domyślnie: 0.8)"
    )
    
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=200,
        help="Maksymalna liczba tokenów 50-500 (domyślnie: 200)"
    )
    
    parser.add_argument(
        "--url",
        type=str,
        default=DEFAULT_URL,
        help=f"URL serwera (domyślnie: {DEFAULT_URL})"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Wyświetl odpowiedź w formacie JSON"
    )
    
    parser.add_argument(
        "--health",
        action="store_true",
        help="Sprawdź tylko czy serwis jest dostępny"
    )
    
    args = parser.parse_args()
    
    # Sprawdź health check
    if args.health:
        if check_health(args.url):
            print("✅ Serwis Joker jest dostępny")
            sys.exit(0)
        else:
            print("❌ Serwis Joker nie jest dostępny")
            sys.exit(1)
    
    # Walidacja parametrów
    if args.temperature < 0.0 or args.temperature > 2.0:
        print("❌ Błąd: temperature musi być w zakresie 0.0-2.0", file=sys.stderr)
        sys.exit(1)
    
    if args.max_tokens < 50 or args.max_tokens > 500:
        print("❌ Błąd: max-tokens musi być w zakresie 50-500", file=sys.stderr)
        sys.exit(1)
    
    # Wygeneruj żart
    print(f"🎭 Wysyłanie żądania do {args.url}/joker/generate...")
    if args.topic:
        print(f"   Temat: {args.topic}")
    print(f"   Styl: {args.style}")
    print(f"   Długość: {args.length}")
    print(f"   Temperature: {args.temperature}")
    print(f"   Max tokens: {args.max_tokens}")
    print()
    
    result = generate_joke(
        url=args.url,
        topic=args.topic,
        style=args.style,
        length=args.length,
        temperature=args.temperature,
        max_tokens=args.max_tokens
    )
    
    # Wyświetl wynik
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result.get("success"):
            print("✅ Sukces!")
            print()
            if result.get("joke"):
                print("Żart:")
                print("-" * 60)
                print(result["joke"])
                print("-" * 60)
                print()
            
            if result.get("generation_time"):
                print(f"⏱️  Czas generowania: {result['generation_time']:.2f}s")
            
            if result.get("model"):
                print(f"🤖 Model: {result['model']}")
            
            if result.get("topic"):
                print(f"📝 Temat: {result['topic']}")
            
            if result.get("style"):
                print(f"🎨 Styl: {result['style']}")
        else:
            print("❌ Błąd!")
            print()
            if result.get("error"):
                print(f"Błąd: {result['error']}")
            else:
                print("Nieznany błąd")
            sys.exit(1)


if __name__ == "__main__":
    main()

