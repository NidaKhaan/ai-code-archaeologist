"""Data models for API requests and responses."""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional


class GreetingResponse(BaseModel):
    """Response model for greeting endpoint."""

    greeting: str
    timestamp: Optional[str] = None


class RepositoryValidation(BaseModel):
    """Response model for repository validation."""

    url: str
    is_valid: bool
    message: str
    details: Optional[str] = None


class AnalysisRequest(BaseModel):
    """Request model for code analysis."""

    repo_url: HttpUrl = Field(..., description="GitHub repository URL to analyze")
    analyze_dependencies: bool = Field(
        default=True, description="Analyze project dependencies"
    )
    detect_bugs: bool = Field(default=True, description="Run bug detection")

    model_config = {
        "json_schema_extra": {
            "example": {
                "repo_url": "https://github.com/torvalds/linux",
                "analyze_dependencies": True,
                "detect_bugs": True,
            }
        }
    }
