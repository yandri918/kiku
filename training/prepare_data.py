"""
Prepare the dataset for supervised fine-tuning.

Steps:
  1. Load raw labeled examples from data/synthetic_examples.jsonl
  2. Validate schema compliance
  3. Check for duplicates and cross-split leakage
  4. Write train / validation / test splits to training/data/
  5. Print a summary

Usage:
  python training/prepare_data.py --input data/synthetic_examples.jsonl --seed 42
"""

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

SPLIT_RATIOS = {"train": 0.71, "validation": 0.14, "test": 0.14}  # ~500 / 100 / 100
REQUIRED_INPUT_KEYS = {"input", "output", "source", "split_hint"}
REQUIRED_OUTPUT_KEYS = {"events", "clarifications"}


def sha256_of_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def validate_example(ex: dict, index: int) -> list[str]:
    errors = []
    for k in REQUIRED_INPUT_KEYS:
        if k not in ex:
            errors.append(f"[{index}] Missing key: {k}")
    if "output" in ex:
        out = ex["output"]
        if not isinstance(out, dict):
            errors.append(f"[{index}] 'output' must be a dict")
        else:
            for k in REQUIRED_OUTPUT_KEYS:
                if k not in out:
                    errors.append(f"[{index}] output missing key: {k}")
    return errors


def load_and_validate(path: Path) -> list[dict]:
    examples = []
    all_errors = []
    with path.open(encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                ex = json.loads(line)
            except json.JSONDecodeError as e:
                all_errors.append(f"[{i}] JSON parse error: {e}")
                continue
            errors = validate_example(ex, i)
            all_errors.extend(errors)
            examples.append(ex)

    if all_errors:
        print("Validation errors:")
        for e in all_errors:
            print(" ", e)
        sys.exit(1)

    return examples


def check_leakage(splits: dict[str, list]) -> None:
    """Warn if the same input text appears in more than one split."""
    seen: dict[str, str] = {}
    for split_name, examples in splits.items():
        for ex in examples:
            h = sha256_of_text(ex["input"])
            if h in seen:
                print(f"WARNING: Duplicate input across {seen[h]} and {split_name}: {ex['input'][:60]!r}")
            seen[h] = split_name


def split_examples(examples: list[dict], seed: int) -> dict[str, list]:
    # Honour split_hint if provided ("train", "validation", "test", or "locked_test")
    hinted: dict[str, list] = {"train": [], "validation": [], "test": []}
    free: list[dict] = []

    for ex in examples:
        hint = ex.get("split_hint", "").lower()
        if hint in hinted:
            hinted[hint].append(ex)
        elif hint == "locked_test":
            hinted["test"].append(ex)
        else:
            free.append(ex)

    rng = random.Random(seed)
    rng.shuffle(free)

    n = len(free)
    n_train = int(n * SPLIT_RATIOS["train"])
    n_val   = int(n * SPLIT_RATIOS["validation"])

    hinted["train"]      += free[:n_train]
    hinted["validation"] += free[n_train:n_train + n_val]
    hinted["test"]       += free[n_train + n_val:]

    return hinted


def write_splits(splits: dict[str, list], out_dir: Path) -> dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for split_name, examples in splits.items():
        path = out_dir / f"{split_name}.jsonl"
        with path.open("w", encoding="utf-8") as f:
            for ex in examples:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")
        content = path.read_bytes()
        hashes[split_name] = hashlib.sha256(content).hexdigest()
        print(f"  {split_name}: {len(examples)} examples -> {path} (sha256: {hashes[split_name][:16]}...)")
    return hashes


def main():
    parser = argparse.ArgumentParser(description="Prepare SFT dataset splits.")
    parser.add_argument("--input", default="data/synthetic_examples.jsonl")
    parser.add_argument("--output-dir", default="training/data")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        sys.exit(1)

    print(f"Loading {input_path}...")
    examples = load_and_validate(input_path)
    print(f"  {len(examples)} valid examples loaded.")

    splits = split_examples(examples, seed=args.seed)
    check_leakage(splits)

    print(f"\nWriting splits to {args.output_dir}/")
    hashes = write_splits(splits, Path(args.output_dir))

    print("\nDataset hash summary (record these before training):")
    for split_name, h in hashes.items():
        print(f"  {split_name}: {h}")


if __name__ == "__main__":
    main()
