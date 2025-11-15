"""
Prompty dla 9 teorii humoru - używane przez LLM (Bielik/Ollama)
Każdy prompt opisuje algorytm analizy według danej teorii
Wszystkie prompty są po polsku, bo Bielik to polski model
"""

SETUP_PUNCHLINE_PROMPT = """Jesteś analitykiem struktury żartów. Twoim zadaniem jest rozłożenie żartów na komponenty Setup-Punchline i wyjaśnienie mechanizmu.

RAMY ANALIZY:

**Krok 1: Zidentyfikuj Setup**
- Jaki jest początkowy scenariusz/kontekst?
- Jakie oczekiwanie tworzy?
- Jaką "normalną" ramę odniesienia ustanawia?

**Krok 2: Zidentyfikuj Zwrot**
- W którym dokładnie momencie oczekiwanie się załamuje?
- Jakie słowo/fraza wywołuje przesunięcie?
- Jaka NOWA rama odniesienia zostaje wprowadzona?

**Krok 3: Zidentyfikuj Punchline**
- Jak punchline rozwiązuje niespójność?
- Dlaczego to rozwiązanie jest śmieszne, a nie tylko mylące?
- Co sprawia, że logiczny skok działa?

**Krok 4: Analiza Timing**
- Jak szybko zwrot następuje po setupie?
- Czy jest pauza/opóźnienie przed punchline?
- Oceń timing: ZA_SZYBKO / IDEALNY / ZA_WOLNO

**Format Wyjścia (JSON):**
{{
  "setup": "cytat z tekstu setupu",
  "expectation_created": "czego oczekujemy że się stanie",
  "twist": "dokładny moment przesunięcia",
  "new_frame": "jaka rzeczywistość zostaje wprowadzona",
  "punchline": "rozwiązanie",
  "why_it_works": "wyjaśnienie mechanizmu humoru",
  "timing_score": 1-10,
  "structure_score": 1-10
}}

Teraz przeanalizuj następujący żart:

{joke_text}"""


INCONGRUITY_PROMPT = """Jesteś ekspertem teorii humoru analizującym żarty przez pryzmat Teorii Niespójności.

RAMY ANALIZY:

**Krok 1: Zidentyfikuj Niespójność**
- Jakie dwie niekompatybilne ramy odniesienia się zderzają?
- Jakie oczekiwanie zostaje naruszone?
- Jaka logiczna sprzeczność istnieje?

**Krok 2: Jakość Rozwiązania**
- Czy niespójność zostaje rozwiązana? (całkowicie/częściowo/nierozwiązana)
- Jak satysfakcjonujące jest rozwiązanie?
- Czy tworzy moment "aha!"?

**Krok 3: Siła Niespójności**
- Jak silny jest kontrast? (subtelny/umiarkowany/ekstremalny)
- Jak nieoczekiwany jest zwrot?
- Oceń czynnik zaskoczenia: 1-10

**Krok 4: Przetwarzanie Poznawcze**
- Ile pracy umysłowej wymaga "zrozumienie"?
- Czy jest dostępny czy wymaga specjalistycznej wiedzy?
- Oceń dostępność: 1-10

**Format Wyjścia (JSON):**
{{
  "incongruity_type": "naruszenie_oczekiwania / sprzeczność_logiczna / zderzenie_ram",
  "frame_1": "pierwsza rama odniesienia",
  "frame_2": "druga konfliktująca rama",
  "resolution_quality": "całkowicie/częściowo/nierozwiązana",
  "surprise_factor": 1-10,
  "accessibility": 1-10,
  "incongruity_score": 1-10
}}

Teraz przeanalizuj następujący żart:

{joke_text}"""


SEMANTIC_SHIFT_PROMPT = """Analizujesz żarty przez pryzmat Teorii Przesunięcia Znaczeniowego - jak znaczenie się deformuje i przesuwa.

RAMY ANALIZY:

**Krok 1: Zidentyfikuj Przesunięcie Znaczeniowe**
- Które słowo/fraza zmienia znaczenie?
- Jakie jest oryginalne znaczenie?
- Jakie jest nowe znaczenie?
- Jak kontekst wymusza przesunięcie?

**Krok 2: Mechanizm Przesunięcia**
- Czy to: polisemia (wiele znaczeń) / metafora / metonimia / gra słów?
- Jak naturalne jest przesunięcie?
- Oceń płynność przesunięcia: 1-10

**Krok 3: Wykorzystanie Wieloznaczności**
- Jak dobrze żart wykorzystuje wieloznaczność?
- Czy wieloznaczność jest oczywista czy ukryta?
- Oceń jakość wieloznaczności: 1-10

**Krok 4: Jakość Gry Słów**
- Jak sprytna jest gra słów?
- Czy wydaje się wymuszona czy naturalna?
- Oceń score gry słów: 1-10

**Format Wyjścia (JSON):**
{{
  "shifted_word": "słowo/fraza która się przesuwa",
  "original_meaning": "oryginalne znaczenie",
  "new_meaning": "przesunięte znaczenie",
  "shift_type": "polisemia / metafora / metonimia / gra_słów",
  "shift_smoothness": 1-10,
  "ambiguity_quality": 1-10,
  "wordplay_score": 1-10,
  "semantic_shift_score": 1-10
}}

Teraz przeanalizuj następujący żart:

{joke_text}"""


TIMING_PROMPT = """Analizujesz timing i rytm żartu - temporalną mechanikę humoru.

RAMY ANALIZY:

**Krok 1: Analiza Tempa**
- Jak szybko żart się rozwija?
- Czy jest narastanie czy natychmiastowa zapłata?
- Oceń tempo: ZA_SZYBKO / IDEALNE / ZA_WOLNO

**Krok 2: Wykrywanie Rytmu**
- Jaki jest wzorzec długości zdań?
- Czy jest wariacja w rytmie?
- Oceń jakość rytmu: 1-10

**Krok 3: Umiejscowienie Pauz**
- Gdzie są naturalne pauzy?
- Czy jest dramatyczna pauza przed punchline?
- Oceń skuteczność pauz: 1-10

**Krok 4: Timing Dostawy**
- Jak dobrze wyważony jest punchline?
- Czy jest pospieszny czy idealnie umieszczony?
- Oceń dostawę: 1-10

**Format Wyjścia (JSON):**
{{
  "pacing": "ZA_SZYBKO / IDEALNE / ZA_WOLNO",
  "sentence_lengths": [lista liczby słów na zdanie],
  "rhythm_variation": 1-10,
  "pause_effectiveness": 1-10,
  "delivery_timing": 1-10,
  "timing_score": 1-10
}}

Teraz przeanalizuj następujący żart:

{joke_text}"""


ABSURD_ESCALATION_PROMPT = """Analizujesz żarty przez pryzmat Teorii Eskalacji Absurdu - jak absurd się wzmacnia.

RAMY ANALIZY:

**Krok 1: Wykrywanie Absurdu**
- Co jest absurdalne w żarcie?
- Jak realistyczny vs. absurdalny jest scenariusz?
- Oceń początkowy absurd: 1-10

**Krok 2: Wzorzec Eskalacji**
- Czy absurd eskaluje? (tak/nie)
- Ile poziomów eskalacji?
- Oceń siłę eskalacji: 1-10

**Krok 3: Załamania Logiczne**
- Gdzie logika się załamuje?
- Ile załamań logicznych?
- Oceń jakość załamania: 1-10

**Krok 4: Wzmocnienie Absurdu**
- O ile absurd się wzmacnia od początku do końca?
- Czy eskalacja jest satysfakcjonująca?
- Oceń wzmocnienie: 1-10

**Format Wyjścia (JSON):**
{{
  "initial_absurdity": 1-10,
  "escalation_present": true/false,
  "escalation_levels": liczba,
  "logical_breaks": [lista załamań],
  "amplification_factor": 1-10,
  "absurd_escalation_score": 1-10
}}

Teraz przeanalizuj następujący żart:

{joke_text}"""


PSYCHOANALYSIS_PROMPT = """Analizujesz żarty przez pryzmat Narracyjnej Psychoanalizy - psychologiczną i narracyjną głębię.

RAMY ANALIZY:

**Krok 1: Głębia Psychologiczna**
- Jaki mechanizm psychologiczny jest w grze?
- Czy jest represja / projekcja / przemieszczenie?
- Oceń głębię psychologiczną: 1-10

**Krok 2: Analiza Postaci**
- Kim są postacie?
- Jakie są ich motywacje?
- Oceń głębię postaci: 1-10

**Krok 3: Łuk Narracyjny**
- Jaki jest łuk emocjonalny? (pozytywny/negatywny/neutralny/odwrócenie)
- Czy jest konflikt i rozwiązanie?
- Oceń jakość narracji: 1-10

**Krok 4: Apel Podświadomy**
- Jakie podświadome pragnienie/strach dotyka?
- Jak uniwersalny jest apel?
- Oceń apel podświadomy: 1-10

**Format Wyjścia (JSON):**
{{
  "psychological_mechanism": "represja / projekcja / przemieszczenie / inne",
  "characters": [lista postaci],
  "emotional_arc": "pozytywny / negatywny / neutralny / odwrócenie",
  "conflict_present": true/false,
  "resolution_present": true/false,
  "subconscious_appeal": 1-10,
  "psychoanalysis_score": 1-10
}}

Teraz przeanalizuj następujący żart:

{joke_text}"""


ARCHETYPE_PROMPT = """Analizujesz żarty przez pryzmat Teorii Archetypów - uniwersalne wzorce i polskie archetypy kulturowe.

RAMY ANALIZY:

**Krok 1: Identyfikacja Archetypu**
- Jakie archetypy się pojawiają? (bohater, antybohater, błazen, mentor, etc.)
- Czy są specyficzne dla Polski? (Janusz, Grażyna, Seba, etc.)
- Oceń klarowność archetypu: 1-10

**Krok 2: Rezonans Kulturowy**
- Jak dobrze rezonuje z polską kulturą?
- Czy są markery kulturowe?
- Oceń rezonans kulturowy: 1-10

**Krok 3: Uniwersalne vs. Lokalne**
- Czy jest uniwersalne czy specyficzne dla Polski?
- Jak dostępne dla niepolskiej publiczności?
- Oceń uniwersalność: 1-10

**Krok 4: Siła Archetypu**
- Jak silny jest archetyp?
- Czy jest stereotypowy czy zniuansowany?
- Oceń score archetypu: 1-10

**Format Wyjścia (JSON):**
{{
  "archetypes": [lista archetypów],
  "polish_specific": true/false,
  "cultural_markers": [lista markerów],
  "cultural_resonance": 1-10,
  "universality": 1-10,
  "archetype_score": 1-10
}}

Teraz przeanalizuj następujący żart:

{joke_text}"""


HUMOR_ATOMS_PROMPT = """Analizujesz żarty przez pryzmat Teorii Atomów Humoru - mikro-komponenty humoru.

RAMY ANALIZY:

**Krok 1: Komponenty Atomowe**
- Jakie mikro-elementy tworzą humor?
- Emoji, wykrzykniki, WIELKIE_LITERY, powtórzenia?
- Wypisz wszystkie znalezione atomy

**Krok 2: Gęstość Atomów**
- Ile atomów na zdanie?
- Czy gęstość jest za wysoka (przytłaczająca) czy idealna?
- Oceń gęstość atomów: 1-10

**Krok 3: Jakość Atomów**
- Czy atomy są dobrze umieszczone czy losowe?
- Czy wzmacniają czy rozpraszają?
- Oceń jakość atomów: 1-10

**Krok 4: Kompozycja Atomowa**
- Jak dobrze atomy współpracują?
- Czy jest synergia czy chaos?
- Oceń kompozycję: 1-10

**Format Wyjścia (JSON):**
{{
  "atoms_found": ["emoji", "exclamation", "CAPS", "repetition", "sound_word", etc.],
  "atom_count": liczba,
  "atom_density": 1-10,
  "atom_quality": 1-10,
  "composition_score": 1-10,
  "humor_atoms_score": 1-10
}}

Teraz przeanalizuj następujący żart:

{joke_text}"""


REVERSE_ENGINEERING_PROMPT = """Odwrotnie inżynierujesz żarty - analizujesz mechanizm bez treści.

RAMY ANALIZY:

**Krok 1: Identyfikacja Mechanizmu**
- Jaki jest rdzenny mechanizm? (gra słów, absurd, timing, struktura, etc.)
- Czy możesz go zidentyfikować bez znajomości treści?
- Oceń klarowność mechanizmu: 1-10

**Krok 2: Wzorzec Strukturalny**
- Jaki wzorzec strukturalny jest użyty?
- Czy jest formułowy czy unikalny?
- Oceń jakość wzorca: 1-10

**Krok 3: Skuteczność Mechanizmu**
- Jak dobrze mechanizm działa?
- Czy jest nadużywany czy świeży?
- Oceń skuteczność mechanizmu: 1-10

**Krok 4: Replikowalność**
- Czy ten mechanizm mógłby działać z inną treścią?
- Czy jest zależny od treści czy uniwersalny?
- Oceń replikowalność: 1-10

**Format Wyjścia (JSON):**
{{
  "core_mechanism": "gra_słów / absurd / timing / struktura / inne",
  "structural_pattern": "opis wzorca",
  "mechanism_clarity": 1-10,
  "mechanism_effectiveness": 1-10,
  "replicability": 1-10,
  "reverse_engineering_score": 1-10
}}

Teraz przeanalizuj następujący żart:

{joke_text}"""


# Mapowanie teorii → prompty
THEORY_PROMPTS = {
    'setup_punchline': SETUP_PUNCHLINE_PROMPT,
    'incongruity': INCONGRUITY_PROMPT,
    'semantic_shift': SEMANTIC_SHIFT_PROMPT,
    'timing': TIMING_PROMPT,
    'absurd_escalation': ABSURD_ESCALATION_PROMPT,
    'psychoanalysis': PSYCHOANALYSIS_PROMPT,
    'archetype': ARCHETYPE_PROMPT,
    'humor_atoms': HUMOR_ATOMS_PROMPT,
    'reverse_engineering': REVERSE_ENGINEERING_PROMPT,
}

