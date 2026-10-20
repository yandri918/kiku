# Model Card

## Model overview

| Field         | Value |
|---|---|
| Task          | Structured extraction from informal work notes (chrysanthemum farm, Japan) |
| Languages     | Indonesian with Japanese agricultural terms |
| Base model    | To be confirmed — verify availability in your Tinker account |
| Fine-tuning   | Supervised fine-tuning (SFT) with LoRA via Tinker |
| Output format | JSON: events list + clarifications list |

## Intended use

- KikuLog application: extract work events from notes entered by a farm worker.
- Evaluation and research: compare extraction quality before and after fine-tuning.

## Out-of-scope use

- Medical or safety-critical decisions.
- Agronomic recommendations (fertilizer doses, disease diagnosis).
- Replacing any company procedure or official record system.
- Use by anyone other than the authorized farm worker in the demo context.

## Training data

See [../data/dataset_card.md](../data/dataset_card.md).

## Evaluation

See [../evaluation/](../evaluation/) for scripts and reports.
Results are recorded in `evaluation/reports/` after the locked test run.

## Limitations

- Domain is narrow: single chrysanthemum operation in Japan.
- Language mix (Indonesian + Japanese) may differ from other agricultural contexts.
- Sample size is small; metrics have uncertainty — see bootstrap CI in reports.
- Model may fail on rare activity combinations or unfamiliar expressions.

## Base model license

To be documented once the base model is selected and confirmed.
Fine-tuned weights distribution terms depend on the base model license.
Check the base model's license before publishing any weights.

## Bias and risks

- Training data is currently synthetic; real-world distribution may differ.
- Model output is always reviewed by the user before saving; it does not act autonomously.
- Incorrect extractions are corrected at approval time and logged in the audit trail.
