"""
Integration tests for FastAPI endpoints: health, UI routes, and APIs.
"""

import asyncio
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.persistence import init_db


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    asyncio.run(init_db())


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_ui_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "KikuLog" in response.text
    assert "<html" in response.text.lower()


def test_ui_journal(client):
    response = client.get("/journal")
    assert response.status_code == 200
    assert "<html" in response.text.lower()


def test_ui_agenda(client):
    response = client.get("/agenda")
    assert response.status_code == 200
    assert "<html" in response.text.lower()


def test_ui_evaluation(client):
    response = client.get("/evaluation")
    assert response.status_code == 200
    assert "<html" in response.text.lower()


def test_api_houses_list(client):
    response = client.get("/api/houses/")
    assert response.status_code == 200
    houses = response.json()
    assert isinstance(houses, list)
    assert len(houses) >= 3
    names = [h["display_name"] for h in houses]
    assert "House 1" in names
    assert "House 2" in names
    assert "House 3" in names


def test_api_agenda_today(client):
    response = client.get("/api/agenda/today")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_note_extraction_and_approval_flow(client):
    # 1. Submit note for extraction
    note_payload = {
        "text": "Bongkar house tiga sudah selesai, net sudah dicopot, pasak belum.",
        "working_date": "2026-11-01",
    }
    submit_res = client.post("/api/notes/submit", json=note_payload)
    assert submit_res.status_code == 200
    draft_data = submit_res.json()

    assert "draft_id" in draft_data
    assert "events" in draft_data
    events = draft_data["events"]
    assert len(events) >= 2

    activities = [e["activity"] for e in events]
    assert "clear_old_plants" in activities
    assert "remove_net" in activities

    # 2. Approve draft
    approve_payload = {
        "draft_id": draft_data["draft_id"],
        "approved_events": events,
        "rejected_event_indices": [],
        "user_notes": "All verified",
    }
    approve_res = client.post("/api/notes/approve", json=approve_payload)
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "ok"
    assert approve_res.json()["saved_events_count"] == len(events)

    # 3. Verify house journal has recorded events
    houses = client.get("/api/houses/").json()
    h3 = next(h for h in houses if h["display_name"] == "House 3")
    journal_res = client.get(f"/api/houses/{h3['id']}/journal")
    assert journal_res.status_code == 200
    journal_events = journal_res.json()
    assert len(journal_events) >= len(events)


def test_note_ambiguous_clarification(client):
    note_payload = {
        "text": "House B sudah dibuka.",
        "working_date": "2026-11-02",
    }
    res = client.post("/api/notes/submit", json=note_payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["clarifications"]) > 0
    assert any("clarify" in c.lower() for c in data["clarifications"])
