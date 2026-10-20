"""Notes router: submit a note, retrieve a draft, approve or reject."""

from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.extraction import call_model
from app.persistence import AuditLog, CropCycle, DraftExtraction, House, RawNote, WorkEvent, get_session
from app.schemas import DraftReviewRequest, NoteSubmit

router = APIRouter()


async def _resolve_house_and_cycle(house_ref: str | None, db: AsyncSession) -> tuple[UUID | None, UUID | None]:
    """Helper to resolve a string house reference (e.g. 'house_1' or name) to House and active CropCycle UUIDs."""
    if not house_ref:
        return None, None

    # Check if already a valid UUID
    try:
        h_uuid = UUID(house_ref)
        house = await db.get(House, h_uuid)
        if house:
            stmt = select(CropCycle).where(CropCycle.house_id == house.id, CropCycle.status == "active")
            cycle_res = await db.execute(stmt)
            cycle = cycle_res.scalars().first()
            return house.id, (cycle.id if cycle else None)
    except ValueError:
        pass

    # Match by display name or alias
    clean_ref = house_ref.lower().replace("_", " ").strip()
    result = await db.execute(select(House).options(selectinload(House.cycles)))
    houses = result.scalars().all()

    for h in houses:
        aliases_clean = [a.lower().replace("_", " ").strip() for a in (h.aliases or [])]
        if (
            clean_ref == h.display_name.lower().replace("_", " ").strip()
            or clean_ref in aliases_clean
            or clean_ref.endswith(h.display_name.lower()[-1])  # e.g. "house_1" ends with "1" matching "House 1"
        ):
            active_c = next((c for c in h.cycles if c.status == "active"), None)
            return h.id, (active_c.id if active_c else None)

    return None, None


@router.post("/submit", summary="Submit a work note for extraction")
async def submit_note(payload: NoteSubmit, db: AsyncSession = Depends(get_session)):
    """
    Accept a raw note, call the model/baseline extractor, and return a draft for review.
    Persists RawNote and DraftExtraction in pending status.
    """
    ref_date = payload.working_date or date.today()

    # Load houses and cycle context
    result = await db.execute(select(House).options(selectinload(House.cycles)).where(House.is_active == True))
    houses = result.scalars().all()

    house_aliases = []
    cycle_summaries = []
    for h in houses:
        house_aliases.extend(h.aliases or [])
        house_aliases.append(h.display_name)
        active_c = next((c for c in h.cycles if c.status == "active"), None)
        if active_c:
            hst = (ref_date - active_c.planting_date).days
            cycle_summaries.append({
                "house_id": f"house_{h.display_name.lower().replace('house ', '')}",
                "planting_date": active_c.planting_date.isoformat(),
                "hst": hst,
                "variety": active_c.variety,
            })

    # Save RawNote
    raw_note = RawNote(
        text=payload.text,
        working_date=ref_date,
        is_demo=False,
    )
    db.add(raw_note)
    await db.flush()

    # Extract draft via Tinker / baseline
    draft = await call_model(
        note_text=payload.text,
        reference_date=ref_date,
        house_aliases=house_aliases,
        cycle_summaries=cycle_summaries,
    )

    # Save DraftExtraction record
    draft_record = DraftExtraction(
        note_id=raw_note.id,
        model_version=draft.model_version,
        result={"events": [e.model_dump(mode="json") for e in draft.events]},
        clarifications=draft.clarifications,
        review_status="pending",
    )
    db.add(draft_record)
    await db.commit()
    await db.refresh(draft_record)

    return {
        "draft_id": str(draft_record.id),
        "note_id": str(raw_note.id),
        "events": [e.model_dump(mode="json") for e in draft.events],
        "clarifications": draft.clarifications,
        "model_version": draft.model_version,
    }


@router.post("/approve", summary="Approve or correct a draft and save events")
async def approve_draft(payload: DraftReviewRequest, db: AsyncSession = Depends(get_session)):
    """
    Save approved events after user review. Discard rejected ones.
    Creates an audit log entry for transparency.
    """
    draft = await db.get(DraftExtraction, payload.draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    saved_events = []
    for event_data in payload.approved_events:
        house_id, cycle_id = await _resolve_house_and_cycle(event_data.house_id, db)

        work_event = WorkEvent(
            cycle_id=cycle_id,
            house_id=house_id,
            draft_id=draft.id,
            activity=event_data.activity.value if hasattr(event_data.activity, "value") else str(event_data.activity),
            status=event_data.status.value if hasattr(event_data.status, "value") else str(event_data.status),
            occurred_on=event_data.occurred_on,
            planned_on=event_data.planned_on,
            quantity=event_data.quantity,
            unit=event_data.unit,
            variety=event_data.variety,
            evidence=event_data.evidence,
            approved_by="worker",
        )
        db.add(work_event)
        saved_events.append(work_event)

    # Update draft review status
    draft.review_status = "approved"

    # Log audit entry
    audit = AuditLog(
        entity="draft_extraction",
        entity_id=draft.id,
        before={"review_status": "pending"},
        after={
            "review_status": "approved",
            "saved_count": len(saved_events),
            "user_notes": payload.user_notes,
        },
        actor="worker",
    )
    db.add(audit)

    await db.commit()

    return {
        "status": "ok",
        "saved_events_count": len(saved_events),
    }


@router.get("/{note_id}", summary="Get a raw note and its draft")
async def get_note(note_id: str, db: AsyncSession = Depends(get_session)):
    try:
        n_uuid = UUID(note_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid note UUID")

    note = await db.get(RawNote, n_uuid)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    stmt = select(DraftExtraction).where(DraftExtraction.note_id == note.id).order_by(DraftExtraction.created_at.desc())
    res = await db.execute(stmt)
    drafts = res.scalars().all()

    return {
        "id": str(note.id),
        "text": note.text,
        "working_date": note.working_date.isoformat() if note.working_date else None,
        "input_time": note.input_time.isoformat() if note.input_time else None,
        "drafts": [
            {
                "id": str(d.id),
                "model_version": d.model_version,
                "review_status": d.review_status,
                "result": d.result,
                "clarifications": d.clarifications,
            }
            for d in drafts
        ],
    }
