# KikuLog

**Work journal and schedule assistant for chrysanthemum farm workers based on experience working in Japan.**

KikuLog turns short informal notes into structured per-house work logs and generates the next day's agenda automatically. The system combines the position of each house in the growing cycle with cutting, packing, and net maintenance schedules.

---

## How it works

1. Enter a note describing what was done (or still needs to be done).
2. The fine-tuned model drafts a structured extraction with source evidence.
3. You review, correct, and approve before anything is saved.
4. The schedule engine recalculates the agenda from confirmed events.

**AI prepares a draft. The user approves changes.**

---

## Features (MVP)

- House and active crop cycle list
- Free-text note input with working date selection
- Multi-activity extraction from a single note
- Source evidence citation for each extracted field
- Clarification prompts for ambiguous location, stage, quantity, or date
- Correction and approval before saving
- Per-house journal and combined agenda view
- CSV export
- Baseline vs. fine-tuned model comparison page
- Demo mode with labeled synthetic data

---

## Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI |
| Database | PostgreSQL (Render Postgres) |
| Model training | Tinker (LoRA supervised fine-tuning) |
| Hosting | Render Web Service |
| Frontend | HTML, CSS, JavaScript (served by FastAPI) |

---

## Project structure

```
kikulog/
  app/               FastAPI backend and web UI
  training/          Dataset preparation and SFT scripts
  evaluation/        Evaluation runner, scoring, and reports
  data/              Synthetic dataset and dataset card
  tests/             Unit and integration tests
  docs/              Architecture, model card, demo script, submission draft
```

---

## Setup

### Requirements

- Python 3.11+
- PostgreSQL database
- Tinker account (for training)
- Render account (for deployment)

### Local development

```bash
git clone https://github.com/<your-username>/kikulog.git
cd kikulog

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env and fill in the required values

uvicorn app.main:app --reload
```

### Environment variables

See [`.env.example`](.env.example) for all required and optional variables.

---

## Evaluation

```bash
# Run baseline and fine-tuned model on the locked test set
python evaluation/run_eval.py --config evaluation/configs/eval_config.yaml

# Score and produce a comparison report
python evaluation/score.py --predictions evaluation/reports/predictions.jsonl
```

Results are written to `evaluation/reports/`. The test set is not used during training or checkpoint selection.

---

## Demo

A live demo running on Render uses isolated synthetic data. Write access is rate-limited. Real work notes are only accessible to authorized users.

Demo link: *(added after deployment)*

---

## Hackathon categories

- **Best Use of Tinker** — supervised fine-tuning of an open-weight model for chrysanthemum work note understanding
- **Best Use of Render** — web application and API hosted on Render Web Service with Render Postgres

Submission: DEV Hacktoberfest Open-Source AI Challenge Week 3, theme "Slow and Steady".

---

## License

See [LICENSE](LICENSE). The base model license and any fine-tuned weight distribution terms are documented separately in [docs/model_card.md](docs/model_card.md).

---

## Credits and AI use disclosure

Concept and domain knowledge: Andriyanto.
Blueprint and code assistance: documented in submission article.
