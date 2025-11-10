#!/bin/bash
# Testy kompatybilności CLI dla wszystkich skryptów

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"
source venv/bin/activate

echo "🧪 Testing CLI compatibility..."
echo ""

# Test 1: Translation
echo "1️⃣  Testing Translation CLI..."
echo -n "   PL: "
RESULT=$(python3 src/translation/translate.py "Hello world" pl 2>&1 | grep -o '"success": true' || echo "FAILED")
if [ "$RESULT" = '"success": true' ]; then
    echo "✅ OK"
else
    echo "❌ FAILED"
fi

echo -n "   DE: "
RESULT=$(python3 src/translation/translate.py "Hello world" de 2>&1 | grep -o '"success": true' || echo "FAILED")
if [ "$RESULT" = '"success": true' ]; then
    echo "✅ OK"
else
    echo "❌ FAILED"
fi

# Test 2: Image Description
echo ""
echo "2️⃣  Testing Image Description CLI..."
echo -n "   URL: "
RESULT=$(python3 src/image/describe.py "https://picsum.photos/800/600" 50 2>&1 | grep -o '"success": true' || echo "FAILED")
if [ "$RESULT" = '"success": true' ]; then
    echo "✅ OK"
else
    echo "❌ FAILED"
fi

# Test 3: Ollama (wymaga uruchomionego Ollama)
echo ""
echo "3️⃣  Testing Ollama CLI..."
OLLAMA_RUNNING=$(curl -s http://localhost:11434/api/tags >/dev/null 2>&1 && echo "yes" || echo "no")
if [ "$OLLAMA_RUNNING" = "yes" ]; then
    echo -n "   Basic: "
    RESULT=$(python3 src/ollama/complete.py '{"user": "Say hello"}' 2>&1 | grep -o '"success": true' || echo "FAILED")
    if [ "$RESULT" = '"success": true' ]; then
        echo "✅ OK"
    else
        echo "❌ FAILED"
    fi
else
    echo "   ⚠️  Ollama nie jest uruchomiona (pomiń test)"
    echo "   Uruchom: ollama serve"
fi

# Test 4: Error handling (brak argumentów)
echo ""
echo "4️⃣  Testing error handling..."
echo -n "   Translation (no args): "
RESULT=$(python3 src/translation/translate.py 2>&1 | grep -o '"error":' || echo "FAILED")
if [ "$RESULT" = '"error":' ]; then
    echo "✅ OK"
else
    echo "❌ FAILED"
fi

echo -n "   Image (no args): "
RESULT=$(python3 src/image/describe.py 2>&1 | grep -o '"error":' || echo "FAILED")
if [ "$RESULT" = '"error":' ]; then
    echo "✅ OK"
else
    echo "❌ FAILED"
fi

echo -n "   Ollama (no args): "
RESULT=$(python3 src/ollama/complete.py 2>&1 | grep -o '"error":' || echo "FAILED")
if [ "$RESULT" = '"error":' ]; then
    echo "✅ OK"
else
    echo "❌ FAILED"
fi

echo ""
echo "✅ CLI compatibility tests completed!"

