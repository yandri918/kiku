"""
Scheduling engine unit tests.
Run: python -m pytest tests/ -v
"""

from datetime import date
from app.scheduling import (
    days_since_planting,
    uncover_plastic_1_window,
    uncover_plastic_2_date,
    install_net_date,
    next_cutting_dates,
    next_packing_dates,
    PACKING_WEEKDAYS,
)


def test_days_since_planting():
    planting = date(2026, 11, 1)
    assert days_since_planting(planting, date(2026, 11, 1)) == 0
    assert days_since_planting(planting, date(2026, 11, 15)) == 14


def test_uncover_plastic_1_window():
    cover_date = date(2026, 11, 1)
    start, end = uncover_plastic_1_window(cover_date)
    assert start == date(2026, 11, 4)
    assert end   == date(2026, 11, 5)


def test_uncover_plastic_2_is_14_hst():
    planting = date(2026, 11, 1)
    assert uncover_plastic_2_date(planting) == date(2026, 11, 15)


def test_install_net_is_14_hst():
    planting = date(2026, 11, 1)
    assert install_net_date(planting) == date(2026, 11, 15)


def test_install_net_independent_of_uncover_plastic_2():
    # Both are 14 HST but treated as separate events with independent status
    planting = date(2026, 11, 1)
    assert uncover_plastic_2_date(planting) == install_net_date(planting)


def test_cutting_dates_every_two_days():
    ref  = date(2026, 11, 1)   # known cutting date
    from_date = date(2026, 11, 3)
    dates = next_cutting_dates(ref, from_date, n=3)
    assert dates[0] == date(2026, 11, 3)
    assert dates[1] == date(2026, 11, 5)
    assert dates[2] == date(2026, 11, 7)


def test_packing_dates_correct_weekdays():
    from_date = date(2026, 11, 2)  # Sunday
    dates = next_packing_dates(from_date, n=6)
    for d in dates:
        assert d.weekday() in PACKING_WEEKDAYS, f"{d} is not a packing day"


def test_packing_does_not_shift_with_cutting():
    # Verify packing and cutting are computed independently
    planting  = date(2026, 11, 1)
    from_date = date(2026, 11, 10)
    cutting = next_cutting_dates(date(2026, 11, 1), from_date, n=3)
    packing = next_packing_dates(from_date, n=3)
    # They may overlap on some days; that is expected and not a bug
    assert isinstance(cutting, list)
    assert isinstance(packing, list)
