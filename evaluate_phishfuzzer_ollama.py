import json
import requests
import time
import csv
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:1.5b"

logging.info("📂 Loading PhishFuzzer dataset...")
with open("./data/PhishFuzzer_emails_original_seed_v1.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

test_datasets = dataset[1385:1400] 

system_prompt = """You are an expert cybersecurity email classifier. 
Analyze the email and classify it into EXACTLY ONE category.
Output ONLY valid JSON with the single key "predicted_type".

Categories:
- "Phishing": Deceptive sender, fake urgency, malicious/obfuscated links, credential theft.
- "Spam": Unsolicited marketing, but uses real official company domains.
- "Valid": Legitimate business, expected, professional communication.

Do not output any text outside the JSON object."""

correct_count = 0
total_processed = 0
results_log = [] 

logging.info(f"🚀 Starting detailed evaluation on {len(test_datasets)} emails...\n")
logging.info("-" * 70)

for index, email in enumerate(test_datasets):
    sender = email.get('Sender', "Unknown")
    subject = email.get('Subject', "No Subject")
    body = email.get('Body', '')
    urls = ", ".join(email.get('URL', []) or []) or "None"
    
    state_text = f"SENDER: {sender}\nSUBJECT: {subject}\nURLS: {urls}\nBODY: {body}"
    ground_truth = email.get("Type", "Unknown")
    
    payload = {
        "model": MODEL,
        "prompt": f"{system_prompt}\n\nEMAIL TO ANALYZE:\n{state_text}",
        "stream": False,
        "format": "json", 
        "options": {
            "temperature": 0.1, 
            "num_ctx": 2048     
        }
    }
    
    start_time = time.time()
    raw_response = None
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        
        raw_response = response.json()["response"]
        result = json.loads(raw_response)
        latency = (time.time() - start_time) * 1000
        
        type_pred = result.get("predicted_type", "Unknown").strip()
        total_processed += 1
        
        logging.info(f"type_pred {type_pred} => ground_truth {ground_truth}")
        
        is_match = type_pred.lower() == ground_truth.lower()
        status = "✅ MATCH" if is_match else " MISMATCH"
        if is_match:
            correct_count += 1
            
        # Detailed console logging for every email
        logging.info(f"Email #{index+1:02d} | Truth: {ground_truth:<10} | Pred: {type_pred.upper():<10} | Latency: {latency:>6.1f}ms | {status}")
        
        # Save to log for CSV
        results_log.append({
            "email_index": index + 1,
            "ground_truth": ground_truth,
            "prediction": type_pred,
            "latency_ms": round(latency, 2),
            "status": "Match" if is_match else "Mismatch"
        })
            
    except json.JSONDecodeError as e:
        logging.error(f" JSON Parse Error on email {index+1}.")
        logging.error(f"   Raw Model Output: {repr(raw_response)}") 
        results_log.append({
            "email_index": index + 1,
            "ground_truth": ground_truth,
            "prediction": "JSON_ERROR",
            "latency_ms": round((time.time() - start_time) * 1000, 2),
            "status": "Error"
        })
    except Exception as e:
        logging.error(f" Unexpected Error on email {index+1}: {e}")

logging.info("-" * 70)
final_acc = (correct_count / total_processed) * 100 if total_processed > 0 else 0

logging.info("🏁 FINAL RESULTS")
logging.info(f"Total Processed : {total_processed}")
logging.info(f"Correct Matches : {correct_count}")
logging.info(f"Final Accuracy  : {final_acc:.2f}%")
logging.info("-" * 70)

# Save the detailed results to a CSV file for analysis
csv_filename = "phishfuzzer_evaluation_results.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["email_index", "ground_truth", "prediction", "latency_ms", "status"])
    writer.writeheader()
    writer.writerows(results_log)

logging.info(f"💾 Detailed results saved to: {csv_filename}")