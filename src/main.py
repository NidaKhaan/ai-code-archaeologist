"""Main FastAPI application for AI Code Archaeologist."""

from fastapi import FastAPI, HTTPException
from datetime import datetime
from src.utils import greet, validate_github_url
from src.models import GreetingResponse, RepositoryValidation, AnalysisRequest

app = FastAPI(
    title="AI Code Archaeologist",
    description="Intelligent code analysis powered by AI",
    version="0.1.0",
)


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "message": "AI Code Archaeologist API",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/greet/{name}", response_model=GreetingResponse)
async def greet_user(name: str):
    """Greet a user by name."""
    if not name.strip():
        raise HTTPException(status_code=400, detail="Name cannot be empty")

    return GreetingResponse(greeting=greet(name), timestamp=datetime.now().isoformat())


@app.get("/validate-repo", response_model=RepositoryValidation)
async def validate_repository(url: str):
    """Validate if a GitHub repository URL is valid."""
    is_valid = validate_github_url(url)

    return RepositoryValidation(
        url=url,
        is_valid=is_valid,
        message="Valid GitHub repository URL" if is_valid else "Invalid URL format",
        details="Repository structure: owner/repo" if not is_valid else None,
    )


@app.post("/analyze", response_model=dict)
async def analyze_repository(request: AnalysisRequest):
    """
    Analyze a GitHub repository (placeholder for now).
    This will be fully implemented in Week 2-3.
    """
    return {
        "status": "queued",
        "repo_url": str(request.repo_url),
        "message": "Analysis pipeline coming in Week 2!",
        "options": {
            "analyze_dependencies": request.analyze_dependencies,
            "detect_bugs": request.detect_bugs,
        },
    }
