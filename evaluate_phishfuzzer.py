import json
import time
import csv
import logging
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning, module="laya")
from laya import Router

logging.basicConfig(level=logging.INFO, format='%(message)s')

logging.info("📂 Loading PhishFuzzer sample dataset...")
with open("./data/phishfuzzer_sample_300.json", "r", encoding="utf-8") as f:
    test_datasets = json.load(f)

logging.info("🔌 Loading Laya directly into GPU (CUDA)...")
# Force CUDA and preload to prevent CPU fallback and VRAM thrashing
router = Router(preload=True, device="cuda")
logging.info("✅ Model loaded successfully!\n")

# LAYA SCHEMA: Short, distinct criteria work best for Laya's token-scoring head
questions = {
    "classification": {
        "type": "choice",
        "instructions": "Primary email classification",
        "criteria": {
            "Phishing": "Deceptive sender, fake urgency, malicious links",
            "Spam": "Unsolicited marketing, real official domains",
            "Valid": "Legitimate business, expected, professional"
        }
    }
}

correct_count = 0
total_processed = 0
results_log = []

logging.info(f"🚀 Starting detailed Laya evaluation on {len(test_datasets)} emails...\n")
logging.info("-" * 75)

for index, email in enumerate(test_datasets):
    sender = email.get('Sender', "Unknown")
    subject = email.get('Subject', "No Subject")
    body = email.get('Body', '')
    urls = ", ".join(email.get('URL', []) or []) or "None"
    
    state_text = f"SENDER: {sender}\nSUBJECT: {subject}\nURLS: {urls}\nBODY: {body}"
    ground_truth = email.get("Type", "Unknown")
    
    start_time = time.time()
    try:
        result = router.predict(state_text, questions, model="typed-decisions")
        latency = (time.time() - start_time) * 1000
        
        type_pred = result["answers"]["classification"]["choice"].strip()
        confidence = result["answers"]["classification"]["confidence"]
        total_processed += 1
        
        is_match = type_pred.lower() == ground_truth.lower()
        status = "✅ MATCH" if is_match else "❌ MISMATCH"
        if is_match:
            correct_count += 1
            
        # Detailed console logging
        logging.info(f"Email #{index+1:02d} | Truth: {ground_truth:<10} | Pred: {type_pred.upper():<10} (Conf: {confidence:.2f}) | Latency: {latency:>6.1f}ms | {status}")
        
        results_log.append({
            "email_index": index + 1,
            "ground_truth": ground_truth,
            "prediction": type_pred,
            "confidence": round(confidence, 4),
            "latency_ms": round(latency, 2),
            "status": "Match" if is_match else "Mismatch"
        })
            
    except Exception as e:
        logging.error(f"❌ Error on email {index+1}: {e}")
        results_log.append({
            "email_index": index + 1,
            "ground_truth": ground_truth,
            "prediction": "ERROR",
            "confidence": 0.0,
            "latency_ms": round((time.time() - start_time) * 1000, 2),
            "status": "Error"
        })

logging.info("-" * 75)
final_acc = (correct_count / total_processed) * 100 if total_processed > 0 else 0

logging.info("🏁 FINAL RESULTS")
logging.info(f"Total Processed : {total_processed}")
logging.info(f"Correct Matches : {correct_count}")
logging.info(f"Final Accuracy  : {final_acc:.2f}%")
logging.info("-" * 75)

# Save to CSV
csv_filename = "laya_phishfuzzer_results.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["email_index", "ground_truth", "prediction", "confidence", "latency_ms", "status"])
    writer.writeheader()
    writer.writerows(results_log)

logging.info(f"💾 Detailed results saved to: {csv_filename}")