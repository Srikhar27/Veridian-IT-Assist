import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.main import app

client = TestClient(app)

def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "operational"
    assert data["components"]["policy_engine"] == "Operational"
    assert data["stats"]["policies_count"] >= 11

def test_api_dashboard():
    res = client.get("/api/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert "kpis" in data
    assert data["kpis"]["total_requests"] == 15
    assert "category_distribution" in data
    assert "ai_performance" in data

def test_api_policies():
    res = client.get("/api/policies")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 11
    pids = [p["id"] for p in data]
    assert "KB-01" in pids
    assert "KB-ASSET-01" in pids

def test_api_chat_password_reset():
    payload = {
        "query": "I forgot my password",
        "employee": "John Doe",
        "email": "john.doe@veridian-corp.example"
    }
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "Password Reset"
    assert "KB-01" in data["source"]
    assert data["ticket_id"] == "N/A"

def test_api_trace_decision():
    payload = {
        "query": "My laptop is 3.5 years old and completely dead",
        "employee": "Aditi Sharma",
        "email": "aditi.sharma@veridian-corp.example"
    }
    res = client.post("/api/trace", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["stages"]) == 5
    assert data["stages"][0]["name"] == "NLU & Entity Extraction"
    assert data["stages"][3]["name"] == "Deterministic Rule Engine"
    assert data["stages"][4]["name"] == "Final Output & Ticket Synchronization"

def test_api_test_cases_list():
    res = client.get("/api/test-cases")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 12
