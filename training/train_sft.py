"""
Supervised fine-tuning via Tinker API.

This script sends a training job to Tinker using the prepared JSONL splits.
It does not run training locally; training runs on Tinker infrastructure.

Usage:
  python training/train_sft.py --config training/configs/default.yaml

Prerequisites:
  - TINKER_API_KEY must be set in the environment or .env
  - Run training/prepare_data.py first to generate training/data/ splits
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# NOTE: Fill in the actual Tinker SDK / API calls once you have confirmed
# the available models, SDK version, and LoRA parameters in your account.
# Do not hard-code model names or hyperparameters without verifying support.
# ---------------------------------------------------------------------------


def load_config(config_path: Path) -> dict:
    import yaml  # pip install pyyaml
    with config_path.open() as f:
        return yaml.safe_load(f)


def run_training(config: dict) -> None:
    api_key = os.environ.get("TINKER_API_KEY", "")
    if not api_key:
        print("ERROR: TINKER_API_KEY is not set.")
        sys.exit(1)

    train_path = Path(config.get("train_file", "training/data/train.jsonl"))
    val_path   = Path(config.get("val_file",   "training/data/validation.jsonl"))

    for p in [train_path, val_path]:
        if not p.exists():
            print(f"ERROR: Data file not found: {p}")
            sys.exit(1)

    print("Configuration:")
    print(json.dumps(config, indent=2, default=str))
    print()

    # TODO: Replace the block below with actual Tinker SDK calls
    # Example (verify against actual Tinker documentation before running):
    #
    # from tinker import TinkerClient
    # client = TinkerClient(api_key=api_key)
    # job = client.training.create(
    #     base_model=config["base_model"],
    #     train_file=str(train_path),
    #     val_file=str(val_path),
    #     lora_rank=config.get("lora_rank", 8),
    #     learning_rate=config.get("learning_rate"),
    #     num_epochs=config.get("num_epochs"),
    #     batch_size=config.get("batch_size"),
    # )
    # print(f"Training job started: {job.id}")
    # record_run(config, job.id)

    print("train_sft.py: Tinker API integration not yet implemented.")
    print("Fill in the TODO block above once you have confirmed model availability.")


def record_run(config: dict, job_id: str) -> None:
    """Persist run metadata for reproducibility."""
    record = {
        "job_id":     job_id,
        "config":     config,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    out = Path("training/runs") / f"{job_id}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f:
        json.dump(record, f, indent=2, default=str)
    print(f"Run metadata saved to {out}")


def main():
    parser = argparse.ArgumentParser(description="Launch SFT job on Tinker.")
    parser.add_argument("--config", default="training/configs/default.yaml")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Config not found: {config_path}")
        sys.exit(1)

    config = load_config(config_path)
    run_training(config)


if __name__ == "__main__":
    main()
