# Architecture

## Overview

KikuLog uses a server-rendered web application pattern. The FastAPI backend
serves both the REST API and the HTML UI. This reduces the number of services
to deploy on Render.

## Request flow

```
User (browser)
  |
  | HTTP (form submit / fetch)
  v
FastAPI backend (Render Web Service)
  |--- Validate input (Pydantic)
  |--- Fetch cycle context (PostgreSQL)
  |--- Call model (Tinker endpoint)
  |--- Validate model output (Pydantic)
  |--- Return draft to browser
  |
User reviews draft in UI
  |
  | HTTP (approve endpoint)
  v
FastAPI backend
  |--- Validate approved events
  |--- Write WorkEvent rows (PostgreSQL)
  |--- Write AuditLog row
  |--- Recalculate agenda (scheduling.py)
  |--- Return updated state
```

## Components

| Component         | Location              | Responsibility |
|-------------------|-----------------------|----------------|
| Web UI            | app/ui/               | HTML templates, CSS, JavaScript |
| API routers       | app/routers/          | HTTP endpoints |
| Extraction        | app/extraction.py     | Prompt building, model call, retry |
| Schedule engine   | app/scheduling.py     | Deterministic date calculation |
| ORM / persistence | app/persistence.py    | SQLAlchemy models, DB session |
| Config            | app/config.py         | Environment variable loading |
| Training scripts  | training/             | Dataset prep, SFT launch |
| Evaluation        | evaluation/           | Inference, scoring, reporting |

## Constraints by design

- The model returns a draft; no database write happens from raw model output.
- Schedule dates are computed by `scheduling.py`, not the model.
- Retry on invalid model output; fall back to manual entry on repeated failure.
- API keys are server-side environment variables only.
- Demo mode uses isolated synthetic data and rate limiting.
- All timestamps stored in UTC; working dates stored as local date (Asia/Tokyo).

## What is NOT in this architecture

- Background workers: not needed for MVP because agenda is computed on request.
- Local GPU inference: Render Free does not provide GPU.
- Multi-agent orchestration: out of scope for MVP.
- IoT or hardware integrations: out of scope.
