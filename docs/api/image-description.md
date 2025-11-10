# API Reference: Image Description 🖼️

**← Powrót do:** [waldus-api WL-2 Faza 1](../../../waldus-api/docs/features/WL-2-faza-1-szybkie-wygrane.md)

---

## 📋 Informacje podstawowe

**Base URL:** `http://localhost:5001` (domyślnie)  
**Protokół:** HTTP/1.1  
**Content-Type:** `application/json`  
**Wersja API:** 1.0

**Model:** BLIP (Bootstrapping Language-Image Pre-training)  
**Implementacja:** `src/image/describe.py`

---

## 🌐 Endpoints

### 1. POST /describe

Generuje opis obrazu w języku naturalnym na podstawie URL obrazka.

#### Request

**Method:** `POST`  
**Path:** `/describe`  
**Content-Type:** `application/json`

**Body Schema:**

```json
{
  "image_url": "string (required)",
  "max_length": "integer (optional, default: 50)",
  "language": "string (optional, default: 'en')"
}
```

**Parametry:**

| Parametr | Typ | Wymagany | Default | Opis |
|----------|-----|----------|---------|------|
| `image_url` | string | Tak | - | URL obrazka do opisania |
| `max_length` | integer | Nie | 50 | Maksymalna długość opisu (w tokenach) |
| `language` | string | Nie | `en` | Język opisu (`en` lub `pl`) |

**Przykład:**

```json
{
  "image_url": "https://example.com/image.jpg",
  "max_length": 50,
  "language": "en"
}
```

#### Response

**Status:** `200 OK`

**Body Schema:**

```json
{
  "success": "boolean",
  "description": "string",
  "image_url": "string",
  "model": "string",
  "processing_time_ms": "float"
}
```

**Przykład:**

```json
{
  "success": true,
  "description": "A white cat sitting on a wooden chair, looking at the camera with bright green eyes",
  "image_url": "https://example.com/image.jpg",
  "model": "blip-base",
  "processing_time_ms": 342.5
}
```

#### Error Responses

**400 Bad Request - Brak URL:**

```json
{
  "success": false,
  "error": "Missing required field: image_url"
}
```

**400 Bad Request - Nieprawidłowy URL:**

```json
{
  "success": false,
  "error": "Invalid image URL"
}
```

**500 Internal Server Error:**

```json
{
  "success": false,
  "error": "Failed to download image: [details]"
}
```

**500 Internal Server Error:**

```json
{
  "success": false,
  "error": "Failed to generate description: [details]"
}
```

#### cURL Example

```bash
curl -X POST http://localhost:5001/describe \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/cat.jpg",
    "max_length": 50
  }'
```

#### PHP Example (waldus-api)

```php
use Illuminate\Support\Facades\Http;

class ImageDescriptionService
{
    private string $apiUrl;
    
    public function __construct()
    {
        $this->apiUrl = config('services.image_description.api_url', 'http://localhost:5001');
    }
    
    public function describeViaApi(string $imageUrl, int $maxLength = 50): ?string
    {
        try {
            $response = Http::timeout(30)->post($this->apiUrl . '/describe', [
                'image_url' => $imageUrl,
                'max_length' => $maxLength,
                'language' => 'en',
            ]);
            
            if ($response->successful()) {
                $data = $response->json();
                
                if ($data['success'] ?? false) {
                    Log::info('ImageDescriptionService: API description generated', [
                        'image_url' => $imageUrl,
                        'description' => $data['description'],
                        'processing_time_ms' => $data['processing_time_ms'] ?? 0,
                    ]);
                    
                    return $data['description'];
                }
            }
            
            Log::warning('ImageDescriptionService: API request failed', [
                'status' => $response->status(),
                'body' => $response->body(),
            ]);
            
            return null;
            
        } catch (\Exception $e) {
            Log::error('ImageDescriptionService: API error', [
                'error' => $e->getMessage(),
            ]);
            return null;
        }
    }
}
```

---

### 2. GET /health

Sprawdza status API i dostępność modelu BLIP.

#### Request

**Method:** `GET`  
**Path:** `/health`  
**Query Parameters:** None

#### Response

**Status:** `200 OK`

**Body Schema:**

```json
{
  "status": "string",
  "model_loaded": "boolean",
  "model_name": "string",
  "uptime_seconds": "float"
}
```

**Przykład:**

```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_name": "blip-base",
  "uptime_seconds": 3600.5
}
```

#### cURL Example

```bash
curl http://localhost:5001/health
```

#### PHP Example

```php
$response = Http::get('http://localhost:5001/health');

if ($response->successful()) {
    $health = $response->json();
    
    if ($health['model_loaded'] ?? false) {
        echo "AI Local Core is ready!\n";
    }
}
```

---

## ⚙️ Konfiguracja

### Zmienne środowiskowe

**Plik:** `.env` (w ai-local-core)

```env
# Flask server
FLASK_ENV=production
FLASK_HOST=0.0.0.0
FLASK_PORT=5001

# BLIP model
BLIP_MODEL_NAME=Salesforce/blip-image-captioning-base
BLIP_MAX_LENGTH=50

# Cache
BLIP_CACHE_DIR=/Users/piotradamczyk/.cache/huggingface
```

### Konfiguracja w waldus-api

**Plik:** `config/services.php`

```php
'image_description' => [
    'mode' => env('IMAGE_DESCRIPTION_MODE', 'api'), // 'api' lub 'local'
    'api_url' => env('IMAGE_DESCRIPTION_API_URL', 'http://localhost:5001'),
    'timeout' => env('IMAGE_DESCRIPTION_TIMEOUT', 30),
    'max_length' => env('IMAGE_DESCRIPTION_MAX_LENGTH', 50),
],
```

**Plik:** `.env` (w waldus-api)

```env
IMAGE_DESCRIPTION_MODE=api
IMAGE_DESCRIPTION_API_URL=http://localhost:5001
IMAGE_DESCRIPTION_TIMEOUT=30
IMAGE_DESCRIPTION_MAX_LENGTH=50
```

---

## 🔄 Integracja z waldus-api

### Architektura

```
┌─────────────────────┐
│   waldus-api        │
│                     │
│  ImageDescription   │
│     Service         │
│                     │
│  1. Sprawdź cache   │──> MemoryService
│  2. Jeśli brak:     │    (database cache)
│     wywołaj API ────┼────────────┐
│  3. Zapisz cache    │            │
└─────────────────────┘            │
                                   │ HTTP POST /describe
                                   ▼
                         ┌──────────────────┐
                         │  ai-local-core   │
                         │                  │
                         │  BLIP Model      │
                         │  (GPU/CPU)       │
                         │                  │
                         │  Flask API       │
                         └──────────────────┘
```

### Workflow

1. **Bot** zbiera obrazki ze strony (`page_data.images[]`)
2. **PromptBuilder** wywołuje `MemoryService::getImageDescription()`
3. **MemoryService** sprawdza cache w bazie danych
4. Jeśli brak w cache → **ImageDescriptionService::describeViaApi()**
5. **ai-local-core** generuje opis używając BLIP
6. **MemoryService** zapisuje opis do cache
7. **PromptBuilder** używa opisu w promptcie dla LLM

### Przykład użycia

```php
// app/Services/PromptBuilder.php

public function buildPromptForPage(array $pageData): array
{
    $waldusUuid = $pageData['session_uuid'];
    $images = $pageData['images'] ?? [];
    
    $imageDescriptions = [];
    
    foreach ($images as $image) {
        // Sprawdź cache
        $description = $this->memoryService->getImageDescription($waldusUuid, $image['url']);
        
        if (!$description) {
            // Cache miss - wygeneruj opis
            $description = $this->imageDescriptionService->describeViaApi($image['url']);
            
            if ($description) {
                // Zapisz do cache
                $this->memoryService->saveImageDescription($waldusUuid, $image['url'], $description);
            }
        }
        
        if ($description) {
            $imageDescriptions[] = [
                'url' => $image['url'],
                'alt' => $image['alt'] ?? '',
                'description' => $description,
            ];
        }
    }
    
    // Dodaj opisy obrazków do promptu
    $prompt = [
        'messages' => [
            [
                'role' => 'user',
                'content' => "Strona zawiera następujące obrazki:\n" .
                             implode("\n", array_map(
                                 fn($img) => "- {$img['description']} (alt: {$img['alt']})",
                                 $imageDescriptions
                             ))
            ]
        ]
    ];
    
    return $prompt;
}
```

---

## 🚨 Ważne ograniczenia

### ⚠️ Sekwencyjne przetwarzanie

**KRYTYCZNE:** `ai-local-core` może przetwarzać tylko **jedno żądanie na raz**.

**Dlaczego?**
- Model BLIP jest załadowany w pamięci GPU/CPU
- Równoległe żądania mogłyby spowodować błędy CUDA out-of-memory
- Potencjalne konflikty w dostępie do modelu

**Rozwiązanie:**
- Wszystkie żądania do `/describe` **MUSZĄ** być kolejkowane w `llm_jobs`
- Provider: `ai-local-core-image`
- QueueService sprawdza czy `ai-local-core` jest zajęty przed wysłaniem żądania
- Maksymalnie 1 aktywny job (`pending` lub `processing`) dla `ai-local-core-*` providerów

**Implementacja w waldus-api:**

```php
// app/Services/QueueService.php

public function isProviderBusy(string $provider): bool
{
    // Dla ai-local-core: sprawdź wszystkie warianty
    if (str_starts_with($provider, 'ai-local-core')) {
        $activeJobs = LlmJob::where(function ($query) {
            $query->where('provider', 'LIKE', 'ai-local-core%');
        })
        ->whereIn('status', ['pending', 'processing'])
        ->count();
        
        return $activeJobs > 0; // Zajęty jeśli JAKIKOLWIEK job jest aktywny
    }
    
    // Dla innych providerów
    return LlmJob::where('provider', $provider)
        ->whereIn('status', ['pending', 'processing'])
        ->exists();
}
```

---

## 📊 Wydajność

### Czasy przetwarzania

| Typ obrazka | Rozmiar | GPU (RTX 3060) | CPU (Ryzen 5) |
|-------------|---------|----------------|---------------|
| Mały (< 500KB) | 640x480 | ~200-300ms | ~1-2s |
| Średni (500KB-2MB) | 1920x1080 | ~300-500ms | ~2-4s |
| Duży (> 2MB) | 4K+ | ~500-800ms | ~4-8s |

### Optymalizacja

1. **Cache w bazie danych** - unikaj duplikacji generowania opisów
2. **Priorytetyzacja** - obrazki on-demand mają wyższy priorytet
3. **Batch processing** - grupuj żądania (jeśli możliwe)
4. **Timeout** - ustaw timeout 30s dla API calls

---

## 🧪 Testowanie

### Test manualny

```bash
# Test basic
curl -X POST http://localhost:5001/describe \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba"
  }'

# Test z długim opisem
curl -X POST http://localhost:5001/describe \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba",
    "max_length": 100
  }'
```

### Test jednostkowy

**Plik:** `tests/unit/test_image_describe.py`

```python
import pytest
from src.image.describe import describe_image

def test_describe_image():
    result = describe_image(
        'https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba',
        max_length=50
    )
    
    assert result is not None
    assert len(result) > 0
    assert 'cat' in result.lower()  # Jeśli to zdjęcie kota
```

---

## 📝 Changelog

### v1.0 (Obecna)

- ✅ Endpoint `/describe` dla generowania opisów
- ✅ Model BLIP-base
- ✅ Health check endpoint
- ✅ Obsługa timeoutów
- ✅ Logowanie requestów

### Planowane

- ⏳ Tłumaczenie opisów na polski
- ⏳ Multi-język support (użycie `language` parametru)
- ⏳ Batch processing (wiele obrazków na raz)
- ⏳ Upgrade do BLIP-2 (lepsza jakość)

---

## 🔗 Powiązane dokumenty

- [waldus-api: ImageDescriptionService](../../../waldus-api/app/Services/ImageDescriptionService.php)
- [waldus-api: MemoryService](../../../waldus-api/app/Services/MemoryService.php)
- [WL-2 Faza 1: Integracja z ai-local-core](../../../waldus-api/docs/features/WL-2-faza-1-szybkie-wygrane.md)

---

**Status:** 🟢 Dokumentacja kompletna  
**Ostatnia aktualizacja:** 2025-11-10

