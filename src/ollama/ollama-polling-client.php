#!/usr/bin/env php
<?php
/**
 * Klient polling dla Ollama
 * 
 * Co kilka sekund pyta serwer OVH czy ma zadanie do przetworzenia.
 * Jeśli tak, przetwarza przez Ollama i zwraca odpowiedź.
 * 
 * Użycie:
 *   php src/ollama/ollama-polling-client.php
 *   php src/ollama/ollama-polling-client.php --api-url=https://waldus.cloud/api/v1
 *   php src/ollama/ollama-polling-client.php --poll-interval=5
 *   lub użyj głównego skryptu: ./start.sh
 * 
 * Wymagane zmienne środowiskowe:
 *   OLLAMA_POLLING_API_URL - URL do API (domyślnie: https://waldus.cloud/api/v1)
 *   OLLAMA_POLLING_INTERVAL - Interwał polling w sekundach (domyślnie: 3)
 *   OLLAMA_URL - URL do lokalnego Ollama (domyślnie: http://localhost:11434)
 */

/**
 * Załaduj zmienne środowiskowe z pliku .env (jeśli istnieje)
 */
function loadEnvFile(string $projectDir): void
{
    $envPath = $projectDir . '/.env';
    if (!is_file($envPath) || !is_readable($envPath)) {
        return;
    }

    $lines = file($envPath, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    if ($lines === false) {
        return;
    }

    foreach ($lines as $line) {
        $line = trim($line);

        // Pomijamy komentarze
        if ($line === '' || str_starts_with($line, '#')) {
            continue;
        }

        // Podziel klucz=wartość
        $parts = explode('=', $line, 2);
        if (count($parts) !== 2) {
            continue;
        }

        [$key, $value] = $parts;
        $key = trim($key);
        $value = trim($value);

        // Usuń otaczające cudzysłowy
        if (
            (str_starts_with($value, '"') && str_ends_with($value, '"')) ||
            (str_starts_with($value, "'") && str_ends_with($value, "'"))
        ) {
            $value = substr($value, 1, -1);
        }

        if ($key !== '') {
            putenv(sprintf('%s=%s', $key, $value));
            $_ENV[$key] = $value;
            $_SERVER[$key] = $value;
        }
    }
}

$projectDir = dirname(__FILE__);
loadEnvFile($projectDir);

// Pobierz argumenty z linii poleceń
$apiUrl = null;
$pollInterval = null;

foreach ($argv as $arg) {
    if (strpos($arg, '--api-url=') === 0) {
        $apiUrl = substr($arg, 10);
    } elseif (strpos($arg, '--poll-interval=') === 0) {
        $pollInterval = (int)substr($arg, 16);
    }
}

// Pobierz konfigurację
$apiUrl = $apiUrl ?: getenv('OLLAMA_POLLING_API_URL') ?: 'https://waldus.cloud/api/v1';
$pollInterval = $pollInterval ?: (int)(getenv('OLLAMA_POLLING_INTERVAL') ?: 3);
$ollamaUrl = getenv('OLLAMA_URL') ?: 'http://localhost:11434';

// URL endpointów
$pollUrl = rtrim($apiUrl, '/') . '/ollama/poll';
$responseUrl = rtrim($apiUrl, '/') . '/ollama/response';

echo "🤖 Ollama Polling Client\n";
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n";
echo "API URL: {$apiUrl}\n";
echo "Poll interval: {$pollInterval} sekund\n";
echo "Ollama URL: {$ollamaUrl}\n";
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n";

// Główna pętla polling
$iteration = 0;
while (true) {
    $iteration++;
    $timestamp = date('Y-m-d H:i:s');
    
    echo "[{$timestamp}] Iteracja #{$iteration}: Sprawdzanie zadań...\n";
    
    try {
        // GET /api/v1/ollama/poll
        $ch = curl_init($pollUrl);
        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => 10,
            CURLOPT_CONNECTTIMEOUT => 5,
            CURLOPT_HTTPHEADER => [
                'Content-Type: application/json',
            ],
        ]);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $curlError = curl_error($ch);
        curl_close($ch);
        
        if ($response === false || $httpCode !== 200) {
            if ($curlError) {
                echo "  ⚠️  Błąd połączenia: {$curlError}\n";
                echo "  🌐 Ollama URL: {$ollamaUrl}\n";
                echo "  🌐 Poll URL: {$pollUrl}\n";     
            } else {
                echo "  ⚠️  Błąd HTTP: {$httpCode}\n";
                echo "  🌐 Ollama URL: {$ollamaUrl}\n";
                echo "  🌐 Poll URL: {$pollUrl}\n"; 
            }
            echo "  💤 Czekam {$pollInterval} sekund...\n\n";
            sleep($pollInterval);
            continue;
        }
        
        $data = json_decode($response, true);
        
        if (!$data || !isset($data['has_job']) || !$data['has_job']) {
            // Brak zadań
            echo "  ✅ Brak zadań w kolejce\n";
            echo "  💤 Czekam {$pollInterval} sekund...\n\n";
            echo "  🌐 Ollama URL: {$ollamaUrl}\n";
            echo "  🌐 Poll URL: {$pollUrl}\n"; 
            sleep($pollInterval);
            continue;
        }
        
        // Mamy zadanie!
        $job = $data['job'];
        $jobUuid = $job['job_uuid'];
        $requestData = $job['request_data'];
        
        echo "  📋 Znaleziono zadanie: {$jobUuid}\n";
        echo "  📝 Model: {$requestData['model']}\n";
        echo "  ⏳ Przetwarzanie przez Ollama...\n";
        
        // Przetwórz przez Ollama
        $ollamaResponse = processWithOllama($ollamaUrl, $requestData);
        
        if ($ollamaResponse['success']) {
            echo "  ✅ Odpowiedź otrzymana ({$ollamaResponse['response_length']} znaków)\n";
            echo "  📤 Wysyłanie odpowiedzi do serwera...\n";
            
            // POST /api/v1/ollama/response
            $responseData = [
                'job_uuid' => $jobUuid,
                'response_text' => $ollamaResponse['response_text'],
                'response_metadata' => $ollamaResponse['metadata'],
            ];
            
            $ch = curl_init($responseUrl);
            curl_setopt_array($ch, [
                CURLOPT_POST => true,
                CURLOPT_RETURNTRANSFER => true,
                CURLOPT_TIMEOUT => 10,
                CURLOPT_CONNECTTIMEOUT => 5,
                CURLOPT_HTTPHEADER => [
                    'Content-Type: application/json',
                ],
                CURLOPT_POSTFIELDS => json_encode($responseData, JSON_UNESCAPED_UNICODE),
            ]);
            
            $response = curl_exec($ch);
            $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
            curl_close($ch);
            
            if ($httpCode === 200) {
                echo "  ✅ Odpowiedź wysłana pomyślnie\n\n";
            } else {
                echo "  ❌ Błąd wysyłania odpowiedzi: HTTP {$httpCode}\n";
                echo "  Response: {$response}\n\n";
            }
        } else {
            echo "  ❌ Błąd przetwarzania: {$ollamaResponse['error']}\n";
            echo "  📤 Wysyłanie błędu do serwera...\n";
            
            // Wyślij błąd
            $responseData = [
                'job_uuid' => $jobUuid,
                'response_text' => '',
                'response_metadata' => [],
                'error_message' => $ollamaResponse['error'],
            ];
            
            $ch = curl_init($responseUrl);
            curl_setopt_array($ch, [
                CURLOPT_POST => true,
                CURLOPT_RETURNTRANSFER => true,
                CURLOPT_TIMEOUT => 10,
                CURLOPT_CONNECTTIMEOUT => 5,
                CURLOPT_HTTPHEADER => [
                    'Content-Type: application/json',
                ],
                CURLOPT_POSTFIELDS => json_encode($responseData, JSON_UNESCAPED_UNICODE),
            ]);
            
            curl_exec($ch);
            curl_close($ch);
            
            echo "  ✅ Błąd wysłany do serwera\n\n";
        }
        
    } catch (\Exception $e) {
        echo "  ❌ Wyjątek: {$e->getMessage()}\n\n";
    }
    
    // Krótka przerwa przed następnym poll
    sleep(1);
}

/**
 * Przetwórz zadanie przez Ollama
 */
function processWithOllama(string $ollamaUrl, array $requestData): array
{
    try {
        $url = rtrim($ollamaUrl, '/') . '/api/generate';
        
        // Przygotuj prompt
        $systemPrompt = $requestData['system'] ?? '';
        $userPrompt = $requestData['user'] ?? '';
        $fullPrompt = $systemPrompt ? "{$systemPrompt}\n\n{$userPrompt}" : $userPrompt;
        
        $data = [
            'model' => $requestData['model'] ?? 'llama3.1:8b',
            'prompt' => $fullPrompt,
            'stream' => false,
            'options' => [
                'temperature' => $requestData['temperature'] ?? 0.7,
                'num_predict' => min($requestData['max_tokens'] ?? 1000, 8192),
            ],
        ];
        
        // Jeśli system prompt jest osobno, dodaj go
        if (!empty($systemPrompt)) {
            $data['system'] = $systemPrompt;
            $data['prompt'] = $userPrompt;
        }
        
        $startTime = microtime(true);
        
        $ch = curl_init($url);
        curl_setopt_array($ch, [
            CURLOPT_POST => true,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => 300, // 5 minut
            CURLOPT_CONNECTTIMEOUT => 10,
            CURLOPT_HTTPHEADER => [
                'Content-Type: application/json',
            ],
            CURLOPT_POSTFIELDS => json_encode($data, JSON_UNESCAPED_UNICODE),
        ]);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $curlError = curl_error($ch);
        $responseTimeMs = (int)((microtime(true) - $startTime) * 1000);
        curl_close($ch);
        
        if ($response === false || $httpCode !== 200) {
            return [
                'success' => false,
                'error' => $curlError ?: "HTTP {$httpCode}: {$response}",
            ];
        }
        
        $responseData = json_decode($response, true);
        
        if (!isset($responseData['response'])) {
            return [
                'success' => false,
                'error' => 'Nieprawidłowa struktura odpowiedzi z Ollama',
            ];
        }
        
        $inputTokens = $responseData['prompt_eval_count'] ?? 0;
        $outputTokens = $responseData['eval_count'] ?? 0;
        
        return [
            'success' => true,
            'response_text' => trim($responseData['response']),
            'response_length' => strlen($responseData['response']),
            'metadata' => [
                'input_tokens' => $inputTokens,
                'output_tokens' => $outputTokens,
                'response_time_ms' => $responseTimeMs,
            ],
        ];
        
    } catch (\Exception $e) {
        return [
            'success' => false,
            'error' => $e->getMessage(),
        ];
    }
}

