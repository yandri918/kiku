"""
Scoring script.

Reads raw prediction JSONL files produced by run_eval.py and computes metrics.
Metrics are defined in blueprint section 9.

Usage:
  python evaluation/score.py \
      --baseline   evaluation/reports/<ts>_baseline.jsonl \
      --finetuned  evaluation/reports/<ts>_finetuned.jsonl \
      --output     evaluation/reports/<ts>_comparison.json
"""

import argparse
import json
import math
from pathlib import Path


REQUIRED_EVENT_FIELDS = {"house_id", "activity", "status"}


def load_predictions(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def is_schema_valid(predicted: dict | None) -> bool:
    if not isinstance(predicted, dict):
        return False
    if "events" not in predicted or "clarifications" not in predicted:
        return False
    if not isinstance(predicted["events"], list):
        return False
    for ev in predicted["events"]:
        if not isinstance(ev, dict):
            return False
        for k in REQUIRED_EVENT_FIELDS:
            if k not in ev:
                return False
    return True


def event_key(ev: dict) -> tuple:
    """Canonical key for matching events (house, activity, status)."""
    return (
        ev.get("house_id") or "",
        ev.get("activity") or "",
        ev.get("status") or "",
    )


def event_exact_match(expected_events: list, predicted_events: list) -> bool:
    """All required events present and no spurious extras."""
    exp_keys  = sorted(event_key(e) for e in expected_events)
    pred_keys = sorted(event_key(e) for e in predicted_events)
    return exp_keys == pred_keys


def compute_event_prf(expected_events: list, predicted_events: list) -> tuple[float, float, float]:
    exp_keys  = [event_key(e) for e in expected_events]
    pred_keys = [event_key(e) for e in predicted_events]

    tp = sum(1 for k in pred_keys if k in exp_keys)
    precision = tp / len(pred_keys) if pred_keys else 1.0
    recall    = tp / len(exp_keys)  if exp_keys  else 1.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return precision, recall, f1


def unsupported_claim(expected_events: list, predicted_events: list) -> bool:
    exp_keys = set(event_key(e) for e in expected_events)
    return any(event_key(p) not in exp_keys for p in predicted_events)


def bootstrap_ci(values: list[float], n_iter: int = 1000, alpha: float = 0.05) -> tuple[float, float]:
    import random
    n = len(values)
    if n == 0:
        return (float("nan"), float("nan"))
    means = sorted(
        sum(random.choices(values, k=n)) / n
        for _ in range(n_iter)
    )
    lo = means[int(alpha / 2 * n_iter)]
    hi = means[int((1 - alpha / 2) * n_iter)]
    return lo, hi


def score_predictions(predictions: list[dict]) -> dict:
    n = len(predictions)
    exact_matches      = 0
    schema_valid       = 0
    unsupported_claims = 0
    latencies: list[float] = []
    f1s: list[float] = []

    for p in predictions:
        expected  = p.get("expected") or {}
        predicted = p.get("predicted")
        exp_events  = expected.get("events", [])
        pred_events = (predicted or {}).get("events", []) if isinstance(predicted, dict) else []

        if is_schema_valid(predicted):
            schema_valid += 1

        if event_exact_match(exp_events, pred_events):
            exact_matches += 1

        _, _, f1 = compute_event_prf(exp_events, pred_events)
        f1s.append(f1)

        if unsupported_claim(exp_events, pred_events):
            unsupported_claims += 1

        if p.get("latency_ms") is not None:
            latencies.append(p["latency_ms"])

    latencies_sorted = sorted(latencies)
    def pct(lst, p):
        if not lst: return None
        idx = int(math.ceil(len(lst) * p / 100)) - 1
        return lst[max(0, idx)]

    em_values = [
        1.0 if event_exact_match(
            (p.get("expected") or {}).get("events", []),
            ((p.get("predicted") or {}).get("events", []) if isinstance(p.get("predicted"), dict) else [])
        ) else 0.0
        for p in predictions
    ]
    ci_lo, ci_hi = bootstrap_ci(em_values)

    return {
        "n":                     n,
        "event_exact_match":     exact_matches / n if n else None,
        "event_exact_match_n":   f"{exact_matches}/{n}",
        "em_ci_95":              (ci_lo, ci_hi),
        "schema_validity":       schema_valid / n if n else None,
        "event_f1_mean":         sum(f1s) / len(f1s) if f1s else None,
        "unsupported_claim_rate": unsupported_claims / n if n else None,
        "latency_p50_ms":        pct(latencies_sorted, 50),
        "latency_p95_ms":        pct(latencies_sorted, 95),
    }


def main():
    parser = argparse.ArgumentParser(description="Score evaluation predictions.")
    parser.add_argument("--baseline",  required=True)
    parser.add_argument("--finetuned", required=True)
    parser.add_argument("--output",    required=True)
    args = parser.parse_args()

    baseline  = load_predictions(Path(args.baseline))
    finetuned = load_predictions(Path(args.finetuned))

    print(f"Baseline:  {len(baseline)} predictions")
    print(f"Fine-tuned: {len(finetuned)} predictions")

    baseline_scores  = score_predictions(baseline)
    finetuned_scores = score_predictions(finetuned)

    report = {
        "baseline":  {"file": args.baseline,  "scores": baseline_scores},
        "finetuned": {"file": args.finetuned, "scores": finetuned_scores},
    }

    print("\n--- Baseline ---")
    print(json.dumps(baseline_scores, indent=2, default=str))
    print("\n--- Fine-tuned ---")
    print(json.dumps(finetuned_scores, indent=2, default=str))

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\nComparison report saved to {out}")


if __name__ == "__main__":
    main()
