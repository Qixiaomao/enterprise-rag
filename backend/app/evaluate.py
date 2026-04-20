import csv
import time
from pathlib import Path

import requests


BASE_DIR = Path(__file__).resolve().parent.parent.parent
EVAL_DIR = BASE_DIR / "evaluation"
INPUT_CSV = EVAL_DIR / "enterprise_rag_eval_questions.csv"
OUTPUT_CSV = EVAL_DIR / "enterprise_rag_eval_results.csv"

API_URL = "http://127.0.0.1:8000/ask"


def run_evaluation():
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Evaluation file not found: {INPUT_CSV}")

    rows = []
    total = 0
    top1_correct = 0
    total_latency = 0.0

    with open(INPUT_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            qid = row["qid"]
            question = row["question"]
            expected_topic = row["expected_topic"]
            expected_document = row["expected_document"]
            expected_keywords = row["expected_keywords"]

            start = time.perf_counter()

            try:
                response = requests.post(
                    API_URL,
                    json={"question": question},
                    timeout=60
                )
                response.raise_for_status()
                data = response.json()
                success = data.get("success", False)
                answer = data.get("answer", "")
                sources = data.get("sources", [])

            except Exception as e:
                elapsed = round(time.perf_counter() - start, 3)
                rows.append({
                    "qid": qid,
                    "question": question,
                    "expected_topic": expected_topic,
                    "expected_document": expected_document,
                    "expected_keywords": expected_keywords,
                    "success": False,
                    "latency_sec": elapsed,
                    "top1_source_file": "",
                    "top1_page": "",
                    "top1_score": "",
                    "top1_correct": "",
                    "answer": f"ERROR: {e}",
                    "manual_answer_label": "",
                    "manual_answer_score": "",
                    "notes": "request failed"
                })
                print(f"[{qid}] ERROR - {question}")
                continue

            elapsed = round(time.perf_counter() - start, 3)
            total += 1
            total_latency += elapsed

            if sources:
                top1 = sources[0]
                top1_source_file = top1.get("source_file", "")
                top1_page = top1.get("page", "")
                top1_score = top1.get("score", "")
                top1_correct_flag = str(top1_source_file).strip() == str(expected_document).strip()
            else:
                top1_source_file = ""
                top1_page = ""
                top1_score = ""
                top1_correct_flag = False

            if top1_correct_flag:
                top1_correct += 1

            rows.append({
                "qid": qid,
                "question": question,
                "expected_topic": expected_topic,
                "expected_document": expected_document,
                "expected_keywords": expected_keywords,
                "success": success,
                "latency_sec": elapsed,
                "top1_source_file": top1_source_file,
                "top1_page": top1_page,
                "top1_score": top1_score,
                "top1_correct": int(top1_correct_flag),
                "answer": answer,
                "manual_answer_label": "",
                "manual_answer_score": "",
                "notes": ""
            })

            print(
                f"[{qid}] done | latency={elapsed}s | "
                f"top1={'OK' if top1_correct_flag else 'MISS'} | "
                f"source={top1_source_file}"
            )

    with open(OUTPUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        fieldnames = [
            "qid",
            "question",
            "expected_topic",
            "expected_document",
            "expected_keywords",
            "success",
            "latency_sec",
            "top1_source_file",
            "top1_page",
            "top1_score",
            "top1_correct",
            "answer",
            "manual_answer_label",
            "manual_answer_score",
            "notes",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    avg_latency = round(total_latency / total, 3) if total > 0 else 0
    top1_acc = round(top1_correct / total * 100, 2) if total > 0 else 0

    print("\n=== Evaluation Summary ===")
    print(f"Total Questions: {total}")
    print(f"Top-1 Retrieval Accuracy: {top1_correct}/{total} = {top1_acc}%")
    print(f"Average Latency: {avg_latency}s")
    print(f"Saved to: {OUTPUT_CSV}")


if __name__ == "__main__":
    run_evaluation()