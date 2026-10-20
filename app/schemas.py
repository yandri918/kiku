"""
Pydantic schemas for request/response validation and model output contract.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class ActivityCode(str, Enum):
    clear_old_plants  = "clear_old_plants"
    remove_net        = "remove_net"
    remove_stakes     = "remove_stakes"
    tillage_1         = "tillage_1"
    cover_plastic_1   = "cover_plastic_1"
    uncover_plastic_1 = "uncover_plastic_1"
    basal_fertilization = "basal_fertilization"
    tillage_2         = "tillage_2"
    make_beds         = "make_beds"
    planting          = "planting"
    cover_plastic_2   = "cover_plastic_2"
    uncover_plastic_2 = "uncover_plastic_2"
    install_net       = "install_net"
    inspect_net       = "inspect_net"
    raise_net         = "raise_net"
    cutting           = "cutting"
    packing           = "packing"
    other             = "other"


class EventStatus(str, Enum):
    planned     = "planned"
    in_progress = "in_progress"
    done        = "done"
    not_done    = "not_done"
    postponed   = "postponed"
    cancelled   = "cancelled"


class CycleStatus(str, Enum):
    active    = "active"
    completed = "completed"
    cancelled = "cancelled"


# ---------------------------------------------------------------------------
# Model output contract
# ---------------------------------------------------------------------------

class DraftEvent(BaseModel):
    """One activity extracted from a note by the model."""
    house_id: Optional[str] = None
    cycle_id: Optional[str] = None
    activity: ActivityCode
    status: EventStatus
    occurred_on: Optional[date] = None
    planned_on: Optional[date] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    variety: Optional[str] = None
    evidence: str = Field(description="Exact quote from the note that supports this extraction.")
    correction_quote: Optional[str] = None
    notes: Optional[str] = None


class ModelDraft(BaseModel):
    """Full output from one model call."""
    events: list[DraftEvent]
    clarifications: list[str] = Field(default_factory=list)
    model_version: str
    raw_output: Optional[str] = None


# ---------------------------------------------------------------------------
# API request/response schemas
# ---------------------------------------------------------------------------

class NoteSubmit(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    working_date: Optional[date] = None
    house_context: Optional[list[str]] = None


class DraftReviewRequest(BaseModel):
    draft_id: UUID
    approved_events: list[DraftEvent]
    rejected_event_indices: list[int] = Field(default_factory=list)
    user_notes: Optional[str] = None


class HouseCreate(BaseModel):
    display_name: str
    aliases: list[str] = Field(default_factory=list)


class CycleCreate(BaseModel):
    house_id: UUID
    planting_date: date
    variety: Optional[str] = None


class TaskResponse(BaseModel):
    id: UUID
    house_id: Optional[UUID]
    cycle_id: Optional[UUID]
    activity: ActivityCode
    status: EventStatus
    window_start: Optional[date]
    window_end: Optional[date]
    source: str  # "event" or "rule"


class EvaluationRunResult(BaseModel):
    run_id: str
    model_label: str
    dataset_hash: str
    config: dict[str, Any]
    event_exact_match: Optional[float] = None
    schema_validity: Optional[float] = None
    clarification_f1: Optional[float] = None
    unsupported_claim_rate: Optional[float] = None
    latency_p50_ms: Optional[float] = None
    latency_p95_ms: Optional[float] = None
    cost_usd: Optional[float] = None
    n_samples: int
    notes: Optional[str] = None
    created_at: datetime
