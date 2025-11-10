# API Reference: Provider Selection 🔄

**← Powrót do:** [WL-2: Provider Selection ML](../features/WL-2-provider-selection-ml.md)

---

## 📋 Informacje podstawowe

**Base URL:** `http://localhost:5001` (domyślnie)  
**Protokół:** HTTP/1.1  
**Content-Type:** `application/json`  
**Wersja API:** 1.0

---

## 🌐 Endpoints

### 1. POST /select-provider

Wybiera najlepszego providera LLM na podstawie ML modelu (Multi-Armed Bandit - Thompson Sampling).

#### Request

**Method:** `POST`  
**Path:** `/select-provider`  
**Content-Type:** `application/json`

**Body Schema:**

```json
{
  "waldus_uuid": "string (required)",
  "user_context": {
    "age": "integer (optional)",
    "humor_style": "string (optional)",
    "engagement_level": "string (optional)",
    "communication_style": "string (optional)"
  },
  "prompt_context": {
    "page_type": "string (optional)",
    "complexity": "integer (optional)",
    "has_images": "boolean (optional)"
  },
  "provider_metrics": {
    "anthropic": {
      "avg_latency_ms": "float",
      "success_rate": "float (0-1)",
      "avg_rating": "float (1-5)"
    },
    "openai": { "..." },
    "groq": { "..." }
  },
  "priority": "integer (0-100, default: 10)"
}
```

**Przykład:**

```json
{
  "waldus_uuid": "abc-123-def-456",
  "user_context": {
    "age": 25,
    "humor_style": "sarcastic",
    "engagement_level": "high"
  },
  "prompt_context": {
    "page_type": "blog",
    "complexity": 150,
    "has_images": true
  },
  "provider_metrics": {
    "anthropic": {
      "avg_latency_ms": 500,
      "success_rate": 0.98,
      "avg_rating": 4.5
    },
    "openai": {
      "avg_latency_ms": 800,
      "success_rate": 0.95,
      "avg_rating": 4.2
    },
    "groq": {
      "avg_latency_ms": 200,
      "success_rate": 0.92,
      "avg_rating": 4.0
    }
  },
  "priority": 0
}
```

#### Response

**Status:** `200 OK`

**Body Schema:**

```json
{
  "provider": "string",
  "confidence": "float (0-1)",
  "reason": "string"
}
```

**Przykład:**

```json
{
  "provider": "anthropic",
  "confidence": 0.85,
  "reason": "Thompson Sampling confidence: 85%"
}
```

#### Error Responses

**400 Bad Request:**

```json
{
  "error": "Missing required field: waldus_uuid"
}
```

**500 Internal Server Error:**

```json
{
  "error": "ML model error: [details]"
}
```

#### cURL Example

```bash
curl -X POST http://localhost:5001/select-provider \
  -H "Content-Type: application/json" \
  -d '{
    "waldus_uuid": "abc-123",
    "user_context": {"age": 25, "humor_style": "sarcastic"},
    "prompt_context": {"page_type": "blog", "complexity": 150},
    "provider_metrics": {
      "anthropic": {"avg_latency_ms": 500, "success_rate": 0.98},
      "openai": {"avg_latency_ms": 800, "success_rate": 0.95}
    },
    "priority": 10
  }'
```

#### PHP Example

```php
use Illuminate\Support\Facades\Http;

$response = Http::timeout(2)->post('http://localhost:5001/select-provider', [
    'waldus_uuid' => 'abc-123',
    'user_context' => [
        'age' => 25,
        'humor_style' => 'sarcastic',
    ],
    'prompt_context' => [
        'page_type' => 'blog',
        'complexity' => 150,
    ],
    'provider_metrics' => [
        'anthropic' => [
            'avg_latency_ms' => 500,
            'success_rate' => 0.98,
        ],
        'openai' => [
            'avg_latency_ms' => 800,
            'success_rate' => 0.95,
        ],
    ],
    'priority' => 10,
]);

if ($response->successful()) {
    $provider = $response->json('provider');
    $confidence = $response->json('confidence');
}
```

---

### 2. POST /update-reward

Aktualizuje statystyki Multi-Armed Bandit po otrzymaniu feedbacku od użytkownika.

#### Request

**Method:** `POST`  
**Path:** `/update-reward`  
**Content-Type:** `application/json`

**Body Schema:**

```json
{
  "waldus_uuid": "string (required)",
  "provider": "string (required)",
  "reward": "float (0-1, required)"
}
```

**Przykład:**

```json
{
  "waldus_uuid": "abc-123-def-456",
  "provider": "anthropic",
  "reward": 0.875
}
```

**Mapowanie rating → reward:**

```
Rating 1 → reward 0.00
Rating 2 → reward 0.25
Rating 3 → reward 0.50
Rating 4 → reward 0.75
Rating 5 → reward 1.00

Formula: reward = (rating - 1) / 4
```

#### Response

**Status:** `200 OK`

**Body Schema:**

```json
{
  "success": "boolean",
  "updated_stats": {
    "[provider_name]": {
      "mean": "float (0-1)",
      "alpha": "float",
      "beta": "float",
      "total_trials": "integer"
    }
  }
}
```

**Przykład:**

```json
{
  "success": true,
  "updated_stats": {
    "anthropic": {
      "mean": 0.85,
      "alpha": 34.875,
      "beta": 6.25,
      "total_trials": 42
    },
    "openai": {
      "mean": 0.78,
      "alpha": 28.3,
      "beta": 8.1,
      "total_trials": 36
    }
  }
}
```

#### Error Responses

**400 Bad Request:**

```json
{
  "error": "Missing required fields"
}
```

**400 Bad Request:**

```json
{
  "error": "Reward must be between 0 and 1"
}
```

#### cURL Example

```bash
curl -X POST http://localhost:5001/update-reward \
  -H "Content-Type: application/json" \
  -d '{
    "waldus_uuid": "abc-123",
    "provider": "anthropic",
    "reward": 0.875
  }'
```

#### PHP Example

```php
// Po otrzymaniu ratingu użytkownika (1-5)
$rating = 5;
$reward = ($rating - 1) / 4; // Normalize to 0-1

Http::timeout(2)->post('http://localhost:5001/update-reward', [
    'waldus_uuid' => $waldusUuid,
    'provider' => $provider,
    'reward' => $reward,
]);
```

---

### 3. GET /provider-stats

Zwraca statystyki wszystkich providerów (alpha, beta, mean, total trials).

#### Request

**Method:** `GET`  
**Path:** `/provider-stats`  
**Query Parameters:** None

#### Response

**Status:** `200 OK`

**Body Schema:**

```json
{
  "[provider_name]": {
    "mean": "float (0-1)",
    "alpha": "float",
    "beta": "float",
    "total_trials": "integer"
  }
}
```

**Przykład:**

```json
{
  "anthropic": {
    "mean": 0.85,
    "alpha": 34.5,
    "beta": 6.2,
    "total_trials": 40
  },
  "openai": {
    "mean": 0.78,
    "alpha": 28.3,
    "beta": 8.1,
    "total_trials": 36
  },
  "groq": {
    "mean": 0.72,
    "alpha": 22.1,
    "beta": 9.5,
    "total_trials": 31
  },
  "ollama": {
    "mean": 0.65,
    "alpha": 15.2,
    "beta": 8.3,
    "total_trials": 23
  },
  "deepseek": {
    "mean": 0.70,
    "alpha": 18.5,
    "beta": 7.9,
    "total_trials": 26
  }
}
```

#### Interpretacja statystyk

**mean:** Średnia sukcesu providera (0-1)
- Wyższa wartość = lepszy provider
- Obliczana jako: `alpha / (alpha + beta)`

**alpha:** Suma nagród (sukcesów)
- Wyższa wartość = więcej pozytywnych feedbacków

**beta:** Suma kar (porażek)
- Wyższa wartość = więcej negatywnych feedbacków

**total_trials:** Liczba feedbacków
- `alpha + beta - 2` (odejmujemy uniform prior)

#### cURL Example

```bash
curl http://localhost:5001/provider-stats
```

#### PHP Example

```php
$response = Http::get('http://localhost:5001/provider-stats');

if ($response->successful()) {
    $stats = $response->json();
    
    foreach ($stats as $provider => $providerStats) {
        echo "Provider: $provider\n";
        echo "  Mean: " . $providerStats['mean'] . "\n";
        echo "  Trials: " . $providerStats['total_trials'] . "\n";
    }
}
```

---

## 🔒 Bezpieczeństwo

### Obecne

- **Brak autoryzacji** - API jest otwarte dla lokalnych requestów
- **Rate limiting** - Nie zaimplementowany

### Rekomendacje produkcyjne

1. **API Key Authentication:**

```python
from functools import wraps
from flask import request

API_KEY = os.getenv('AI_LOCAL_CORE_API_KEY')

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        key = request.headers.get('X-API-Key')
        if key != API_KEY:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/select-provider', methods=['POST'])
@require_api_key
def select_provider():
    # ...
```

2. **Rate Limiting:**

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.headers.get('X-API-Key'),
    default_limits=["100 per minute"]
)

@app.route('/select-provider', methods=['POST'])
@limiter.limit("10 per second")
def select_provider():
    # ...
```

---

## 📊 Monitoring i logi

### Logowanie requestów

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@app.route('/select-provider', methods=['POST'])
def select_provider():
    data = request.json
    
    logging.info(f"SELECT_PROVIDER request from {data.get('waldus_uuid')}")
    # ...
    logging.info(f"Selected provider: {provider}, confidence: {confidence}")
```

### Metryki

**Liczba requestów per endpoint:**
- `/select-provider` - liczba wyborów providerów
- `/update-reward` - liczba feedbacków
- `/provider-stats` - liczba zapytań o statystyki

**Średni czas odpowiedzi:**
- Powinien być < 100ms dla `/select-provider`
- Powinien być < 50ms dla `/update-reward`

---

## 🧪 Testowanie API

### Testy jednostkowe

**Plik:** `tests/integration/test_api_provider_selection.py`

```python
import pytest
from src.api.server import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_select_provider_success(client):
    response = client.post('/select-provider', json={
        'waldus_uuid': 'test-uuid',
        'user_context': {'age': 25},
        'prompt_context': {},
        'provider_metrics': {},
        'priority': 10
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'provider' in data
    assert 'confidence' in data

def test_update_reward_success(client):
    response = client.post('/update-reward', json={
        'waldus_uuid': 'test-uuid',
        'provider': 'anthropic',
        'reward': 0.875
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True

def test_get_provider_stats(client):
    response = client.get('/provider-stats')
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'anthropic' in data
    assert 'mean' in data['anthropic']
```

### Testy integracyjne (z waldus-api)

```bash
# Test end-to-end z waldus-api
curl -X POST http://localhost:8000/api/bot/plan \
  -H "Content-Type: application/json" \
  -d '{"session_uuid": "test", "page_signature": "test"}'

# Sprawdź czy ML API zostało wywołane
tail -f /Users/piotradamczyk/Projects/Octadecimal/ai-local-core/logs/app.log
```

---

## 📝 Changelog

### v1.0 (2025-11-10)

- ✅ Dodano endpoint `/select-provider`
- ✅ Dodano endpoint `/update-reward`
- ✅ Dodano endpoint `/provider-stats`
- ✅ Zaimplementowano Multi-Armed Bandit (Thompson Sampling)
- ✅ Dodano persystencję stanu do JSON file

### Planowane

- ⏳ API Key authentication
- ⏳ Rate limiting
- ⏳ XGBoost model (jako alternatywa dla MAB)
- ⏳ Webhook notifications

---

**Status:** 🟢 Dokumentacja kompletna  
**Ostatnia aktualizacja:** 2025-11-10

