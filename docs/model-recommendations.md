# Rekomendacje modeli Ollama dla zadań Waldus

## 🎯 Wymagania zadania

- ✅ **Strukturyzowane odpowiedzi JSON** - złożone formaty z wieloma kategoriami
- ✅ **Język polski** - wysokiej jakości odpowiedzi po polsku
- ✅ **Kreatywność i sarkazm** - inteligentny humor, przewrotność
- ✅ **Precyzja** - dokładne przestrzeganie formatu i wymagań

## 📊 Porównanie modeli dla polskiego + JSON

### ⭐⭐⭐⭐⭐ Najlepsze opcje

#### 1. **Qwen2.5 7B/14B** (REKOMENDOWANE dla polskiego)

**Zalety:**
- ✅ **Doskonały dla polskiego** - trenowany na dużym korpusie polskich tekstów
- ✅ **Świetny JSON** - bardzo dobre przestrzeganie formatów
- ✅ **Kreatywność** - dobry balans między precyzją a kreatywnością
- ✅ **Wielkość:** 7B Q4 (~4.5GB) lub 14B Q4 (~8GB)

**Dostępne wersje:**
```bash
ollama pull qwen2.5:7b      # 7B - szybki, dobry dla RTX 3060
ollama pull qwen2.5:14b      # 14B - lepszy, ale wolniejszy
ollama pull qwen2.5:32b      # 32B - najlepszy, ale wymaga dużo VRAM
```

**Dla RTX 3060:** `qwen2.5:7b` lub `qwen2.5:14b` (jeśli zmieści się w 12GB)

#### 2. **Aya 23 8B/13B** (NAJLEPSZY dla polskiego)

**Zalety:**
- ✅ **Najlepszy dla polskiego** - specjalnie trenowany dla 23 języków w tym polskiego
- ✅ **Dobry JSON** - solidne przestrzeganie formatów
- ✅ **Wielojęzyczność** - native support dla polskiego

**Dostępne wersje:**
```bash
ollama pull aya:8b           # 8B - dobry balans
ollama pull aya:13b          # 13B - lepszy, ale wolniejszy
```

**Dla RTX 3060:** `aya:8b` (idealny) lub `aya:13b` (jeśli zmieści się)

#### 3. **Llama 3.1 8B** (obecny - dobry, ale słabszy polski)

**Zalety:**
- ✅ **Doskonały JSON** - bardzo dobre przestrzeganie formatów
- ✅ **Kreatywność** - dobry balans
- ⚠️ **Polski** - działa, ale nie jest specjalizowany

**Wady:**
- ⚠️ Czasem gubi się w polskim (mieszanie języków)
- ⚠️ Słabsze zrozumienie polskich kontekstów kulturowych

### ⭐⭐⭐⭐ Dobre opcje

#### 4. **Mistral 7B**

**Zalety:**
- ✅ Dobry JSON
- ✅ Średni polski (lepszy niż Llama 3.1)
- ✅ Szybki

**Wady:**
- ⚠️ Nie specjalizowany dla polskiego

#### 5. **Solar 10.7B**

**Zalety:**
- ✅ Dobry dla polskiego
- ✅ Dobry JSON
- ✅ Kreatywność

**Wady:**
- ⚠️ Większy rozmiar (może być na granicy dla RTX 3060)

### ⭐⭐⭐ Średnie opcje

#### 6. **Gemma 2 9B**

**Zalety:**
- ✅ Dobry JSON
- ⚠️ Średni polski

**Wady:**
- ⚠️ Słabszy dla polskiego niż Qwen/Aya

## 🏆 Finalna rekomendacja

### Dla zadania Waldus (polski + JSON + kreatywność):

**1. Qwen2.5 7B** ⭐⭐⭐⭐⭐
```bash
ollama pull qwen2.5:7b
```
- Najlepszy balans jakości polskiego i JSON
- Zmieści się w RTX 3060 (12GB)
- Szybki (~30-40 tok/s)

**2. Aya 8B** ⭐⭐⭐⭐⭐
```bash
ollama pull aya:8b
```
- Najlepszy dla polskiego
- Dobry JSON
- Zmieści się w RTX 3060

**3. Qwen2.5 14B** ⭐⭐⭐⭐ (jeśli zmieści się)
```bash
ollama pull qwen2.5:14b
```
- Lepszy niż 7B, ale wolniejszy
- Wymaga ~8-9GB VRAM

### Porównanie dla Twojego zadania

| Model | Polski | JSON | Kreatywność | Wydajność (RTX 3060) | Rekomendacja |
|-------|--------|------|-------------|---------------------|--------------|
| **Qwen2.5 7B** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ~30-40 tok/s | ✅ **NAJLEPSZY** |
| **Aya 8B** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ~25-35 tok/s | ✅ **NAJLEPSZY dla polskiego** |
| **Llama 3.1 8B** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ~30-50 tok/s | ⚠️ Obecny - słabszy polski |
| **Mistral 7B** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ~35-55 tok/s | ⚠️ Średni polski |
| **Qwen2.5 14B** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ~20-30 tok/s | ✅ Jeśli zmieści się |

## 🚀 Szybki test

Przetestuj różne modele:

```bash
# Pobierz Qwen2.5 7B
ollama pull qwen2.5:7b

# Edytuj scripts/ask_ollama.py:
MODEL = "qwen2.5:7b"

# Uruchom test
python scripts/ask_ollama.py
```

## 💡 Wskazówki

1. **Dla najlepszego polskiego:** Aya 8B lub Qwen2.5 7B
2. **Dla najlepszego JSON:** Qwen2.5 lub Llama 3.1
3. **Dla balansu:** Qwen2.5 7B (najlepszy kompromis)
4. **Dla szybkości:** Qwen2.5 7B lub Mistral 7B

## 📝 Uwagi

- Llama 3.1 8B (obecny) jest dobry, ale polski może być słabszy
- Qwen2.5 ma najlepszy balans jakości polskiego i JSON
- Aya jest najlepszy dla polskiego, ale może być nieco słabszy w JSON
- Wszystkie modele 7B-8B zmieszczą się w RTX 3060 12GB

---

**Rekomendacja:** Zacznij od **Qwen2.5 7B** - najlepszy balans dla Twojego przypadku użycia! 🎯

