#!/usr/bin/env python3
"""
Test Bielik z promptami dla 9 teorii humoru na żartach Waldusia
Pokazuje szczegółowe logi analizy - co model analizował i dlaczego tak ocenił
"""
import sys
import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ollama.client import OllamaClient
from humor_features.prompts import THEORY_PROMPTS


class BielikAnalyzer:
    """Analizator używający Bielik przez Ollama z promptami dla 9 teorii"""
    
    def __init__(self, model_name: str = "bielik-7b", base_url: str = "http://localhost:11434"):
        """
        Initialize z Bielik przez Ollama
        
        Args:
            model_name: Nazwa modelu w Ollama (default: bielik-7b)
            base_url: URL Ollama server
        """
        self.client = OllamaClient(base_url=base_url, default_model=model_name)
        self.model_name = model_name
        self.prompts = THEORY_PROMPTS
        
        # Statystyki
        self.stats = {
            'total_analyses': 0,
            'successful_analyses': 0,
            'failed_analyses': 0,
            'total_time_ms': 0,
        }
    
    async def analyze_joke_with_theory(
        self, 
        joke_text: str, 
        theory_name: str,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Analizuj żart według jednej teorii używając Bielik
        
        Args:
            joke_text: Tekst żartu
            theory_name: Nazwa teorii (setup_punchline, incongruity, etc.)
            verbose: Czy pokazywać szczegółowe logi
            
        Returns:
            Dict z wynikami analizy + metadata
        """
        if theory_name not in self.prompts:
            raise ValueError(f"Nieznana teoria: {theory_name}")
        
        prompt_template = self.prompts[theory_name]
        prompt = prompt_template.format(joke_text=joke_text)
        
        if verbose:
            print(f"\n{'='*80}")
            print(f"🔍 ANALIZA: {theory_name.upper()}")
            print(f"{'='*80}")
            print(f"📝 Żart: {joke_text[:100]}...")
            print(f"\n📋 Prompt wysłany do Bielik:")
            print(f"{'-'*80}")
            print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
            print(f"{'-'*80}\n")
        
        start_time = time.time()
        
        try:
            # Wywołaj Bielik przez Ollama
            if verbose:
                print("⏳ Wysyłam request do Bielik (Ollama)...")
            
            response = self.client.chat(
                user=prompt,
                system="Jesteś ekspertem analizy humoru. Zawsze odpowiadasz w formacie JSON zgodnie z instrukcjami.",
                temperature=0.3,  # Niższa temperatura = bardziej deterministyczne odpowiedzi
                max_tokens=2000,
            )
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            if verbose:
                print(f"✅ Odpowiedź otrzymana w {elapsed_ms:.2f}ms")
            
            # Parsuj JSON z odpowiedzi
            raw_response = response.get('text', '') if isinstance(response, dict) else str(response)
            
            if verbose:
                print(f"\n📥 RAW RESPONSE (pierwsze 500 znaków):")
                print(f"{'-'*80}")
                print(raw_response[:500] + "..." if len(raw_response) > 500 else raw_response)
                print(f"{'-'*80}\n")
            
            # Spróbuj wyciągnąć JSON z odpowiedzi
            json_data = self._extract_json(raw_response)
            
            if json_data:
                if verbose:
                    print(f"✅ JSON sparsowany pomyślnie")
                    print(f"\n📊 WYNIKI ANALIZY:")
                    print(f"{'-'*80}")
                    self._print_analysis_results(json_data, theory_name)
                    print(f"{'-'*80}\n")
                
                self.stats['successful_analyses'] += 1
                
                return {
                    'theory': theory_name,
                    'success': True,
                    'analysis': json_data,
                    'raw_response': raw_response,
                    'elapsed_ms': elapsed_ms,
                    'model': self.model_name,
                }
            else:
                if verbose:
                    print(f"⚠️  Nie udało się sparsować JSON")
                    print(f"Odpowiedź nie zawiera poprawnego JSON")
                
                self.stats['failed_analyses'] += 1
                
                return {
                    'theory': theory_name,
                    'success': False,
                    'error': 'JSON parsing failed',
                    'raw_response': raw_response,
                    'elapsed_ms': elapsed_ms,
                    'model': self.model_name,
                }
                
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            
            if verbose:
                print(f"❌ Błąd podczas analizy: {e}")
            
            self.stats['failed_analyses'] += 1
            
            return {
                'theory': theory_name,
                'success': False,
                'error': str(e),
                'elapsed_ms': elapsed_ms,
                'model': self.model_name,
            }
        finally:
            self.stats['total_analyses'] += 1
            self.stats['total_time_ms'] += elapsed_ms
    
    def _extract_json(self, text: str) -> Dict[str, Any] | None:
        """Wyciągnij JSON z tekstu odpowiedzi"""
        import re
        
        # Szukaj JSON w odpowiedzi (może być otoczony markdown code blocks)
        json_pattern = r'```json\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, text, re.DOTALL)
        
        if match:
            json_str = match.group(1)
        else:
            # Szukaj samego JSON object
            json_pattern = r'(\{.*\})'
            match = re.search(json_pattern, text, re.DOTALL)
            if match:
                json_str = match.group(1)
            else:
                return None
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None
    
    def _print_analysis_results(self, data: Dict, theory_name: str):
        """Wypisz wyniki analizy w czytelny sposób"""
        # Dla każdej teorii inny format
        if theory_name == 'setup_punchline':
            print(f"SETUP: {data.get('setup', 'N/A')}")
            print(f"OCZEKIWANIE: {data.get('expectation_created', 'N/A')}")
            print(f"ZWROT: {data.get('twist', 'N/A')}")
            print(f"NOWA RAMA: {data.get('new_frame', 'N/A')}")
            print(f"PUNCHLINE: {data.get('punchline', 'N/A')}")
            print(f"DLACZEGO DZIAŁA: {data.get('why_it_works', 'N/A')}")
            print(f"TIMING SCORE: {data.get('timing_score', 'N/A')}/10")
            print(f"STRUCTURE SCORE: {data.get('structure_score', 'N/A')}/10")
        
        elif theory_name == 'incongruity':
            print(f"TYP NIESPÓJNOŚCI: {data.get('incongruity_type', 'N/A')}")
            print(f"RAMA 1: {data.get('frame_1', 'N/A')}")
            print(f"RAMA 2: {data.get('frame_2', 'N/A')}")
            print(f"JAKOŚĆ ROZWIĄZANIA: {data.get('resolution_quality', 'N/A')}")
            print(f"CZYNNIK ZASKOCZENIA: {data.get('surprise_factor', 'N/A')}/10")
            print(f"DOSTĘPNOŚĆ: {data.get('accessibility', 'N/A')}/10")
            print(f"INCONGRUITY SCORE: {data.get('incongruity_score', 'N/A')}/10")
        
        elif theory_name == 'semantic_shift':
            print(f"PRZESUNIĘTE SŁOWO: {data.get('shifted_word', 'N/A')}")
            print(f"ORYGINALNE ZNACZENIE: {data.get('original_meaning', 'N/A')}")
            print(f"NOWE ZNACZENIE: {data.get('new_meaning', 'N/A')}")
            print(f"TYP PRZESUNIĘCIA: {data.get('shift_type', 'N/A')}")
            print(f"PŁYNOŚĆ: {data.get('shift_smoothness', 'N/A')}/10")
            print(f"JAKOŚĆ WIELOZNACZNOŚCI: {data.get('ambiguity_quality', 'N/A')}/10")
            print(f"WORDPLAY SCORE: {data.get('wordplay_score', 'N/A')}/10")
            print(f"SEMANTIC SHIFT SCORE: {data.get('semantic_shift_score', 'N/A')}/10")
        
        elif theory_name == 'timing':
            print(f"TEMPO: {data.get('pacing', 'N/A')}")
            print(f"DŁUGOŚCI ZDAŃ: {data.get('sentence_lengths', 'N/A')}")
            print(f"WARIACJA RYTMU: {data.get('rhythm_variation', 'N/A')}/10")
            print(f"SKUTECZNOŚĆ PAUZ: {data.get('pause_effectiveness', 'N/A')}/10")
            print(f"TIMING DOSTAWY: {data.get('delivery_timing', 'N/A')}/10")
            print(f"TIMING SCORE: {data.get('timing_score', 'N/A')}/10")
        
        elif theory_name == 'absurd_escalation':
            print(f"POCZĄTKOWY ABSURD: {data.get('initial_absurdity', 'N/A')}/10")
            print(f"ESKALACJA OBECNA: {data.get('escalation_present', 'N/A')}")
            print(f"POZIOMY ESKALACJI: {data.get('escalation_levels', 'N/A')}")
            print(f"ZAŁAMANIA LOGICZNE: {data.get('logical_breaks', 'N/A')}")
            print(f"WZMOCNIENIE: {data.get('amplification_factor', 'N/A')}/10")
            print(f"ABSURD ESCALATION SCORE: {data.get('absurd_escalation_score', 'N/A')}/10")
        
        elif theory_name == 'psychoanalysis':
            print(f"MECHANIZM PSYCHOLOGICZNY: {data.get('psychological_mechanism', 'N/A')}")
            print(f"POSTACIE: {data.get('characters', 'N/A')}")
            print(f"ŁUK EMOCJONALNY: {data.get('emotional_arc', 'N/A')}")
            print(f"KONFLIKT: {data.get('conflict_present', 'N/A')}")
            print(f"ROZWIĄZANIE: {data.get('resolution_present', 'N/A')}")
            print(f"APEL PODŚWIADOMY: {data.get('subconscious_appeal', 'N/A')}/10")
            print(f"PSYCHOANALYSIS SCORE: {data.get('psychoanalysis_score', 'N/A')}/10")
        
        elif theory_name == 'archetype':
            print(f"ARCHETYPY: {data.get('archetypes', 'N/A')}")
            print(f"POLSKIE SPECYFICZNE: {data.get('polish_specific', 'N/A')}")
            print(f"MARKERY KULTUROWE: {data.get('cultural_markers', 'N/A')}")
            print(f"REZONANS KULTUROWY: {data.get('cultural_resonance', 'N/A')}/10")
            print(f"UNIWERSALNOŚĆ: {data.get('universality', 'N/A')}/10")
            print(f"ARCHETYPE SCORE: {data.get('archetype_score', 'N/A')}/10")
        
        elif theory_name == 'humor_atoms':
            print(f"ZNALEZIONE ATOMY: {data.get('atoms_found', 'N/A')}")
            print(f"LICZBA ATOMÓW: {data.get('atom_count', 'N/A')}")
            print(f"GĘSTOŚĆ ATOMÓW: {data.get('atom_density', 'N/A')}/10")
            print(f"JAKOŚĆ ATOMÓW: {data.get('atom_quality', 'N/A')}/10")
            print(f"KOMPOZYCJA: {data.get('composition_score', 'N/A')}/10")
            print(f"HUMOR ATOMS SCORE: {data.get('humor_atoms_score', 'N/A')}/10")
        
        elif theory_name == 'reverse_engineering':
            print(f"RDZENNY MECHANIZM: {data.get('core_mechanism', 'N/A')}")
            print(f"WZORZEC STRUKTURALNY: {data.get('structural_pattern', 'N/A')}")
            print(f"KLAROWNOŚĆ MECHANIZMU: {data.get('mechanism_clarity', 'N/A')}/10")
            print(f"SKUTECZNOŚĆ MECHANIZMU: {data.get('mechanism_effectiveness', 'N/A')}/10")
            print(f"REPLIKOWALNOŚĆ: {data.get('replicability', 'N/A')}/10")
            print(f"REVERSE ENGINEERING SCORE: {data.get('reverse_engineering_score', 'N/A')}/10")
        
        # Wypisz wszystkie klucze które nie zostały pokazane
        shown_keys = set()
        if theory_name == 'setup_punchline':
            shown_keys = {'setup', 'expectation_created', 'twist', 'new_frame', 'punchline', 'why_it_works', 'timing_score', 'structure_score'}
        # ... (dla innych teorii)
        
        remaining = {k: v for k, v in data.items() if k not in shown_keys and not k.endswith('_score')}
        if remaining:
            print(f"\n📌 DODATKOWE DANE: {remaining}")


async def main():
    """Główna funkcja testowa"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Bielik z promptami dla 9 teorii humoru')
    parser.add_argument('--joke-id', type=int, help='ID żartu do testowania (1-N)')
    parser.add_argument('--all', action='store_true', help='Testuj wszystkie żarty')
    parser.add_argument('--model', type=str, default='bielik-7b', help='Nazwa modelu Ollama')
    parser.add_argument('--base-url', type=str, default='http://localhost:11434', help='URL Ollama server')
    parser.add_argument('--theory', type=str, help='Testuj tylko jedną teorię (opcjonalne)')
    args = parser.parse_args()
    
    print("🧪 TEST BIELIK Z PROMPTAMI DLA 9 TEORII HUMORU")
    print("=" * 80)
    
    # Załaduj żarty Waldusia
    jokes_file = "validation/test-waldus-classics.json"
    if not os.path.exists(jokes_file):
        print(f"❌ Nie znaleziono pliku: {jokes_file}")
        return
    
    with open(jokes_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    jokes = data.get('jokes', [])
    print(f"📚 Załadowano {len(jokes)} żartów Waldusia\n")
    
    # Wybierz żarty do testowania
    if args.all:
        test_jokes = jokes
        print(f"🎯 Testuję WSZYSTKIE {len(test_jokes)} żarty\n")
    elif args.joke_id:
        test_jokes = [j for j in jokes if j.get('id') == args.joke_id]
        if not test_jokes:
            print(f"❌ Nie znaleziono żartu o ID {args.joke_id}")
            return
        print(f"🎯 Testuję żart #{args.joke_id}\n")
    else:
        # Domyślnie: pierwszy żart
        test_jokes = [jokes[0]] if jokes else []
        print(f"🎯 Testuję pierwszy żart (użyj --joke-id N lub --all dla więcej)\n")
    
    # Wybierz teorie do testowania
    if args.theory:
        if args.theory not in THEORY_PROMPTS:
            print(f"❌ Nieznana teoria: {args.theory}")
            print(f"Dostępne: {', '.join(THEORY_PROMPTS.keys())}")
            return
        theories = [args.theory]
        print(f"🔬 Testuję tylko teorię: {args.theory}\n")
    else:
        theories = list(THEORY_PROMPTS.keys())
        print(f"🔬 Testuję wszystkie 9 teorii\n")
    
    # Initialize analyzer
    analyzer = BielikAnalyzer(model_name=args.model, base_url=args.base_url)
    
    all_results = []
    
    # Testuj każdy żart
    for joke_idx, test_joke in enumerate(test_jokes, 1):
        joke_text = test_joke['text']
        joke_id = test_joke.get('id', joke_idx)
        
        print(f"\n{'#'*80}")
        print(f"# ŻART #{joke_id} ({joke_idx}/{len(test_jokes)})")
        print(f"{'#'*80}")
        print(f"📝 Tekst: {joke_text}\n")
        
        joke_results = []
        
        # Testuj wszystkie wybrane teorie
        for theory_idx, theory in enumerate(theories, 1):
            print(f"\n[{theory_idx}/{len(theories)}] Analizuję teorię: {theory}")
            
            result = await analyzer.analyze_joke_with_theory(
                joke_text=joke_text,
                theory_name=theory,
                verbose=True
            )
            joke_results.append(result)
            
            # Pauza między requestami (żeby nie przeciążać Ollama)
            if theory_idx < len(theories):
                await asyncio.sleep(2)
        
        all_results.append({
            'joke_id': joke_id,
            'joke_text': joke_text,
            'metadata': test_joke.get('metadata', {}),
            'results': joke_results,
        })
    
    # Podsumowanie
    print("\n" + "=" * 80)
    print("📊 PODSUMOWANIE")
    print("=" * 80)
    print(f"✅ Udane analizy: {analyzer.stats['successful_analyses']}/{analyzer.stats['total_analyses']}")
    print(f"❌ Nieudane: {analyzer.stats['failed_analyses']}")
    if analyzer.stats['total_analyses'] > 0:
        avg_time = analyzer.stats['total_time_ms'] / analyzer.stats['total_analyses']
        print(f"⏱️  Średni czas: {avg_time:.2f}ms")
        print(f"⏱️  Całkowity czas: {analyzer.stats['total_time_ms']/1000:.2f}s")
    
    # Zapisuj wyniki do pliku
    output_file = f"test-bielik-results-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_data = {
        'model': analyzer.model_name,
        'base_url': args.base_url,
        'timestamp': datetime.now().isoformat(),
        'theories_tested': theories,
        'jokes_tested': len(test_jokes),
        'results': all_results,
        'stats': analyzer.stats,
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Wyniki zapisane do: {output_file}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

