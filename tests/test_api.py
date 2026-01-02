"""Tests for FastAPI endpoints."""

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

# Mock API key for testing
VALID_API_KEY = "dev_key_123"
HEADERS = {"X-API-Key": VALID_API_KEY}


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


def test_analyze_endpoint_with_auth():
    """Test analyze endpoint with authentication."""
    payload = {
        "repo_url": "https://github.com/microsoft/vscode",
        "analyze_dependencies": True,
        "detect_bugs": True,
    }
    response = client.post("/analyze", json=payload, headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
    assert "id" in data


def test_analyze_endpoint_without_auth():
    """Test analyze endpoint fails without authentication."""
    payload = {
        "repo_url": "https://github.com/microsoft/vscode",
        "analyze_dependencies": True,
        "detect_bugs": True,
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 401


def test_get_analysis_with_auth():
    """Test getting analysis with authentication."""
    # First create an analysis
    payload = {
        "repo_url": "https://github.com/python/cpython",
        "analyze_dependencies": True,
        "detect_bugs": True,
    }
    create_response = client.post("/analyze", json=payload, headers=HEADERS)
    analysis_id = create_response.json()["id"]

    # Now retrieve it
    response = client.get(f"/analysis/{analysis_id}", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == analysis_id


def test_get_analysis_without_auth():
    """Test getting analysis fails without authentication."""
    response = client.get("/analysis/1")
    assert response.status_code == 401
