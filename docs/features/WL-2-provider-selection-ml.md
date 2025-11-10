# WL-2: Provider Selection ML 🤖

**← Powrót do:** [waldus-api WL-2 Faza 4](../../../waldus-api/docs/features/WL-2-faza-4-provider-selection.md)

---

## 📋 Informacje podstawowe

**Repozytorium:** `ai-local-core`  
**Czas implementacji:** 1-2 tygodnie  
**Priorytet:** ⭐⭐ (niski, ale duży potencjał)  
**Zależności:** Zebranie danych (min. 1000+ interakcji), waldus-api Faza 4.1

---

## 🎯 Cel

Zastosowanie Machine Learning do inteligentnego wyboru najlepszego providera LLM na podstawie:
- Historycznych metryk wydajności
- Ocen użytkowników
- Kontekstu użytkownika i promptu
- Samonauki w czasie rzeczywistym (Reinforcement Learning)

---

## 🏗️ Architektura

### Umieszczenie ML w ai-local-core

**Uzasadnienie:**
- ✅ **Lepsze biblioteki ML:** Python ma bogaty ekosystem (scikit-learn, PyTorch, TensorFlow, XGBoost)
- ✅ **Już istniejąca infrastruktura:** Flask API, łatwe dodanie endpointu `/select-provider`
- ✅ **Izolacja:** ML model nie obciąża głównej aplikacji PHP
- ✅ **Skalowanie:** Można uruchomić osobny serwer ML bez wpływu na waldus-api
- ✅ **Trening modelu:** Łatwiejsze w Pythonie (pandas, numpy, scikit-learn)

### Komunikacja

```
┌─────────────────┐         HTTP POST          ┌──────────────────┐
│   waldus-api    │  ──────────────────────>   │  ai-local-core   │
│                 │                             │                  │
│ ProviderSelection│  {                         │   ML Model       │
│    Service      │    waldus_uuid,             │  (Python)        │
│    (PHP)        │    user_context,            │                  │
│                 │    provider_metrics,        │  /select-provider│
│                 │    priority                 │  /update-reward  │
│                 │  }                          │                  │
│                 │                             │                  │
│                 │  <──────────────────────   │                  │
│                 │  {                         │                  │
│                 │    provider: "anthropic",  │                  │
│                 │    confidence: 0.85        │                  │
│                 │  }                         │                  │
└─────────────────┘                             └──────────────────┘
```

---

## 📦 Struktura projektu

```
ai-local-core/
├── src/
│   ├── ml/                          # NOWY MODUŁ
│   │   ├── __init__.py
│   │   ├── provider_selector.py    # Główna logika ML
│   │   ├── features.py              # Feature engineering
│   │   ├── models/                  # Zapisane modele
│   │   │   └── bandit_state.json   # Stan Multi-Armed Bandit
│   │   └── training/                # Skrypty treningowe
│   │       ├── train_bandit.py
│   │       ├── train_xgboost.py
│   │       └── evaluate.py
│   └── api/
│       └── server.py                # Flask API (rozszerzyć)
```

---

## 🤖 Propozycje modeli ML

### Opcja A: Reinforcement Learning (Multi-Armed Bandit) ⭐ REKOMENDOWANE

**Algorytm:** Thompson Sampling

**Zalety:**
- ✅ Uczy się w czasie rzeczywistym
- ✅ Nie wymaga danych treningowych
- ✅ Automatycznie adaptuje się do zmian
- ✅ Prosty w implementacji

**Wady:**
- ❌ Wymaga czasu na "rozgrzanie"
- ❌ Może eksperymentować

**Implementacja:**

```python
# src/ml/provider_selector.py

import numpy as np
from scipy.stats import beta
import json
import os
from typing import Dict, Tuple

class RLProviderSelector:
    """
    Multi-Armed Bandit z Thompson Sampling dla wyboru providera
    """
    
    def __init__(self, state_file='src/ml/models/bandit_state.json'):
        self.state_file = state_file
        
        # Dla każdego providera: alpha (sukcesy), beta (porażki)
        self.arms = {
            'anthropic': {'alpha': 1.0, 'beta': 1.0},  # Uniform prior
            'openai': {'alpha': 1.0, 'beta': 1.0},
            'groq': {'alpha': 1.0, 'beta': 1.0},
            'ollama': {'alpha': 1.0, 'beta': 1.0},
            'deepseek': {'alpha': 1.0, 'beta': 1.0},
        }
        
        # Wczytaj zapisany stan
        self.load_state()
    
    def select_provider(self, waldus_uuid: str, context: dict = None) -> Tuple[str, float]:
        """
        Thompson Sampling: wybierz providera na podstawie beta distribution
        
        Returns:
            (provider_name, confidence)
        """
        samples = {}
        
        for provider, params in self.arms.items():
            # Próbkuj z beta distribution
            sample = beta.rvs(params['alpha'], params['beta'])
            samples[provider] = sample
        
        # Wybierz providera z najwyższym sample
        selected = max(samples, key=samples.get)
        confidence = samples[selected]
        
        return selected, confidence
    
    def update_reward(
        self,
        waldus_uuid: str,
        provider: str,
        reward: float  # 0-1 (normalizowana ocena użytkownika)
    ):
        """
        Aktualizuj statystyki po otrzymaniu feedbacku
        reward: 0-1 (np. (rating - 1) / 4 dla rating 1-5)
        """
        if provider not in self.arms:
            return
        
        # Aktualizuj alpha (sukcesy) i beta (porażki)
        # reward bliskie 1.0 → sukces, bliskie 0.0 → porażka
        self.arms[provider]['alpha'] += reward
        self.arms[provider]['beta'] += (1 - reward)
        
        # Zapisz stan
        self.save_state()
    
    def get_stats(self) -> Dict:
        """
        Zwraca statystyki dla wszystkich providerów
        """
        stats = {}
        
        for provider, params in self.arms.items():
            # Średnia beta distribution = alpha / (alpha + beta)
            mean = params['alpha'] / (params['alpha'] + params['beta'])
            
            # Liczba prób
            total_trials = params['alpha'] + params['beta'] - 2  # Odejmij priory
            
            stats[provider] = {
                'mean': mean,
                'alpha': params['alpha'],
                'beta': params['beta'],
                'total_trials': total_trials,
            }
        
        return stats
    
    def save_state(self):
        """Zapisz stan do pliku"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        
        with open(self.state_file, 'w') as f:
            json.dump(self.arms, f, indent=2)
    
    def load_state(self):
        """Wczytaj stan z pliku"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    saved_arms = json.load(f)
                    
                # Aktualizuj tylko istniejące armes
                for provider, params in saved_arms.items():
                    if provider in self.arms:
                        self.arms[provider] = params
                        
            except Exception as e:
                print(f"Warning: Could not load state: {e}")
```

### Opcja B: XGBoost (Gradient Boosting)

**Dla zaawansowanego użycia po zebraniu danych (1000+ interakcji)**

```python
# src/ml/training/train_xgboost.py

import xgboost as xgb
import pandas as pd
from sklearn.model_selection import train_test_split
import joblib

class XGBoostProviderSelector:
    """
    XGBoost dla wyboru providera na podstawie zebranych danych
    """
    
    def __init__(self, model_path='src/ml/models/xgboost_provider.model'):
        self.model_path = model_path
        self.model = None
        self.load_model()
    
    def train(self, training_data: pd.DataFrame):
        """
        Trenuj model na zebranych danych
        
        training_data columns:
        - provider (target)
        - avg_latency_ms
        - success_rate
        - avg_rating
        - user_age
        - user_humor_style
        - prompt_complexity
        - priority
        """
        # Przygotuj features
        X = training_data.drop(['provider'], axis=1)
        y = training_data['provider'].astype('category').cat.codes
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train
        self.model = xgb.XGBClassifier(
            objective='multi:softmax',
            num_class=len(training_data['provider'].unique()),
            max_depth=5,
            learning_rate=0.1,
            n_estimators=100
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        accuracy = self.model.score(X_test, y_test)
        print(f"Model accuracy: {accuracy:.2%}")
        
        # Save
        self.save_model()
    
    def predict(self, features: dict) -> Tuple[str, float]:
        """
        Przewiduj najlepszego providera
        """
        if self.model is None:
            return 'anthropic', 0.5  # Default
        
        # Przygotuj features
        X = pd.DataFrame([features])
        
        # Predict
        provider_code = self.model.predict(X)[0]
        proba = self.model.predict_proba(X)[0]
        
        # Map code to provider name
        provider_names = ['anthropic', 'openai', 'groq', 'ollama', 'deepseek']
        provider = provider_names[provider_code]
        confidence = proba[provider_code]
        
        return provider, confidence
    
    def save_model(self):
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
    
    def load_model(self):
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
```

---

## 🌐 API Endpoints

### Dokumentacja API: [provider-selection.md](../api/provider-selection.md)

### POST /select-provider

**Wybiera najlepszego providera**

**Request:**
```json
{
  "waldus_uuid": "abc-123",
  "user_context": {
    "age": 25,
    "humor_style": "sarcastic",
    "engagement_level": "high"
  },
  "prompt_context": {
    "page_type": "blog",
    "complexity": 150
  },
  "provider_metrics": {
    "anthropic": {"avg_latency_ms": 500, "success_rate": 0.98},
    "openai": {"avg_latency_ms": 800, "success_rate": 0.95}
  },
  "priority": 10
}
```

**Response:**
```json
{
  "provider": "anthropic",
  "confidence": 0.85,
  "reason": "Best combination of latency and historical success rate"
}
```

### POST /update-reward

**Aktualizuje statystyki po otrzymaniu feedbacku**

**Request:**
```json
{
  "waldus_uuid": "abc-123",
  "provider": "anthropic",
  "reward": 0.875
}
```

**Response:**
```json
{
  "success": true,
  "updated_stats": {
    "anthropic": {
      "mean": 0.85,
      "total_trials": 42
    }
  }
}
```

### GET /provider-stats

**Zwraca statystyki wszystkich providerów**

**Response:**
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
  }
}
```

---

## 🔧 Implementacja w Flask API

**Plik:** `src/api/server.py`

```python
from flask import Flask, request, jsonify
from src.ml.provider_selector import RLProviderSelector

app = Flask(__name__)

# Inicjalizuj selector
selector = RLProviderSelector()

@app.route('/select-provider', methods=['POST'])
def select_provider():
    """
    Wybiera najlepszego providera na podstawie ML modelu
    """
    data = request.json
    
    waldus_uuid = data.get('waldus_uuid')
    user_context = data.get('user_context', {})
    prompt_context = data.get('prompt_context', {})
    provider_metrics = data.get('provider_metrics', {})
    priority = data.get('priority', 10)
    
    # Wybierz providera
    provider, confidence = selector.select_provider(
        waldus_uuid,
        context={
            'user': user_context,
            'prompt': prompt_context,
            'metrics': provider_metrics,
            'priority': priority
        }
    )
    
    return jsonify({
        'provider': provider,
        'confidence': float(confidence),
        'reason': f'Thompson Sampling confidence: {confidence:.2%}'
    })

@app.route('/update-reward', methods=['POST'])
def update_reward():
    """
    Aktualizuje statystyki po otrzymaniu feedbacku
    """
    data = request.json
    
    waldus_uuid = data.get('waldus_uuid')
    provider = data.get('provider')
    reward = data.get('reward')  # 0-1
    
    if not all([waldus_uuid, provider, reward is not None]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Aktualizuj reward
    selector.update_reward(waldus_uuid, provider, reward)
    
    # Zwróć zaktualizowane statystyki
    stats = selector.get_stats()
    
    return jsonify({
        'success': True,
        'updated_stats': stats
    })

@app.route('/provider-stats', methods=['GET'])
def get_provider_stats():
    """
    Zwraca statystyki wszystkich providerów
    """
    stats = selector.get_stats()
    return jsonify(stats)

# Existing endpoints...
# /describe, /health, etc.
```

---

## 📦 Instalacja zależności

**Plik:** `requirements.txt`

```txt
# Existing dependencies
flask>=2.3.0
Pillow>=10.0.0
transformers>=4.30.0
torch>=2.0.0
requests>=2.31.0

# NEW: ML dependencies
scipy>=1.11.0
scikit-learn>=1.3.0
xgboost>=2.0.0
pandas>=2.0.0
numpy>=1.24.0
joblib>=1.3.0
```

**Instalacja:**

```bash
cd /Users/piotradamczyk/Projects/Octadecimal/ai-local-core
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🧪 Testy

**Plik:** `tests/unit/test_provider_selector.py`

```python
import pytest
from src.ml.provider_selector import RLProviderSelector

def test_select_provider():
    selector = RLProviderSelector()
    
    provider, confidence = selector.select_provider('test-uuid')
    
    assert provider in ['anthropic', 'openai', 'groq', 'ollama', 'deepseek']
    assert 0 <= confidence <= 1

def test_update_reward():
    selector = RLProviderSelector()
    
    # High reward
    selector.update_reward('test-uuid', 'anthropic', 0.9)
    
    stats = selector.get_stats()
    assert stats['anthropic']['alpha'] > 1.0  # Increased

def test_thompson_sampling_converges():
    selector = RLProviderSelector()
    
    # Symuluj wiele nagród dla anthropic
    for _ in range(100):
        selector.update_reward('test-uuid', 'anthropic', 0.9)
    
    # Anthropic powinien mieć najwyższy mean
    stats = selector.get_stats()
    anthropic_mean = stats['anthropic']['mean']
    
    for provider, provider_stats in stats.items():
        if provider != 'anthropic':
            assert anthropic_mean > provider_stats['mean']
```

---

## 📊 Monitoring

**Dashboard do wizualizacji:**

```python
# src/ml/dashboard.py (opcjonalnie)

import matplotlib.pyplot as plt
from src.ml.provider_selector import RLProviderSelector

def plot_provider_stats():
    selector = RLProviderSelector()
    stats = selector.get_stats()
    
    providers = list(stats.keys())
    means = [stats[p]['mean'] for p in providers]
    trials = [stats[p]['total_trials'] for p in providers]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Mean confidence
    ax1.bar(providers, means)
    ax1.set_title('Provider Mean Confidence')
    ax1.set_ylabel('Mean')
    
    # Total trials
    ax2.bar(providers, trials)
    ax2.set_title('Provider Total Trials')
    ax2.set_ylabel('Trials')
    
    plt.tight_layout()
    plt.savefig('provider_stats.png')
```

---

## 🚀 Deployment

**Uruchomienie serwera:**

```bash
cd /Users/piotradamczyk/Projects/Octadecimal/ai-local-core
source venv/bin/activate
python src/api/server.py
```

**Lub jako serwis systemd:**

```ini
# /etc/systemd/system/ai-local-core-ml.service

[Unit]
Description=AI Local Core ML Service
After=network.target

[Service]
Type=simple
User=piotradamczyk
WorkingDirectory=/Users/piotradamczyk/Projects/Octadecimal/ai-local-core
ExecStart=/Users/piotradamczyk/Projects/Octadecimal/ai-local-core/venv/bin/python src/api/server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 📝 Następne kroki

1. ✅ Zaimplementować `RLProviderSelector` w `src/ml/provider_selector.py`
2. ✅ Dodać endpointy do `src/api/server.py`
3. ✅ Dodać testy w `tests/unit/test_provider_selector.py`
4. ⏳ Zebrać dane (1000+ interakcji) z waldus-api
5. ⏳ Zaimplementować `XGBoostProviderSelector` (opcjonalnie)
6. ⏳ A/B testing: RL vs XGBoost vs heurystyki

---

**Status:** 🟡 Gotowy do implementacji  
**Ostatnia aktualizacja:** 2025-11-10

