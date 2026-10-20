"""Evaluation router: list runs and comparison data for the UI."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.persistence import get_session

router = APIRouter()


@router.get("/runs", summary="List all evaluation runs")
async def list_runs(db: AsyncSession = Depends(get_session)):
    # TODO: implement in Day 3
    return []


@router.get("/runs/{run_id}", summary="Get a single evaluation run")
async def get_run(run_id: str, db: AsyncSession = Depends(get_session)):
    # TODO: implement in Day 3
    return {"status": "not_implemented"}
