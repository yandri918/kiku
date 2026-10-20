"""Notes router: submit a note, retrieve a draft, approve or reject."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.persistence import get_session
from app.schemas import NoteSubmit, DraftReviewRequest

router = APIRouter()


@router.post("/submit", summary="Submit a work note for extraction")
async def submit_note(payload: NoteSubmit, db: AsyncSession = Depends(get_session)):
    """
    Accept a raw note, call the model, and return a draft for review.
    Nothing is saved to the database at this point.
    """
    # TODO: implement in Day 2
    return {"status": "not_implemented"}


@router.post("/approve", summary="Approve or correct a draft and save events")
async def approve_draft(payload: DraftReviewRequest, db: AsyncSession = Depends(get_session)):
    """
    Save approved events after user review. Rejected events are discarded.
    An audit log entry is created for each saved event.
    """
    # TODO: implement in Day 2
    return {"status": "not_implemented"}


@router.get("/{note_id}", summary="Get a raw note and its draft")
async def get_note(note_id: str, db: AsyncSession = Depends(get_session)):
    # TODO: implement in Day 2
    return {"status": "not_implemented"}
