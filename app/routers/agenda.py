"""Agenda router: today's tasks, upcoming schedule, and CSV export."""

import csv
import io
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.persistence import CropCycle, House, WorkEvent, get_session
from app.scheduling import (
    PACKING_WEEKDAYS,
    compute_pending_tasks,
    next_cutting_dates,
    next_packing_dates,
)

router = APIRouter()


@router.get("/today", summary="Get today's tasks across all houses")
async def get_today(
    reference_date: date = Query(default=None, description="Override today's date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_session),
):
    target_date = reference_date or date.today()

    # Load active houses with cycles and work events
    stmt = (
        select(House)
        .options(
            selectinload(House.cycles),
            selectinload(House.events),
        )
        .where(House.is_active == True)
        .order_by(House.display_name)
    )
    result = await db.execute(stmt)
    houses = result.scalars().all()

    tasks: list[dict] = []

    # 1. House-specific rule-based pending tasks
    for house in houses:
        active_cycle = next((c for c in house.cycles if c.status == "active"), None)
        if not active_cycle:
            continue

        done_activities = {
            e.activity for e in house.events
            if e.cycle_id == active_cycle.id and e.status == "done"
        }

        # Find cover_plastic_1 date if done
        cp1_event = next(
            (e for e in house.events if e.cycle_id == active_cycle.id and e.activity == "cover_plastic_1" and e.status == "done"),
            None,
        )
        cp1_date = cp1_event.occurred_on if cp1_event else None

        pending = compute_pending_tasks(
            planting_date=active_cycle.planting_date,
            cover_plastic_1_date=cp1_date,
            completed_activities=done_activities,
            today=target_date,
        )

        for p in pending:
            w_start = p["window_start"]
            w_end = p["window_end"]

            is_overdue = target_date > w_end
            is_window = (w_start < w_end) and (w_start <= target_date <= w_end)
            is_scheduled = (target_date == w_start) or is_window or is_overdue

            tasks.append({
                "id": f"{house.id}_{p['activity']}",
                "house_id": str(house.id),
                "house_name": house.display_name,
                "activity": p["activity"],
                "status": "overdue" if is_overdue else "planned",
                "window_start": w_start.isoformat(),
                "window_end": w_end.isoformat(),
                "is_overdue": is_overdue,
                "is_window": is_window,
                "source": p["source"],
            })

    # 2. Check scheduled explicit planned events from notes for today or overdue
    planned_events_stmt = (
        select(WorkEvent)
        .where(WorkEvent.status == "planned")
    )
    res_planned = await db.execute(planned_events_stmt)
    for pe in res_planned.scalars().all():
        if pe.planned_on:
            is_overdue = target_date > pe.planned_on
            house_name = next((h.display_name for h in houses if h.id == pe.house_id), "General")
            tasks.append({
                "id": str(pe.id),
                "house_id": str(pe.house_id) if pe.house_id else None,
                "house_name": house_name,
                "activity": pe.activity,
                "status": "overdue" if is_overdue else "planned",
                "window_start": pe.planned_on.isoformat(),
                "window_end": pe.planned_on.isoformat(),
                "is_overdue": is_overdue,
                "is_window": False,
                "source": f"note_evidence: {pe.evidence or ''}",
            })

    # 3. Packing task if today is Tuesday, Thursday, or Sunday
    if target_date.weekday() in PACKING_WEEKDAYS:
        # Check if packing was already recorded for today
        packing_done = any(
            e.activity == "packing" and e.occurred_on == target_date and e.status == "done"
            for h in houses for e in h.events
        )
        if not packing_done:
            tasks.append({
                "id": f"packing_{target_date.isoformat()}",
                "house_id": None,
                "house_name": "Packing Station",
                "activity": "packing",
                "status": "planned",
                "window_start": target_date.isoformat(),
                "window_end": target_date.isoformat(),
                "is_overdue": False,
                "is_window": False,
                "source": "rule:tue_thu_sun_packing",
            })

    return tasks


@router.get("/upcoming", summary="Get upcoming schedule including packing and cutting")
async def get_upcoming(
    reference_date: date = Query(default=None, description="Starting date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_session),
):
    start = reference_date or date.today()

    # Find the most recent confirmed cutting date to anchor the 2-day cycle
    stmt = (
        select(WorkEvent)
        .where(WorkEvent.activity == "cutting", WorkEvent.status == "done")
        .order_by(WorkEvent.occurred_on.desc())
    )
    res = await db.execute(stmt)
    last_cut_event = res.scalars().first()
    cutting_ref = last_cut_event.occurred_on if (last_cut_event and last_cut_event.occurred_on) else (start - timedelta(days=1))

    packing_dates = next_packing_dates(from_date=start, n=7)
    cutting_dates = next_cutting_dates(reference_date=cutting_ref, from_date=start, n=7)

    return {
        "start_date": start.isoformat(),
        "packing_dates": [d.isoformat() for d in packing_dates],
        "cutting_dates": [d.isoformat() for d in cutting_dates],
    }


@router.get("/export/csv", summary="Export agenda as CSV")
async def export_csv(
    reference_date: date = Query(default=None),
    db: AsyncSession = Depends(get_session),
):
    target_date = reference_date or date.today()
    tasks = await get_today(reference_date=target_date, db=db)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Task ID",
        "House",
        "Activity",
        "Status",
        "Window Start",
        "Window End",
        "Overdue",
        "Source Rule / Evidence",
    ])

    for t in tasks:
        writer.writerow([
            t["id"],
            t["house_name"],
            t["activity"],
            t["status"],
            t["window_start"],
            t["window_end"],
            "Yes" if t.get("is_overdue") else "No",
            t["source"],
        ])

    csv_data = output.getvalue()
    filename = f"kikulog_agenda_{target_date.isoformat()}.csv"

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
