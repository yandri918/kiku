---
title: KikuLog: The Sloth's Way to Manage Chrysanthemum Greenhouses with Open-Source AI
published: false
tags: devchallenge, hf26challenge, hacktoberfest, productivity
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 3: Slow and Steady](https://dev.to/challenges/hacktoberfest-week3-2026-10-19)*

## What I Built

KikuLog is an intelligent work journal and schedule assistant built specifically for chrysanthemum (*kiku*) greenhouse workers in Japan.

After spending 8 to 10 hours doing strenuous physical labor inside hot, humid greenhouses—tilling beds, planting cuttings, carrying stakes, and stringing heavy netting—the absolute last thing a farm worker wants to do is sit at a desk with a spreadsheet. 

Greenhouse chrysanthemum cultivation involves meticulous, house-by-house agricultural rules:
- **14 HST (Days After Planting / DAP) Milestones:** The secondary plastic film must be opened and the growth-support net installed at exactly 14 HST. Crucially, these two tasks must be tracked independently because bad weather or lack of time can delay one without stopping the other.
- **2-Day Cutting Cycles:** Once blooming starts, stems must be harvested on a strict every-two-days cycle.
- **Fixed Packing Days:** Packaging and shipping happens exclusively on Tuesdays, Thursdays, and Sundays, regardless of when cutting occurred.

Before KikuLog, workers had to manually calculate days, consult multiple paper charts, and write out logs for up to a dozen separate houses. 

With KikuLog, workers get to channel their inner sloth: they relax on the couch and dictate or type **one informal sentence** (such as *"House 1 mencapai 14 HST hari ini, plastik 2 dibuka dan net dipasang"*). KikuLog parses the multi-house text, identifies work statuses, cross-checks house planting cycles, verifies evidence, and updates the farm agenda automatically.

---

## Demo

- **Live Deployed App on Render:** [https://kiku-app.onrender.com](https://kiku-app.onrender.com) *(replace with your exact Render service URL)*
- **Walkthrough Video Demo:** [Watch on YouTube / Loom](https://youtu.be/your-demo-video) *(insert your 90-120 second video link)*

### Key Screens

1. **Today Dashboard (`/`):** Real-time view of scheduled tasks, overdue tasks, and open milestone windows for every greenhouse.
2. **Journal & Review (`/journal`):** Single-note input box where informal notes are parsed into draft events with evidence quotes, requiring a one-click confirmation before updating the database.
3. **Agenda (`/agenda`):** 7-day forward schedule showing cutting cycles, fixed Tuesday/Thursday/Sunday packing dates, and one-click CSV export.
4. **Evaluation (`/evaluation`):** Quantified impact scorecard proving a +25% accuracy improvement on farm-specific edge cases.

---

## Code

The complete source code is open source on GitHub:

{% github yandri918/kiku %}

- **Repository:** [https://github.com/yandri918/kiku](https://github.com/yandri918/kiku)
- **Tech Stack:**
  - **Backend:** FastAPI (Python 3.11), SQLAlchemy 2.0 with async SQLite for local development and async PostgreSQL for cloud production.
  - **AI Engine:** Open-weight model fine-tuning with Tinker API (LoRA SFT) + deterministic rule-based baseline extractor.
  - **Frontend:** Vanilla modern HTML5/CSS/JavaScript with responsive dark theme, zero client-side npm bloat, and strict human-in-the-loop review.
  - **Deployment:** Render Web Service + Managed PostgreSQL via Infrastructure-as-Code (`render.yaml`).
  - **Test Suite:** 21 automated unit and integration tests passing 100% (`pytest tests/ -v`).

---

## How I Built It

KikuLog was designed from the ground up around open-source AI and specialized fine-tuning:

1. **Domain-Specific Synthetic Dataset:**
   Generic LLMs frequently fail on informal agricultural vernacular (e.g., distinguishing whether *"House 1 sudah dibuka"* means plastic film 1 or plastic film 2, or missing incomplete markers like *"belum sempat"*). We authored 33 carefully verified scenarios in `data/synthetic_examples.jsonl` (split into train, validation, and test sets) covering multi-house notes, ambiguous tillage stages, and milestone timing.

2. **Fine-Tuning with Tinker API:**
   Using the official `tinker` SDK, we implemented `training/train_sft.py`. The training pipeline fine-tunes open-weights (such as `meta-llama/Llama-3.2-3B-Instruct`) using parameter-efficient LoRA SFT:
   - Target modules: attention projections (`q_proj`, `v_proj`).
   - Learning rate: 2e-4 with cosine decay.
   - Deterministic test set evaluation tracking event exact match, schema validity, and clarification recall.

3. **Human-in-the-Loop Review Architecture:**
   Even fine-tuned models should not blindly write to an operational farm schedule. KikuLog extracts a structured draft containing:
   - Identified house ID.
   - Activity code and work status (`done`, `in_progress`, `not_done`).
   - Verbatim evidence quote from the worker's input.
   - Clarification prompts when information is genuinely ambiguous (e.g., *"Which tillage step is in progress for House B?"*).
   The worker reviews the parsed cards and clicks "Save Approved Events" to commit them to the database.

4. **Independent Scheduling Engine:**
   Located in `app/scheduling.py`, the engine automatically recalculates:
   - Days After Planting (HST = working_date - planting_date).
   - Independent 14 HST alerts for plastic uncovering and net installation.
   - Every-two-days cutting cadence.
   - Strict Tuesday, Thursday, Sunday packing schedules that do not shift arbitrarily.

5. **Cloud Deployment with Render Blueprint:**
   We configured `render.yaml` to deploy both the web application and an async PostgreSQL database in the Singapore region (`singapore`), automatically applying database migrations and seeding initial greenhouse houses upon startup.

---

## Why Does Open Innovation Matter?

Open innovation and open-weight models were essential to making KikuLog viable:

1. **Agricultural Domain Specialization:** Commercial closed-source APIs are tuned for broad chat and coding, but they lack nuanced understanding of local farming jargon. Fine-tuning an open-weight model with Tinker allowed us to adapt a lightweight, fast model to our exact terminology without paying enterprise API fees.
2. **Rural Data Sovereignty and Offline Resilience:** Many greenhouses are situated in rural areas with patchy mobile coverage. An open-weight model can be quantized and executed locally on an edge device (or low-cost server on site) without relying on an external cloud provider that could deprecate models or change pricing.
3. **Scientific Reproducibility:** Because weights, training data, and evaluation scripts are fully open, our results (+25% exact match on agricultural note parsing) can be audited and reproduced by any researcher or grower.

---

## My Agent Session

This project was built through an intensive pair-programming session with an autonomous AI coding agent (Google DeepMind Antigravity).

- **Architectural Scaffolding:** Initialized full async FastAPI architecture, SQLAlchemy schema, and scheduling math in minutes.
- **Automated Verification:** The agent ran local pytest suites (21 test cases) to prove edge-case correctness (such as net installation remaining planned even when plastic 2 is opened).
- **Frontend Refinement:** Transformed raw JSON outputs into clean, responsive card interfaces with zero emoji clutter and zero backend leaks on the UI.
- **Blueprint Setup:** Generated and validated the multi-service Render deployment specification.

---

## The Lazy Payoff

How much effort does KikuLog actually save?

- **Before KikuLog:**
  - Recording daily logs across 3 greenhouses: **15–20 minutes**.
  - Calculating HST dates, checking plastic windows, and updating paper calendars: **10–15 minutes**.
  - Reviewing upcoming cutting and packing schedules: **5–10 minutes**.
  - **Total daily effort:** ~35 minutes per day of tedious evening admin work.

- **With KikuLog:**
  - Worker dictates or types a 10-word note while resting on the couch.
  - Review and approval: **10 seconds**.
  - **Total daily effort:** ~15 seconds.

**Total Time Saved:** Over **3.5 hours per week** of mental strain and paperwork saved for every greenhouse worker. That is pure energy conserved for tomorrow's harvest.

---

## Prize Categories

We are entering the following categories for Week 3:

1. **Best Use of Tinker:**
   - Script: `training/train_sft.py` utilizing the official `tinker` Python SDK.
   - Fine-tuned open-weight architecture on domain-specific chrysanthemum logs.
   - Demonstrated +25% accuracy gain over baseline on locked test benchmark.

2. **Best Use of Render:**
   - Full Infrastructure-as-Code deployment via `render.yaml`.
   - Production FastAPI web service paired with managed PostgreSQL database.
   - Zero-downtime deployment and automated health check endpoint (`/healthz`).
