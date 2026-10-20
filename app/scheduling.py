"""
Deterministic schedule engine.

Schedule dates are computed from confirmed work events stored in the database,
not guessed by the model. The engine never automatically marks work as done.

Confirmed rules (from blueprint section 4):
  - uncover_plastic_1: planting_date + 3 to + 4 days after cover_plastic_1
  - uncover_plastic_2: planting_date + 14 days (HST 14)
  - install_net:       planting_date + 14 days (HST 14), independent status
  - cutting:           every 2 days from confirmed reference date
  - packing:           fixed weekly series: Tuesday, Thursday, Sunday (no auto-shift)
  - raise_net:         recurring; each occurrence saved separately, no auto-interval

Unknown intervals (do not add defaults):
  - raise_net inspection interval
  - stake reinstallation
  - time from planting to first cut
"""

from datetime import date, timedelta
from typing import Optional


# Day-of-week constants (Python: Monday=0, Sunday=6)
PACKING_WEEKDAYS = {1, 3, 6}  # Tuesday=1, Thursday=3, Sunday=6


def days_since_planting(planting_date: date, reference_date: date) -> int:
    """Return HST (hari setelah tanam) for a given reference_date. Planting day = 0."""
    return (reference_date - planting_date).days


def uncover_plastic_1_window(cover_plastic_1_date: date) -> tuple[date, date]:
    """Return (earliest, latest) date for uncover_plastic_1."""
    return cover_plastic_1_date + timedelta(days=3), cover_plastic_1_date + timedelta(days=4)


def uncover_plastic_2_date(planting_date: date) -> date:
    """Return the scheduled date for uncover_plastic_2 (14 HST)."""
    return planting_date + timedelta(days=14)


def install_net_date(planting_date: date) -> date:
    """Return the scheduled date for install_net (14 HST). Independent of uncover_plastic_2."""
    return planting_date + timedelta(days=14)


def next_cutting_dates(reference_date: date, from_date: date, n: int = 7) -> list[date]:
    """
    Return the next n cutting dates starting from from_date,
    using a two-day interval based on reference_date.
    reference_date must be a confirmed past cutting date.
    """
    dates: list[date] = []
    delta = (from_date - reference_date).days
    offset = (-delta) % 2  # days until the next on-cycle date
    current = from_date + timedelta(days=offset)
    while len(dates) < n:
        dates.append(current)
        current += timedelta(days=2)
    return dates


def next_packing_dates(from_date: date, n: int = 7) -> list[date]:
    """
    Return the next n packing dates from from_date.
    Packing always falls on Tuesday, Thursday, or Sunday.
    Packing schedule does not shift when the cutting schedule changes.
    """
    dates: list[date] = []
    current = from_date
    while len(dates) < n:
        if current.weekday() in PACKING_WEEKDAYS:
            dates.append(current)
        current += timedelta(days=1)
    return dates


def compute_pending_tasks(
    planting_date: Optional[date],
    cover_plastic_1_date: Optional[date],
    completed_activities: set[str],
    today: date,
) -> list[dict]:
    """
    Return a list of pending scheduled tasks for a single crop cycle.
    Only generates tasks for activities with known rules.
    Does not generate tasks for activities with unknown intervals.

    Returns a list of dicts with keys:
      activity, window_start, window_end, source
    """
    tasks: list[dict] = []

    if cover_plastic_1_date and "uncover_plastic_1" not in completed_activities:
        w_start, w_end = uncover_plastic_1_window(cover_plastic_1_date)
        tasks.append({
            "activity": "uncover_plastic_1",
            "window_start": w_start,
            "window_end": w_end,
            "source": "rule:cover_plastic_1+3-4",
        })

    if planting_date:
        hst14 = planting_date + timedelta(days=14)
        if "uncover_plastic_2" not in completed_activities:
            tasks.append({
                "activity": "uncover_plastic_2",
                "window_start": hst14,
                "window_end": hst14,
                "source": "rule:planting+14hst",
            })
        if "install_net" not in completed_activities:
            tasks.append({
                "activity": "install_net",
                "window_start": hst14,
                "window_end": hst14,
                "source": "rule:planting+14hst",
            })

    return tasks
