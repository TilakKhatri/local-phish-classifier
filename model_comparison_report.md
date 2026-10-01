# PhishFuzzer Model Comparison

Generated: 2026-10-01 15:02 UTC

Local machine: Windows 11 | Intel64 Family 6 Model 158 Stepping 10, GenuineIntel | Python 3.14.2 | Host: DESKTOP-N7U823O

Emails evaluated: 15 (same PhishFuzzer sample across all models)

## Summary

| Model | Device | Accuracy | Correct/Total | Avg Latency | Min Latency | Max Latency |
|---|---|---|---|---|---|---|
| Laya (typed-decisions) | Local GPU (CUDA, 4GB VRAM laptop) | 53.33% | 8/15 | 3482.6 ms | 1322.7 ms | 18856.4 ms |
| Qwen2.5:1.5b (Ollama) | Local GPU (CUDA, 4GB VRAM laptop, quantized) | 20.00% | 3/15 | 1991.5 ms | 1078.6 ms | 6554.3 ms |
| Jev-latest (TypeSafe.ai API) | Cloud API (TypeSafe.ai) | 93.33% | 14/15 | 472.6 ms | 448.3 ms | 513.3 ms |

## Per-Email Predictions

| # | Ground Truth | Laya (typed-decisions) | Qwen2.5:1.5b (Ollama) | Jev-latest (TypeSafe.ai API) |
|---|---|---|---|---|
| 1 | Spam | Spam ✅ | Phishing ❌ | Spam ✅ |
| 2 | Spam | Spam ✅ | Phishing ❌ | Spam ✅ |
| 3 | Spam | Phishing ❌ | Phishing ❌ | Spam ✅ |
| 4 | Spam | Valid ❌ | Spam ✅ | Spam ✅ |
| 5 | Spam | Spam ✅ | Phishing ❌ | Spam ✅ |
| 6 | Spam | Valid ❌ | Spam ✅ | Valid ❌ |
| 7 | Spam | Spam ✅ | Phishing ❌ | Spam ✅ |
| 8 | Spam | Phishing ❌ | Phishing ❌ | Spam ✅ |
| 9 | Spam | Phishing ❌ | Phishing ❌ | Spam ✅ |
| 10 | Spam | Phishing ❌ | Phishing ❌ | Spam ✅ |
| 11 | Spam | Spam ✅ | Phishing ❌ | Spam ✅ |
| 12 | Spam | Phishing ❌ | Spam ✅ | Spam ✅ |
| 13 | Spam | Spam ✅ | Phishing ❌ | Spam ✅ |
| 14 | Spam | Spam ✅ | Phishing ❌ | Spam ✅ |
| 15 | Spam | Spam ✅ | Phishing ❌ | Spam ✅ |
