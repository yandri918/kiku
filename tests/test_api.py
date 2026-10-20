"""
Integration tests for FastAPI endpoints: health, UI routes, and APIs.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.persistence import init_db
import asyncio


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
    assert isinstance(response.json(), list)


def test_api_agenda_today(client):
    response = client.get("/api/agenda/today")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
