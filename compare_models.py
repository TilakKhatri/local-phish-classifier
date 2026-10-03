"""Merge per-email results from the three PhishFuzzer evaluation runs
(Laya, Qwen2.5/Ollama, Jev/TypeSafe.ai) into a single comparison table
and summary report, suitable for sharing (e.g. in an article)."""
import csv
import platform
import socket
from datetime import datetime, timezone

RUNS = [
    {
        "key": "laya",
        "label": "Laya (typed-decisions)",
        "csv": "laya_phishfuzzer_results.csv",
        "device": "Local GPU (CUDA, 4GB VRAM laptop)",
    },
    {
        "key": "ollama",
        "label": "Qwen2.5:1.5b (Ollama)",
        "csv": "phishfuzzer_evaluation_results.csv",
        "device": "Local GPU (CUDA, 4GB VRAM laptop, quantized)",
    },
    {
        "key": "jev",
        "label": "Jev-latest (TypeSafe.ai API)",
        "csv": "jev_phishfuzzer_results.csv",
        "device": "Cloud API (TypeSafe.ai)",
    },
]


def load_run(path):
    rows = {}
    with open(path, "r", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows[int(row["email_index"])] = row
    return rows


def summarize(rows):
    total = len(rows)
    matches = sum(1 for r in rows.values() if r["status"] == "Match")
    latencies = [float(r["latency_ms"]) for r in rows.values() if r.get("latency_ms")]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
    accuracy = (matches / total * 100) if total else 0.0
    return {
        "total": total,
        "matches": matches,
        "accuracy": accuracy,
        "avg_latency_ms": avg_latency,
        "min_latency_ms": min(latencies) if latencies else 0.0,
        "max_latency_ms": max(latencies) if latencies else 0.0,
    }


def confusion_matrix(rows):
    """Per ground-truth class: counts of what the model actually predicted."""
    matrix = {}
    for r in rows.values():
        truth = r["ground_truth"]
        pred = r["prediction"]
        matrix.setdefault(truth, {}).setdefault(pred, 0)
        matrix[truth][pred] += 1
    return matrix


def main():
    run_rows = {run["key"]: load_run(run["csv"]) for run in RUNS}
    all_indexes = sorted(set().union(*(rows.keys() for rows in run_rows.values())))

    # Per-email comparison CSV
    comparison_csv = "model_comparison_results.csv"
    fieldnames = ["email_index", "ground_truth"]
    for run in RUNS:
        fieldnames += [f"{run['key']}_prediction", f"{run['key']}_status", f"{run['key']}_latency_ms"]

    with open(comparison_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for idx in all_indexes:
            ground_truth = next(
                (run_rows[run["key"]][idx]["ground_truth"] for run in RUNS if idx in run_rows[run["key"]]),
                "Unknown",
            )
            out_row = {"email_index": idx, "ground_truth": ground_truth}
            for run in RUNS:
                row = run_rows[run["key"]].get(idx)
                out_row[f"{run['key']}_prediction"] = row["prediction"] if row else "N/A"
                out_row[f"{run['key']}_status"] = row["status"] if row else "N/A"
                out_row[f"{run['key']}_latency_ms"] = row["latency_ms"] if row else "N/A"
            writer.writerow(out_row)

    summaries = {run["key"]: summarize(run_rows[run["key"]]) for run in RUNS}
    confusions = {run["key"]: confusion_matrix(run_rows[run["key"]]) for run in RUNS}
    classes = sorted({r["ground_truth"] for rows in run_rows.values() for r in rows.values()})

    # Markdown summary report
    report_path = "model_comparison_report.md"
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    host_info = f"{platform.system()} {platform.release()} | {platform.processor() or platform.machine()} | Python {platform.python_version()} | Host: {socket.gethostname()}"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# PhishFuzzer Model Comparison\n\n")
        f.write(f"Generated: {generated_at}\n\n")
        f.write(f"Local machine: {host_info}\n\n")
        f.write(f"Emails evaluated: {len(all_indexes)} (same PhishFuzzer sample across all models)\n\n")
        f.write("## Summary\n\n")
        f.write("| Model | Device | Accuracy | Correct/Total | Avg Latency | Min Latency | Max Latency |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for run in RUNS:
            s = summaries[run["key"]]
            f.write(
                f"| {run['label']} | {run['device']} | {s['accuracy']:.2f}% | {s['matches']}/{s['total']} | "
                f"{s['avg_latency_ms']:.1f} ms | {s['min_latency_ms']:.1f} ms | {s['max_latency_ms']:.1f} ms |\n"
            )

        f.write("\n## Per-Class Recall (Confusion Matrix)\n\n")
        f.write("| Model | Class | Recall | Correct/Total | Most Common Confusion |\n")
        f.write("|---|---|---|---|---|\n")
        for run in RUNS:
            matrix = confusions[run["key"]]
            for cls in classes:
                preds = matrix.get(cls, {})
                total = sum(preds.values())
                correct = preds.get(cls, 0)
                recall = (correct / total * 100) if total else 0.0
                wrong_preds = {p: c for p, c in preds.items() if p != cls}
                top_wrong = max(wrong_preds.items(), key=lambda kv: kv[1]) if wrong_preds else None
                confusion_text = f"{top_wrong[0]} ({top_wrong[1]})" if top_wrong else "-"
                f.write(f"| {run['label']} | {cls} | {recall:.1f}% | {correct}/{total} | {confusion_text} |\n")

        f.write("\n## Per-Email Predictions\n\n")
        f.write("| # | Ground Truth | " + " | ".join(run["label"] for run in RUNS) + " |\n")
        f.write("|---|---|" + "---|" * len(RUNS) + "\n")
        for idx in all_indexes:
            ground_truth = next(
                (run_rows[run["key"]][idx]["ground_truth"] for run in RUNS if idx in run_rows[run["key"]]),
                "Unknown",
            )
            cells = []
            for run in RUNS:
                row = run_rows[run["key"]].get(idx)
                if row:
                    mark = "✅" if row["status"] == "Match" else "❌"
                    cells.append(f"{row['prediction']} {mark}")
                else:
                    cells.append("N/A")
            f.write(f"| {idx} | {ground_truth} | " + " | ".join(cells) + " |\n")

    print(f"Comparison CSV saved to: {comparison_csv}")
    print(f"Markdown report saved to: {report_path}")
    for run in RUNS:
        s = summaries[run["key"]]
        print(f"{run['label']}: {s['accuracy']:.2f}% accuracy, avg latency {s['avg_latency_ms']:.1f} ms")


if __name__ == "__main__":
    main()
