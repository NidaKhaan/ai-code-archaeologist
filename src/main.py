"""Main FastAPI application for AI Code Archaeologist."""

from fastapi import FastAPI
from src.utils import greet, validate_github_url

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


@app.get("/greet/{name}")
async def greet_user(name: str):
    """Greet a user by name."""
    return {"greeting": greet(name)}


@app.get("/validate-repo")
async def validate_repository(url: str):
    """Validate if a GitHub repository URL is valid."""
    is_valid = validate_github_url(url)
    return {
        "url": url,
        "is_valid": is_valid,
        "message": "Valid GitHub repository URL" if is_valid else "Invalid URL",
    }
