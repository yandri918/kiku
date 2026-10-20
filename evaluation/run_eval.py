"""
Evaluation runner.

Runs the baseline model and the fine-tuned checkpoint on the locked test set.
Writes raw predictions to evaluation/reports/.

Usage:
  python evaluation/run_eval.py --test-file training/data/test.jsonl \
      --baseline-model <base-model-id> \
      --finetuned-model <checkpoint-id> \
      --output-dir evaluation/reports/

IMPORTANT:
  - Run this script only after training is complete and the test set is locked.
  - Do not use the test set for checkpoint selection; use the validation set only.
  - The test set must not be used for any tuning before this final evaluation.
"""

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import httpx


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def build_prompt(example: dict) -> str:
    """Reconstruct the inference prompt from a test example."""
    inp = example.get("input", "")
    ctx = example.get("context", {})
    houses_str = ", ".join(ctx.get("house_aliases", [])) or "none"
    ref_date   = ctx.get("reference_date", "unknown")
    cycles_str = json.dumps(ctx.get("cycle_summaries", []), ensure_ascii=False)

    return (
        "You are a work-log assistant for a chrysanthemum farm in Japan.\n"
        "Extract all work activities mentioned in the note below.\n"
        "Return ONLY valid JSON matching the schema. Do not add activities not mentioned.\n"
        "If location, stage, date, or quantity is ambiguous, add a clarification question.\n\n"
        f"Reference date: {ref_date}\n"
        f"Known houses/aliases: {houses_str}\n"
        f"Open cycle context: {cycles_str}\n\n"
        f"Note:\n{inp}\n\n"
        '{"events":[...],"clarifications":[...]}'
    )


def call_model_sync(prompt: str, model_id: str, api_key: str, endpoint: str, timeout: int) -> dict:
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 1024,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    t0 = time.monotonic()
    resp = httpx.post(f"{endpoint}/chat/completions", json=payload, headers=headers, timeout=timeout)
    latency_ms = (time.monotonic() - t0) * 1000
    resp.raise_for_status()
    raw = resp.json()["choices"][0]["message"]["content"]
    try:
        output = json.loads(raw)
    except json.JSONDecodeError:
        output = {"parse_error": raw}
    return {"output": output, "latency_ms": latency_ms, "raw": raw}


def run_eval(test_examples: list[dict], model_id: str, label: str,
             api_key: str, endpoint: str, timeout: int) -> list[dict]:
    results = []
    for i, ex in enumerate(test_examples):
        print(f"  [{label}] {i+1}/{len(test_examples)}", end="\r")
        prompt = build_prompt(ex)
        try:
            result = call_model_sync(prompt, model_id, api_key, endpoint, timeout)
        except Exception as e:
            result = {"output": None, "latency_ms": None, "error": str(e)}
        results.append({
            "index":         i,
            "input":         ex.get("input"),
            "expected":      ex.get("output"),
            "predicted":     result.get("output"),
            "latency_ms":    result.get("latency_ms"),
            "error":         result.get("error"),
            "model_label":   label,
            "model_id":      model_id,
        })
    print()
    return results


def save_predictions(results: list[dict], out_path: Path) -> None:
    with out_path.open("w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")
    print(f"Predictions saved to {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Run evaluation on locked test set.")
    parser.add_argument("--test-file",       default="training/data/test.jsonl")
    parser.add_argument("--baseline-model",  required=True, help="Base model ID")
    parser.add_argument("--finetuned-model", required=True, help="Fine-tuned checkpoint ID")
    parser.add_argument("--output-dir",      default="evaluation/reports")
    parser.add_argument("--endpoint",        default=os.environ.get("TINKER_ENDPOINT", ""))
    parser.add_argument("--timeout",         type=int, default=60)
    args = parser.parse_args()

    api_key = os.environ.get("TINKER_API_KEY", "")
    if not api_key:
        print("ERROR: TINKER_API_KEY is not set.")
        sys.exit(1)

    test_path = Path(args.test_file)
    if not test_path.exists():
        print(f"Test file not found: {test_path}")
        sys.exit(1)

    dataset_hash = sha256_file(test_path)
    print(f"Test set: {test_path} (sha256: {dataset_hash[:16]}...)")

    with test_path.open(encoding="utf-8") as f:
        examples = [json.loads(line) for line in f if line.strip()]
    print(f"  {len(examples)} test examples")

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    ts = time.strftime("%Y%m%d_%H%M%S")

    print("\nRunning baseline...")
    baseline_results = run_eval(examples, args.baseline_model, "baseline",
                                api_key, args.endpoint, args.timeout)
    save_predictions(baseline_results, out_dir / f"{ts}_baseline.jsonl")

    print("Running fine-tuned...")
    finetuned_results = run_eval(examples, args.finetuned_model, "finetuned",
                                 api_key, args.endpoint, args.timeout)
    save_predictions(finetuned_results, out_dir / f"{ts}_finetuned.jsonl")

    print(f"\nDataset hash (record this): {dataset_hash}")
    print("Run evaluation/score.py to compute metrics.")


if __name__ == "__main__":
    main()
