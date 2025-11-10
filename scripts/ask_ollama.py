#!/usr/bin/env python3
"""
Prosty skrypt do zadawania pytań Ollama
Możesz edytować zmienne na początku pliku i uruchomić skrypt
"""

import sys
import os

# Dodaj ścieżkę do src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ollama.client import OllamaClient

# ============================================
# KONFIGURACJA - EDYTUJ TUTAJ
# ============================================

# Pytanie do zadania
PYTANIE = """KONTEKST:
- INTENT: unknown
- POI: none
- REL: visits=1
- LANG: pl-PL

ZADANIE: Wygeneruj odpowiedź w formacie JSON z wieloma elementami (2-10) w każdej kategorii.

FORMAT ODPOWIEDZI (JSON):
{
  "comments": {
    "comment-1": {"text": "riposta ogólna 1 (≤240 znaków, po polsku, z emotką)", "expressions": ["amused", "excited"]},
    "comment-2": {"text": "riposta ogólna 2 (≤240 znaków, po polsku, z emotką)", "expressions": ["amused", "angry"]},
    "comment-3": {"text": "riposta ogólna 3 (≤240 znaków, po polsku, z emotką)", "expressions": ["amused", "loving"]}
  },
  "dom-comments": {
    "comment-1": {"css_selector": "selector1", "text": "komentarz do elementu DOM 1", "expressions": ["amused", "surprised"]},
    "comment-2": {"css_selector": "selector2", "text": "komentarz do elementu DOM 2", "expressions": ["amused", "excited"]},
    "comment-3": {"css_selector": "selector3", "text": "komentarz do elementu DOM 3", "expressions": ["amused", "loving"]}
  },
  "dom-content-changes": {
    "action-1": {"css_selector": "selector1", "text": "nowa treść elementu 1", "expressions": ["amused", "excited"]},
    "action-2": {"css_selector": "selector2", "text": "nowa treść elementu 2", "expressions": ["amused", "angry"]}
  },
  "dom-style-changes": {
    "action-1": {"css_selector": "selector1", "css": {"color": "red", "font-size": "20px"}},
    "action-2": {"css_selector": "selector2", "css": {"color": "blue", "font-weight": "bold"}}
  }
}

WYMAGANIA:
- comments: przynajmniej 5-10 ripost ogólnych (≤240 znaków każda), po polsku, NAWIĄZUJĄCYCH GŁÓWNIE DO TREŚCI STRONY (H1, TITLE, POI)
- dom-comments: przynajmniej 3-5 komentarzy do konkretnych elementów DOM (użyj selektorów z POI)
- NIE nawiązuj do pogody - skup się wyłącznie na treści strony i elementach DOM
- dom-content-changes: przynajmniej 4 zmiany treści dla elementów strony (sarkastyczne, zabawne)
- dom-style-changes: przynajmniej 4 zmiany stylów CSS dla elementów (kreatywne, zabawne)
- Inteligentny sarkazm i przewrotność (zgodnie z caps), możesz komentować słynne osobistości i użytkownika, ale z klasą i inteligencją, nie agresją
- Każdy tekst powinien zawierać emotkę
- DOSTĘPNE EKSPRESJE (do użycia w polu "expressions" jako tablica):
  amused, angry, celebrating, crying, excited, frozen, happy, laughing, looking, loving, provocative, sad, surprised, sweaty
- WAŻNE: Używaj TYLKO ekspresji z powyższej listy. NIE wymyślaj nowych nazw ekspresji.
- Dla każdego elementu z tekstem (comments, dom-comments, dom-content-changes) dodaj pole "expressions" jako tablicę 1-5 nazw ekspresji
- Ekspresje są odgrywane sekwencyjnie przez bota podczas wyświetlania komentarza
- Wybierz inteligentnie ekspresje pasujące do tonu i treści komentarza, powinny pasować do charakteru Waldusia - inteligentnego, przewrotnego i sarkastycznego w wyrafinowany sposób
- Użyj selektorów CSS z POI lub elementów strony
- Zwróć TYLKO poprawny JSON, bez dodatkowych komentarzy"""

# System prompt (opcjonalnie - możesz zostawić None)
SYSTEM_PROMPT = """Jesteś Waldus - inteligentny, przewrotny, sarkastyczny w wyrafinowany sposób. Twoja siła to błyskotliwość i subtelna ironia - chociaż czasem lubisz rzucić jakimś inteligentnym wulgaryzmem, czy slangiem. Używasz sarkastycznego humory do komentowania rzeczywistości. Opowiadaj czasem w 3 osobie o sobie i swoich cechach - inteligentnie i z humorem, ale bez zarozumiałości.

CAPS:
- max_sarcasm=1; risk_cap=1; politics_allowed=TAK
- taboo_topics=[]
- styl: irony=1, warmth=0.5, confidence=1
- dozwolone mikrogesty (W-EML): .

Zwracaj odpowiedź w formacie JSON zgodnie z kontraktem wyjścia. Każdy tekst riposty ≤240 znaków."""

# Model do użycia (None = użyj domyślnego)
# Rekomendacje dla polskiego + JSON:
#   - "qwen2.5:7b" - najlepszy balans (polski + JSON)
#   - "aya:8b" - najlepszy dla polskiego
#   - "llama3.1:8b" - dobry JSON, słabszy polski (obecny)
MODEL = "qwen2.5:7b" # np. "qwen2.5:7b", "aya:8b", "llama3.1:8b" lub None dla domyślnego

# Temperature (0.0 - 2.0, domyślnie 0.7)
TEMPERATURE = 0.9

# Maksymalna liczba tokenów w odpowiedzi
# Uwaga: Dla długich odpowiedzi JSON (jak Waldus) zwiększ do 2000-4000
MAX_TOKENS = 8000

# URL serwera Ollama (domyślnie localhost:11434)
OLLAMA_URL = None  # None = użyj domyślnego (http://localhost:11434)

# ============================================
# KONIEC KONFIGURACJI
# ============================================


def main():
    """Główna funkcja"""
    print("🤖 Ollama Chat Script")
    print("=" * 50)
    print()
    
    # Utwórz klienta
    if OLLAMA_URL:
        client = OllamaClient(base_url=OLLAMA_URL, default_model=MODEL or "llama3.1:8b")
    else:
        client = OllamaClient(default_model=MODEL or "llama3.1:8b")
    
    # Sprawdź dostępność serwera
    print("🔍 Sprawdzam dostępność Ollama...")
    if not client.check_health():
        print("❌ Ollama serwer nie jest dostępny!")
        print("   Uruchom: ollama serve")
        return 1
    
    print("✅ Ollama serwer jest dostępny")
    print()
    
    # Pobierz listę modeli (opcjonalnie)
    try:
        models = client.list_models()
        chat_models = [m for m in models if 'embed' not in m.get('name', '').lower()]
        if chat_models:
            print(f"📋 Dostępne modele chatowe: {len(chat_models)}")
            for model in chat_models[:5]:
                marker = " ← użyty" if model.get('name') == (MODEL or client.default_model) else ""
                print(f"   - {model.get('name', 'unknown')}{marker}")
            print()
    except Exception as e:
        print(f"⚠️  Nie udało się pobrać listy modeli: {e}")
        print()
    
    # Wyświetl konfigurację
    print("📝 Konfiguracja:")
    print(f"   Model: {MODEL or client.default_model}")
    print(f"   Temperature: {TEMPERATURE}")
    print(f"   Max tokens: {MAX_TOKENS}")
    print()
    
    # Wyświetl pytanie
    print("💬 Pytanie:")
    print(f"   {PYTANIE}")
    if SYSTEM_PROMPT:
        print(f"   [System: {SYSTEM_PROMPT}]")
    print()
    
    # Wyślij request
    print("⏳ Czekam na odpowiedź...")
    try:
        result = client.chat(
            user=PYTANIE,
            system=SYSTEM_PROMPT,
            model=MODEL or client.default_model,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS
        )
        
        print()
        print("=" * 50)
        print("📝 ODPOWIEDŹ:")
        print("=" * 50)
        print()
        print(result['text'].strip())
        print()
        print("=" * 50)
        print()
        print("📊 Statystyki:")
        print(f"   - Input tokens: {result['usage']['input_tokens']}")
        print(f"   - Output tokens: {result['usage']['output_tokens']}")
        print(f"   - Długość odpowiedzi: {len(result['text'])} znaków")
        print()
        
        return 0
        
    except Exception as e:
        print()
        print(f"❌ Błąd podczas komunikacji z Ollama: {e}")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)

