"""Houses and crop cycles router."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.persistence import get_session, House, CropCycle, WorkEvent
from app.schemas import HouseCreate, CycleCreate

router = APIRouter()


@router.get("/", summary="List all houses")
async def list_houses(db: AsyncSession = Depends(get_session)):
    stmt = (
        select(House)
        .options(selectinload(House.cycles))
        .where(House.is_active == True)
        .order_by(House.display_name)
    )
    result = await db.execute(stmt)
    houses = result.scalars().all()

    return [
        {
            "id": str(h.id),
            "display_name": h.display_name,
            "aliases": h.aliases or [],
            "is_active": h.is_active,
            "active_cycle": (
                {
                    "id": str(c.id),
                    "planting_date": c.planting_date.isoformat(),
                    "variety": c.variety,
                    "status": c.status,
                }
                if (c := next((cyc for cyc in h.cycles if cyc.status == "active"), None))
                else None
            ),
        }
        for h in houses
    ]


@router.post("/", summary="Create a house")
async def create_house(payload: HouseCreate, db: AsyncSession = Depends(get_session)):
    house = House(
        display_name=payload.display_name,
        aliases=payload.aliases,
        is_active=True,
    )
    db.add(house)
    await db.commit()
    await db.refresh(house)
    return {
        "id": str(house.id),
        "display_name": house.display_name,
        "aliases": house.aliases,
        "is_active": house.is_active,
    }


@router.post("/{house_id}/cycles", summary="Create a crop cycle for a house")
async def create_cycle(house_id: str, payload: CycleCreate, db: AsyncSession = Depends(get_session)):
    try:
        h_uuid = UUID(house_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid house UUID")

    house = await db.get(House, h_uuid)
    if not house:
        raise HTTPException(status_code=404, detail="House not found")

    cycle = CropCycle(
        house_id=h_uuid,
        planting_date=payload.planting_date,
        status="active",
        variety=payload.variety,
    )
    db.add(cycle)
    await db.commit()
    await db.refresh(cycle)
    return {
        "id": str(cycle.id),
        "house_id": str(cycle.house_id),
        "planting_date": cycle.planting_date.isoformat(),
        "variety": cycle.variety,
        "status": cycle.status,
    }


@router.get("/{house_id}/journal", summary="Get journal entries for a house")
async def get_journal(house_id: str, db: AsyncSession = Depends(get_session)):
    try:
        h_uuid = UUID(house_id)
    except ValueError:
        # Check by display name or alias if not a valid UUID string
        result = await db.execute(select(House).where(House.display_name == house_id))
        house = result.scalars().first()
        if not house:
            return []
        h_uuid = house.id

    stmt = (
        select(WorkEvent)
        .where(WorkEvent.house_id == h_uuid)
        .order_by(WorkEvent.occurred_on.desc(), WorkEvent.created_at.desc())
    )
    result = await db.execute(stmt)
    events = result.scalars().all()

    return [
        {
            "id": str(e.id),
            "house_id": str(e.house_id) if e.house_id else None,
            "cycle_id": str(e.cycle_id) if e.cycle_id else None,
            "activity": e.activity,
            "status": e.status,
            "occurred_on": e.occurred_on.isoformat() if e.occurred_on else None,
            "planned_on": e.planned_on.isoformat() if e.planned_on else None,
            "quantity": e.quantity,
            "unit": e.unit,
            "variety": e.variety,
            "evidence": e.evidence,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in events
    ]
