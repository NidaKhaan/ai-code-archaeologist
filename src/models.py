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


class CodeSnippet(BaseModel):
    """Model for code snippet analysis."""

    code: str = Field(..., description="The code to analyze")
    language: str = Field(default="python", description="Programming language")
    provider: Optional[str] = Field(
        default=None, description="LLM provider: ollama or groq"
    )


class AIAnalysisResponse(BaseModel):
    """Response from AI analysis."""

    result: str
    provider_used: str
    model_used: str
    tokens_used: int


class CodeAnalysisRequest(BaseModel):
    """Request for code analysis."""

    code: str = Field(..., description="Python code to analyze")
    include_ast: bool = Field(default=True, description="Include AST analysis")
    include_complexity: bool = Field(
        default=True, description="Include complexity metrics"
    )
    include_security: bool = Field(default=True, description="Include security scan")


class AnalysisType(BaseModel):
    """Type of analysis to perform."""

    ast_analysis: bool = Field(default=True)
    complexity_analysis: bool = Field(default=True)
    security_scan: bool = Field(default=True)

    model_config = {
        "json_schema_extra": {
            "example": {
                "repo_url": "https://github.com/torvalds/linux",
                "analyze_dependencies": True,
                "detect_bugs": True,
            }
        }
    }
