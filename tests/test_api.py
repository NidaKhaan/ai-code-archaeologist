"""Tests for FastAPI endpoints."""

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "AI Code Archaeologist" in data["message"]


def test_greet_endpoint():
    """Test greeting endpoint with valid name."""
    response = client.get("/greet/Alice")
    assert response.status_code == 200
    data = response.json()
    assert "Alice" in data["greeting"]
    assert "timestamp" in data


def test_greet_empty_name():
    """Test greeting endpoint with empty name."""
    response = client.get("/greet/ ")
    assert response.status_code == 400


def test_validate_repo_valid():
    """Test repository validation with valid URL."""
    response = client.get("/validate-repo?url=https://github.com/torvalds/linux")
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True


def test_validate_repo_invalid():
    """Test repository validation with invalid URL."""
    response = client.get("/validate-repo?url=not-a-url")
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is False


def test_analyze_endpoint():
    """Test analyze endpoint."""
    payload = {
        "repo_url": "https://github.com/microsoft/vscode",
        "analyze_dependencies": True,
        "detect_bugs": True,
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
