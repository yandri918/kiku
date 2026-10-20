"""Agenda router: today's tasks and combined schedule."""

from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.persistence import get_session

router = APIRouter()


@router.get("/today", summary="Get today's tasks across all houses")
async def get_today(
    reference_date: date = Query(default=None, description="Override today's date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_session),
):
    # TODO: implement in Day 2 — calls scheduling.compute_pending_tasks
    return []


@router.get("/export/csv", summary="Export agenda as CSV")
async def export_csv(db: AsyncSession = Depends(get_session)):
    # TODO: implement in Day 3
    return {"status": "not_implemented"}
