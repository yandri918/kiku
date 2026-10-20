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
import re
import time
from datetime import date, timedelta
from typing import Optional

import httpx

from app.config import settings
from app.schemas import ActivityCode, DraftEvent, EventStatus, ModelDraft

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


def heuristic_extract(
    note_text: str,
    reference_date: date,
    house_aliases: list[str],
    cycle_summaries: list[dict],
) -> ModelDraft:
    """
    Deterministic rule-based extractor used as a baseline and fallback.
    Extracts events, dates, and produces clarifications when ambiguous.
    """
    lower = note_text.lower().strip()
    events: list[DraftEvent] = []
    clarifications: list[str] = []

    # 1. Location correction check
    if re.search(r"\bbukan\s+(house\s*\w+|\w+)\b.*\b(house\s*\w+|\w+)\b", lower) or "not house" in lower:
        clarifications.append("The note appears to be a location correction. Please confirm the intended house.")
        return ModelDraft(
            events=[],
            clarifications=clarifications,
            model_version="heuristic-baseline",
            raw_output=json.dumps({"events": [], "clarifications": clarifications}),
        )

    # Helper to resolve house ID from text snippet
    def find_house(snippet: str) -> Optional[str]:
        m = re.search(r"\bhouse\s*([0-9a-zA-Z]+|\w+)\b", snippet, re.IGNORECASE)
        if m:
            val = m.group(1).lower()
            word_map = {"satu": "house_1", "dua": "house_2", "tiga": "house_3", "empat": "house_4",
                        "1": "house_1", "2": "house_2", "3": "house_3", "4": "house_4",
                        "a": "house_a", "b": "house_b", "c": "house_c"}
            return word_map.get(val, f"house_{val}")
        # Single letter check: "Net on A", "A has been raised"
        m2 = re.search(r"\b([a-cA-C])\b", snippet)
        if m2:
            return f"house_{m2.group(1).lower()}"
        return None

    # Helper to determine event status
    def get_status(snippet: str) -> EventStatus:
        if any(w in snippet for w in ["belum", "not yet", "tidak"]):
            return EventStatus.not_done
        if any(w in snippet for w in ["tinggal sedikit", "masih", "hampir", "sedang", "still"]):
            return EventStatus.in_progress
        if any(w in snippet for w in ["besok", "tomorrow", "rencana", "plan", "minggu depan", "next week"]):
            return EventStatus.planned
        if any(w in snippet for w in ["ditunda", "postponed", "tunda"]):
            return EventStatus.postponed
        if any(w in snippet for w in ["batal", "cancelled"]):
            return EventStatus.cancelled
        return EventStatus.done

    # Split into clauses / sentences for multi-event handling
    clauses = [c.strip() for c in re.split(r"[,;.]+|\bdan\b|\band\b", note_text) if c.strip()]
    if not clauses:
        clauses = [note_text]

    current_house = find_house(note_text)

    for clause in clauses:
        c_lower = clause.lower()
        clause_house = find_house(clause) or current_house

        # Packing (shared, no house required)
        if "packing" in c_lower:
            st = get_status(c_lower)
            q_match = re.search(r"(\d+)\s*(kardus|box|boxes|ikat)", c_lower)
            qty = float(q_match.group(1)) if q_match else None
            unit = q_match.group(2) if q_match else None
            events.append(
                DraftEvent(
                    house_id=None,
                    cycle_id=None,
                    activity=ActivityCode.packing,
                    status=st,
                    occurred_on=reference_date if st in (EventStatus.done, EventStatus.in_progress) else None,
                    planned_on=reference_date + timedelta(days=1) if st == EventStatus.planned else None,
                    quantity=qty,
                    unit=unit,
                    evidence=clause,
                )
            )
            continue

        # Bongkar house (clear old plants)
        if "bongkar" in c_lower or "cleared" in c_lower:
            st = get_status(c_lower)
            events.append(
                DraftEvent(
                    house_id=clause_house,
                    cycle_id=None,
                    activity=ActivityCode.clear_old_plants,
                    status=st,
                    occurred_on=reference_date if st == EventStatus.done else None,
                    planned_on=reference_date + timedelta(days=1) if st == EventStatus.planned else None,
                    evidence=clause,
                )
            )

        # Net operations
        if "net" in c_lower:
            if any(w in c_lower for w in ["dicopot", "removed", "cabut"]):
                events.append(
                    DraftEvent(
                        house_id=clause_house,
                        cycle_id=None,
                        activity=ActivityCode.remove_net,
                        status=get_status(c_lower),
                        occurred_on=reference_date if get_status(c_lower) == EventStatus.done else None,
                        evidence=clause,
                    )
                )
            elif any(w in c_lower for w in ["naik", "dinaikkan", "raised"]):
                st = get_status(c_lower)
                events.append(
                    DraftEvent(
                        house_id=clause_house,
                        cycle_id=None,
                        activity=ActivityCode.raise_net,
                        status=st,
                        occurred_on=reference_date if st == EventStatus.done else None,
                        evidence=clause,
                    )
                )
            elif any(w in c_lower for w in ["pasang", "dipasang", "install"]):
                st = get_status(c_lower)
                events.append(
                    DraftEvent(
                        house_id=clause_house,
                        cycle_id=None,
                        activity=ActivityCode.install_net,
                        status=st,
                        occurred_on=reference_date if st == EventStatus.done else None,
                        planned_on=reference_date + timedelta(days=1) if st == EventStatus.planned else None,
                        evidence=clause,
                    )
                )
            elif any(w in c_lower for w in ["cek", "periksa", "check", "inspect"]):
                st = get_status(c_lower)
                events.append(
                    DraftEvent(
                        house_id=clause_house,
                        cycle_id=None,
                        activity=ActivityCode.inspect_net,
                        status=st,
                        occurred_on=reference_date if st == EventStatus.done else None,
                        planned_on=reference_date + timedelta(days=1) if st == EventStatus.planned else None,
                        evidence=clause,
                    )
                )

        # Stakes
        if "pasak" in c_lower or "stakes" in c_lower:
            events.append(
                DraftEvent(
                    house_id=clause_house,
                    cycle_id=None,
                    activity=ActivityCode.remove_stakes,
                    status=get_status(c_lower),
                    occurred_on=reference_date if get_status(c_lower) == EventStatus.done else None,
                    evidence=clause,
                )
            )

        # Planting
        if any(w in c_lower for w in ["tanam", "planted", "planting"]):
            st = get_status(c_lower)
            q_match = re.search(r"(\d+)\s*(bibit|seedlings|plants)?", c_lower)
            qty = float(q_match.group(1)) if q_match else None
            unit = q_match.group(2) if q_match and q_match.group(2) else ("bibit" if qty else None)
            events.append(
                DraftEvent(
                    house_id=clause_house,
                    cycle_id=None,
                    activity=ActivityCode.planting,
                    status=st,
                    occurred_on=reference_date if st in (EventStatus.done, EventStatus.in_progress) else None,
                    planned_on=reference_date + timedelta(days=1) if st == EventStatus.planned else None,
                    quantity=qty,
                    unit=unit,
                    evidence=clause,
                )
            )

        # Beds (bedengan)
        if "bedeng" in c_lower:
            st = get_status(c_lower)
            events.append(
                DraftEvent(
                    house_id=clause_house,
                    cycle_id=None,
                    activity=ActivityCode.make_beds,
                    status=st,
                    occurred_on=reference_date if st == EventStatus.done else None,
                    evidence=clause,
                )
            )

        # Fertilization (pupuk dasar)
        if any(w in c_lower for w in ["pupuk", "fertilizer", "fertilization"]):
            st = get_status(c_lower)
            occ = reference_date - timedelta(days=1) if "kemarin" in c_lower else reference_date
            events.append(
                DraftEvent(
                    house_id=clause_house,
                    cycle_id=None,
                    activity=ActivityCode.basal_fertilization,
                    status=st,
                    occurred_on=occ if st == EventStatus.done else None,
                    evidence=clause,
                )
            )

        # Tillage (olah tanah)
        if "olah" in c_lower or "till" in c_lower:
            st = get_status(c_lower)
            occ = reference_date - timedelta(days=1) if "kemarin" in c_lower else reference_date
            planned = reference_date + timedelta(days=1) if "besok" in c_lower else None
            if "dua" in c_lower or "2" in c_lower or "kedua" in c_lower or "again" in c_lower:
                act = ActivityCode.tillage_2
            elif "satu" in c_lower or "1" in c_lower or "pertama" in c_lower:
                act = ActivityCode.tillage_1
            else:
                act = None

            if act:
                events.append(
                    DraftEvent(
                        house_id=clause_house,
                        cycle_id=None,
                        activity=act,
                        status=st,
                        occurred_on=occ if st in (EventStatus.done, EventStatus.in_progress) else None,
                        planned_on=planned,
                        evidence=clause,
                    )
                )
            else:
                clarifications.append("Please clarify which house is being tilled and whether this is 1st tillage (tillage_1) or 2nd tillage (tillage_2).")

        # Uncover plastic (buka plastik)
        if "buka plastik" in c_lower or "uncover" in c_lower or "dibuka" in c_lower or "already opened" in c_lower:
            st = get_status(c_lower)
            cycle_match = next((cyc for cyc in cycle_summaries if cyc.get("house_id") == clause_house), None)
            if "dua" in c_lower or "2" in c_lower or (cycle_match and cycle_match.get("hst", 0) >= 14):
                act = ActivityCode.uncover_plastic_2
            elif "satu" in c_lower or "1" in c_lower or (cycle_match and cycle_match.get("last_activity") == "cover_plastic_1"):
                act = ActivityCode.uncover_plastic_1
            else:
                act = None

            if act:
                events.append(
                    DraftEvent(
                        house_id=clause_house,
                        cycle_id=None,
                        activity=act,
                        status=st,
                        occurred_on=reference_date if st == EventStatus.done else None,
                        evidence=clause,
                    )
                )
            else:
                clarifications.append(f"Please clarify which plastic was uncovered in {clause_house or 'the house'}: 1st uncovering (uncover_plastic_1, pre-planting) or 2nd uncovering (uncover_plastic_2, 14 HST).")

        # Cover plastic (tutup plastik)
        if "tutup plastik" in c_lower or "cover plastic" in c_lower:
            st = get_status(c_lower)
            if "dua" in c_lower or "2" in c_lower:
                act = ActivityCode.cover_plastic_2
            elif "satu" in c_lower or "1" in c_lower or "pertama" in c_lower:
                act = ActivityCode.cover_plastic_1
            else:
                act = None

            if act:
                events.append(
                    DraftEvent(
                        house_id=clause_house,
                        cycle_id=None,
                        activity=act,
                        status=st,
                        occurred_on=reference_date if st == EventStatus.done else None,
                        evidence=clause,
                    )
                )
            else:
                clarifications.append("Please specify which house was covered, and whether it was cover_plastic_1 (soil solarization) or cover_plastic_2 (post-planting).")

        # Cutting (potong)
        if "potong" in c_lower or "cutting" in c_lower:
            st = get_status(c_lower)
            events.append(
                DraftEvent(
                    house_id=clause_house,
                    cycle_id=None,
                    activity=ActivityCode.cutting,
                    status=st,
                    occurred_on=reference_date if st == EventStatus.done else None,
                    evidence=clause,
                )
            )

    # General ambiguity checks
    if "tanam minggu depan" in lower and not any(e.activity == ActivityCode.planting for e in events):
        clarifications.append("Please specify the target house and the exact day/date for planting.")

    if not events and not clarifications:
        clarifications.append("No standard chrysanthemum activity recognized in note. You may enter events manually.")

    return ModelDraft(
        events=events,
        clarifications=clarifications,
        model_version="heuristic-baseline",
        raw_output=json.dumps({"events": [e.model_dump(mode="json") for e in events], "clarifications": clarifications}),
    )


async def call_model(
    note_text: str,
    reference_date: date,
    house_aliases: list[str],
    cycle_summaries: list[dict],
    model_version: str | None = None,
) -> ModelDraft:
    """
    Call the Tinker-hosted model or fallback gracefully to baseline extractor.
    """
    used_model = model_version or settings.tinker_model_id

    # If Tinker credentials or endpoint not set, use deterministic baseline
    if not settings.tinker_api_key or not used_model:
        logger.info("Tinker API key or model ID not configured; using heuristic baseline extractor.")
        return heuristic_extract(note_text, reference_date, house_aliases, cycle_summaries)

    prompt = _build_prompt(note_text, reference_date, house_aliases, cycle_summaries)
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

    logger.warning("All Tinker calls failed (%s). Falling back to heuristic baseline.", last_error)
    return heuristic_extract(note_text, reference_date, house_aliases, cycle_summaries)
