#!/usr/bin/env python3
"""
Klient polling - lokalny serwer pyta serwer OVH czy ma zapytanie do Ollama
"""

import requests
import time
import json
import sys
import os
from typing import Optional, Dict, Any

# Dodaj src do ścieżki
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ollama.client import OllamaClient


class PollingClient:
    """Klient który pyta serwer OVH czy ma zapytanie do Ollama"""
    
    def __init__(self, server_url: str, poll_interval: int = 5):
        """
        Args:
            server_url: URL serwera OVH (np. https://waldus-server.com)
            poll_interval: Czas między zapytaniami w sekundach (domyślnie 5)
        """
        self.server_url = server_url.rstrip('/')
        self.poll_interval = poll_interval
        self.ollama_client = OllamaClient()
        self.running = False
        
    def poll(self) -> Optional[Dict[str, Any]]:
        """
        Pyta serwer czy ma zapytanie
        
        Returns:
            Dict z zapytaniem lub None jeśli brak
        """
        try:
            response = requests.get(
                f"{self.server_url}/api/ollama/poll",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('has_request'):
                    return data.get('request')
            elif response.status_code == 204:
                # Brak zapytania
                return None
            else:
                print(f"⚠️  Błąd serwera: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Błąd połączenia: {e}")
            return None
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Przetwarza zapytanie przez Ollama
        
        Args:
            request: Zapytanie z serwera
            
        Returns:
            Odpowiedź z Ollama
        """
        request_id = request.get('id')
        prompt = request.get('prompt')
        system_prompt = request.get('system_prompt')
        model = request.get('model')
        temperature = request.get('temperature', 0.7)
        max_tokens = request.get('max_tokens', 2000)
        
        print(f"📝 Przetwarzanie zapytania {request_id}...")
        
        try:
            # Użyj OllamaClient do przetworzenia
            result = self.ollama_client.chat(
                user=prompt,
                system=system_prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return {
                'id': request_id,
                'response': result.get('text', ''),
                'model': result.get('model', model),
                'success': True
            }
            
        except Exception as e:
            print(f"❌ Błąd przetwarzania: {e}")
            return {
                'id': request_id,
                'error': str(e),
                'success': False
            }
    
    def submit_response(self, response: Dict[str, Any]) -> bool:
        """
        Wysyła odpowiedź z powrotem na serwer
        
        Args:
            response: Odpowiedź do wysłania
            
        Returns:
            True jeśli sukces
        """
        try:
            result = requests.post(
                f"{self.server_url}/api/ollama/response",
                json=response,
                timeout=30
            )
            
            if result.status_code == 200:
                print(f"✅ Odpowiedź {response.get('id')} wysłana")
                return True
            else:
                print(f"⚠️  Błąd wysyłania odpowiedzi: {result.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Błąd połączenia: {e}")
            return False
    
    def run(self):
        """Główna pętla polling"""
        print(f"🚀 Uruchamianie klienta polling...")
        print(f"   Serwer: {self.server_url}")
        print(f"   Interwał: {self.poll_interval}s")
        print(f"   Ollama: {'✅' if self.ollama_client.check_health() else '❌'}")
        print("")
        
        self.running = True
        
        while self.running:
            try:
                # Sprawdź czy serwer ma zapytanie
                request = self.poll()
                
                if request:
                    print(f"📨 Otrzymano zapytanie: {request.get('id')}")
                    
                    # Przetwórz przez Ollama
                    response = self.process_request(request)
                    
                    # Wyślij odpowiedź
                    self.submit_response(response)
                else:
                    # Brak zapytania - czekaj
                    time.sleep(self.poll_interval)
                    
            except KeyboardInterrupt:
                print("\n🛑 Zatrzymywanie klienta...")
                self.running = False
                break
            except Exception as e:
                print(f"❌ Błąd: {e}")
                time.sleep(self.poll_interval)


def main():
    """Główna funkcja"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Klient polling dla Ollama')
    parser.add_argument(
        '--server',
        default=os.getenv('POLLING_SERVER_URL', 'https://waldus-server.com'),
        help='URL serwera OVH'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=int(os.getenv('POLLING_INTERVAL', '5')),
        help='Interwał polling w sekundach (domyślnie 5)'
    )
    
    args = parser.parse_args()
    
    client = PollingClient(args.server, args.interval)
    client.run()


if __name__ == '__main__':
    main()

