"""
Database models (SQLAlchemy) and persistence helpers.
Implements the minimum data model from blueprint section 11.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, Column, Date, DateTime, Enum, Float,
    ForeignKey, Integer, JSON, String, Text, UniqueConstraint, Uuid,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, relationship
import uuid

from app.config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(settings.database_url, echo=False)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


# ---------------------------------------------------------------------------
# ORM models
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    pass


class House(Base):
    __tablename__ = "houses"
    id           = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    display_name = Column(String(100), nullable=False, unique=True)
    aliases      = Column(JSON, nullable=False, default=list)
    is_active    = Column(Boolean, nullable=False, default=True)
    created_at   = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    cycles  = relationship("CropCycle", back_populates="house")
    events  = relationship("WorkEvent", back_populates="house")


class CropCycle(Base):
    __tablename__ = "crop_cycles"
    id            = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    house_id      = Column(Uuid(as_uuid=True), ForeignKey("houses.id"), nullable=False)
    planting_date = Column(Date, nullable=False)
    status        = Column(String(20), nullable=False, default="active")
    variety       = Column(String(100), nullable=True)
    created_at    = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    house  = relationship("House", back_populates="cycles")
    events = relationship("WorkEvent", back_populates="cycle")


class RawNote(Base):
    __tablename__ = "raw_notes"
    id           = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text         = Column(Text, nullable=False)
    input_time   = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    working_date = Column(Date, nullable=True)
    author       = Column(String(100), nullable=True)
    is_demo      = Column(Boolean, nullable=False, default=False)

    drafts = relationship("DraftExtraction", back_populates="note")


class DraftExtraction(Base):
    __tablename__ = "draft_extractions"
    id            = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    note_id       = Column(Uuid(as_uuid=True), ForeignKey("raw_notes.id"), nullable=False)
    model_version = Column(String(200), nullable=False)
    result        = Column(JSON, nullable=False)          # raw ModelDraft dict
    clarifications = Column(JSON, nullable=False, default=list)
    review_status = Column(String(20), nullable=False, default="pending")
    created_at    = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    note   = relationship("RawNote", back_populates="drafts")
    events = relationship("WorkEvent", back_populates="draft")


class WorkEvent(Base):
    __tablename__ = "work_events"
    id            = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cycle_id      = Column(Uuid(as_uuid=True), ForeignKey("crop_cycles.id"), nullable=True)
    house_id      = Column(Uuid(as_uuid=True), ForeignKey("houses.id"), nullable=True)
    draft_id      = Column(Uuid(as_uuid=True), ForeignKey("draft_extractions.id"), nullable=True)
    activity      = Column(String(50), nullable=False)
    status        = Column(String(20), nullable=False)
    occurred_on   = Column(Date, nullable=True)
    planned_on    = Column(Date, nullable=True)
    quantity      = Column(Float, nullable=True)
    unit          = Column(String(30), nullable=True)
    variety       = Column(String(100), nullable=True)
    evidence      = Column(Text, nullable=True)
    approved_by   = Column(String(100), nullable=True)
    created_at    = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    house  = relationship("House", back_populates="events")
    cycle  = relationship("CropCycle", back_populates="events")
    draft  = relationship("DraftExtraction", back_populates="events")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id         = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity     = Column(String(50), nullable=False)
    entity_id  = Column(Uuid(as_uuid=True), nullable=False)
    before     = Column(JSON, nullable=True)
    after      = Column(JSON, nullable=True)
    actor      = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"
    id                    = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_label           = Column(String(200), nullable=False)
    dataset_hash          = Column(String(64), nullable=False)
    config                = Column(JSON, nullable=False, default=dict)
    event_exact_match     = Column(Float, nullable=True)
    schema_validity       = Column(Float, nullable=True)
    clarification_f1      = Column(Float, nullable=True)
    unsupported_claim_rate = Column(Float, nullable=True)
    latency_p50_ms        = Column(Float, nullable=True)
    latency_p95_ms        = Column(Float, nullable=True)
    cost_usd              = Column(Float, nullable=True)
    n_samples             = Column(Integer, nullable=False, default=0)
    notes                 = Column(Text, nullable=True)
    created_at            = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# DB init
# ---------------------------------------------------------------------------

async def seed_initial_data():
    from datetime import date, timedelta
    from sqlalchemy import select

    async with async_session_factory() as session:
        result = await session.execute(select(House))
        if result.scalars().first() is None:
            today = date.today()
            h1 = House(
                display_name="House 1",
                aliases=["house 1", "house_1", "h1", "1", "satu", "a", "house a"],
                is_active=True,
            )
            h2 = House(
                display_name="House 2",
                aliases=["house 2", "house_2", "h2", "2", "dua", "b", "house b"],
                is_active=True,
            )
            h3 = House(
                display_name="House 3",
                aliases=["house 3", "house_3", "h3", "3", "tiga", "c", "house c"],
                is_active=True,
            )
            session.add_all([h1, h2, h3])
            await session.flush()

            # Synthetic active cycles from demo script:
            # House 1: ~18 days after planting
            # House 2: ~14 days after planting
            cycle1 = CropCycle(
                house_id=h1.id,
                planting_date=today - timedelta(days=18),
                status="active",
                variety="Seiko",
            )
            cycle2 = CropCycle(
                house_id=h2.id,
                planting_date=today - timedelta(days=14),
                status="active",
                variety="Iwa",
            )
            session.add_all([cycle1, cycle2])
            await session.commit()
            logger.info("Seeded initial synthetic houses and active cycles.")


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema verified.")
    await seed_initial_data()


async def get_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session

