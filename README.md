# Local-First Phishing Email Classification on Consumer Hardware

A zero-cost, local-first AI pipeline for evaluating and classifying adversarial phishing emails on constrained consumer hardware. This project demonstrates that high-throughput, structured threat classification can be executed entirely on-premise with strict data privacy, providing a viable baseline for researchers and SOC analysts operating under strict hardware and budget constraints.

## Research Context & Motivation

Modern AI security tools often rely on massive cloud-based LLMs (e.g., GPT-4, Claude) or require enterprise-grade GPUs (e.g., A100s). This creates a barrier to entry for independent researchers, students, and security teams in developing regions. 

This repository investigates the feasibility of running **local-first AI for cybersecurity threat triage** using:
1. **Constrained Hardware:** A consumer laptop with a 4GB NVIDIA GPU (e.g., Acer Nitro 5).
2. **Zero Budget:** 100% open-source models and local inference (no API costs).
3. **Strict Privacy:** Data never leaves the local machine.

We evaluate two distinct architectural approaches for structured output generation: **System-1 Decision Models (Laya)** and **Quantized Generative LLMs (Qwen2.5 via Ollama)**.

## Target Hardware Specifications
- **GPU:** NVIDIA GPU with 4GB VRAM 
- **RAM:** 8GB+ System RAM
- **OS:** Windows 10/11 (via WSL2) or native Linux
- **Storage:** SSD (Required for fast model weight loading)

## Dataset

This project evaluates against the **PhishFuzzer** dataset, a highly nuanced, metadata-enriched benchmark for phishing detection.
- **Source:** [DataPhish/PhishFuzzer](https://github.com/DataPhish/PhishFuzzer)
- **File used:** `PhishFuzzer_emails_original_seed_v1.json`
- **Classes:** `Phishing`, `Spam`, `Valid`

*(Note: The `data/` folder is excluded via `.gitignore`. Please download the dataset manually and place it in a local `./data/` directory.)*

---

## Methodology & Experiments

### Experiment 1: System-1 Decision Models (Laya)
We first tested **Laya**, an open-source, 421M parameter non-autoregressive "System-1" decision model designed to output mathematically calibrated probabilities in a single forward pass without generating text.

**Findings:**
- **Latency:** Extremely fast (~40ms per email on GPU).
- **Zero-Shot Limitation:** The base `typed-decisions` checkpoint struggled with zero-shot adversarial classification on the PhishFuzzer dataset (defaulting to "Valid" due to lack of domain-specific fine-tuning).
- **Conclusion:** While System-1 models offer incredible speed and native structured outputs, they require domain-specific fine-tuning to overcome default priors on novel adversarial datasets.

### Experiment 2: Quantized Generative LLMs (Ollama + Qwen2.5)
To achieve high zero-shot accuracy without fine-tuning, we deployed **Qwen2.5:1.5B**, a highly optimized 1.5B parameter generative model, served locally via Ollama.

**Findings:**
- **Accuracy:** Achieved ~80%+ zero-shot accuracy on the PhishFuzzer seed dataset.
- **Structured Output:** Utilized Ollama's native `format: "json"` flag to guarantee strict, parseable JSON outputs without fragile Regex extraction.
- **Resource Usage:** Consumed < 2GB VRAM, leaving ample headroom for the host OS.
- **Conclusion:** Quantized sub-2B generative models provide a highly viable, zero-cost baseline for structured threat classification on consumer hardware.

---

## Setup & Installation

### 1. Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) installed and running locally.

### 2. Environment Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd <your-repo-name>

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate 

# Install Python dependencies
pip install requests laya
```

### 3. Model Setup
Pull the quantized model optimized for 4GB VRAM:
```
ollama pull qwen2.5:1.5b
```


#### Running the Generative LLM Pipeline (Recommended Baseline)
This script uses Ollama and Qwen2.5 to classify the emails, enforcing strict JSON output.
```
python evaluate_phishfuzzer_ollama.py
```

#### Running the System-1 Pipeline (Laya)
This script uses the Laya Python SDK to evaluate the emails using the typed-decisions checkpoint.
```
python evaluate_laya.py
```

#### Output
Both scripts will:
* Print real-time latency, predictions, and ground-truth comparisons to the console.
* Automatically generate a detailed CSV file (e.g., phishfuzzer_evaluation_results.csv) containing every prediction, confidence score, and latency metric for further statistical analysis (Precision, Recall, F1-Score).



### License
This project is intended for academic and research purposes. The PhishFuzzer dataset is subject to its own licensing terms as defined by its original authors (DataPhish). The code in this repository is provided as-is for educational use.

### Contributin
Pull requests and suggestions for optimizing low-VRAM inference, fine-tuning Laya for phishing detection, or testing alternative quantized models (e.g., Phi-3 Mini, Gemma 2B) are highly welcome. Please open an issue to discuss potential improvements.