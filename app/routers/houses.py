"""Houses and crop cycles router."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.persistence import get_session
from app.schemas import HouseCreate, CycleCreate

router = APIRouter()


@router.get("/", summary="List all houses")
async def list_houses(db: AsyncSession = Depends(get_session)):
    # TODO: implement in Day 2
    return []


@router.post("/", summary="Create a house")
async def create_house(payload: HouseCreate, db: AsyncSession = Depends(get_session)):
    # TODO: implement in Day 2
    return {"status": "not_implemented"}


@router.post("/{house_id}/cycles", summary="Create a crop cycle for a house")
async def create_cycle(house_id: str, payload: CycleCreate, db: AsyncSession = Depends(get_session)):
    # TODO: implement in Day 2
    return {"status": "not_implemented"}


@router.get("/{house_id}/journal", summary="Get journal entries for a house")
async def get_journal(house_id: str, db: AsyncSession = Depends(get_session)):
    # TODO: implement in Day 2
    return []
