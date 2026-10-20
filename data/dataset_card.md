# KikuLog Dataset Card

## Overview

This dataset supports supervised fine-tuning of an open-weight language model
for the task of extracting structured work events from informal chrysanthemum
farm work notes written in Indonesian with occasional Japanese terms.

## Task

Given a short informal note (text input) and context (reference date, house
aliases, open cycle summaries), the model must produce a JSON object containing:

- `events`: list of extracted work activities with house, activity code, status,
  date (if mentioned), quantity (if mentioned), and a source evidence quote.
- `clarifications`: list of questions to ask the user when location, stage,
  quantity, or date is ambiguous.

## Data sources

| Source type   | Description |
|---|---|
| `synthetic`   | Hand-authored examples by the project team, reviewed for domain accuracy |
| `adapted`     | Anonymized and paraphrased from real-world notes (not yet collected) |

All examples are labeled by the project author. Real work notes are not included
in this public dataset.

## Schema

Each line in the JSONL files is a JSON object with:

```json
{
  "input": "...",
  "context": {
    "reference_date": "YYYY-MM-DD",
    "house_aliases": ["..."],
    "cycle_summaries": [...]
  },
  "output": {
    "events": [
      {
        "house_id": "...",
        "cycle_id": null,
        "activity": "...",
        "status": "...",
        "occurred_on": "YYYY-MM-DD or null",
        "planned_on":  "YYYY-MM-DD or null",
        "quantity":    null,
        "unit":        null,
        "evidence":    "..."
      }
    ],
    "clarifications": ["..."]
  },
  "source": "synthetic | adapted",
  "split_hint": "train | validation | test"
}
```

## Activity codes

See `app/schemas.py` ActivityCode enum for the full list.

## Curation notes

- Synthetic examples are labeled by a human; no automated generation of ground truth.
- Scenario families (paraphrases of the same situation) are placed in the same split
  to prevent leakage.
- The test split is locked after dataset construction and is not used during training
  or checkpoint selection.
- Corrections from the application UI are not automatically added to training data.

## Limitations

- All current examples are synthetic; coverage of rare edge cases may be limited.
- Varieties, quantities, and Japanese loan terms require expansion.
- Single-user domain; generalization to other farm contexts is not tested.

## Size targets

| Split      | Target |
|---|---:|
| Train      | 500    |
| Validation | 100    |
| Test       | 100    |

Current examples are a pilot set. Expand before full SFT run.
