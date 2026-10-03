import json
import random

SOURCE = "./data/PhishFuzzer_emails_original_seed_v1.json"
OUTPUT = "./data/phishfuzzer_sample_300.json"
PER_CLASS = 100
SEED = 42

with open(SOURCE, "r", encoding="utf-8") as f:
    dataset = json.load(f)

by_class = {}
for email in dataset:
    by_class.setdefault(email.get("Type"), []).append(email)

rng = random.Random(SEED)
sample = []
for cls in ("Phishing", "Spam", "Valid"):
    pool = by_class.get(cls, [])
    sample.extend(rng.sample(pool, min(PER_CLASS, len(pool))))

rng.shuffle(sample)

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(sample, f, ensure_ascii=False, indent=2)

print(f"Saved {len(sample)} emails ({PER_CLASS} per class, seed={SEED}) to {OUTPUT}")
