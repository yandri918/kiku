"""
Model extraction: send a note to the fine-tuned model and validate the output.

The model receives:
  - The raw note text
  - A reference date (working date chosen by the user)
  - The list of active house aliases
  - A summary of relevant open cycles

The model returns a JSON draft (ModelDraft schema).
The application never executes database changes from raw model output.
All changes go through user review first.
"""

import json
import logging
import time
from datetime import date

import httpx

from app.config import settings
from app.schemas import ModelDraft

logger = logging.getLogger(__name__)

# Maximum number of retry attempts on invalid schema output
MAX_RETRIES = 2


def _build_prompt(
    note_text: str,
    reference_date: date,
    house_aliases: list[str],
    cycle_summaries: list[dict],
) -> str:
    """Build the instruction prompt sent to the model."""
    houses_str = ", ".join(house_aliases) if house_aliases else "none provided"
    cycles_str = json.dumps(cycle_summaries, ensure_ascii=False, default=str)
    date_str = reference_date.isoformat()

    return (
        "You are a work-log assistant for a chrysanthemum farm in Japan.\n"
        "Extract all work activities mentioned in the note below.\n"
        "Return ONLY valid JSON matching the schema. Do not add activities not mentioned.\n"
        "If location, stage, date, or quantity is ambiguous, add a clarification question.\n\n"
        f"Reference date: {date_str}\n"
        f"Known houses/aliases: {houses_str}\n"
        f"Open cycle context: {cycles_str}\n\n"
        f"Note:\n{note_text}\n\n"
        "Output format:\n"
        "{\n"
        '  "events": [ { "house_id": ..., "cycle_id": ..., "activity": ...,\n'
        '               "status": ..., "occurred_on": ..., "planned_on": ...,\n'
        '               "quantity": ..., "unit": ..., "evidence": ... } ],\n'
        '  "clarifications": [ "..." ]\n'
        "}"
    )


async def call_model(
    note_text: str,
    reference_date: date,
    house_aliases: list[str],
    cycle_summaries: list[dict],
    model_version: str | None = None,
) -> ModelDraft:
    """
    Call the Tinker-hosted model and return a validated ModelDraft.
    On schema validation failure, retry up to MAX_RETRIES times.
    Raises RuntimeError if all retries fail.
    """
    prompt = _build_prompt(note_text, reference_date, house_aliases, cycle_summaries)
    used_model = model_version or settings.tinker_model_id

    payload = {
        "model": used_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 1024,
    }

    headers = {
        "Authorization": f"Bearer {settings.tinker_api_key}",
        "Content-Type": "application/json",
    }

    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 2):
        try:
            t0 = time.monotonic()
            async with httpx.AsyncClient(timeout=settings.model_timeout_seconds) as client:
                response = await client.post(
                    f"{settings.tinker_endpoint}/chat/completions",
                    json=payload,
                    headers=headers,
                )
            latency_ms = (time.monotonic() - t0) * 1000
            response.raise_for_status()

            raw = response.json()["choices"][0]["message"]["content"]
            logger.debug("Model raw output (attempt %d, %.0fms): %s", attempt, latency_ms, raw)

            parsed = json.loads(raw)
            draft = ModelDraft(
                **parsed,
                model_version=used_model,
                raw_output=raw,
            )
            return draft

        except (httpx.TimeoutException, httpx.HTTPStatusError) as exc:
            logger.warning("Model call failed (attempt %d): %s", attempt, exc)
            last_error = exc
        except (json.JSONDecodeError, Exception) as exc:
            logger.warning("Model output invalid (attempt %d): %s", attempt, exc)
            last_error = exc

    raise RuntimeError(
        f"Model extraction failed after {MAX_RETRIES + 1} attempts. "
        f"Last error: {last_error}"
    )
