"""Main FastAPI application for AI Code Archaeologist."""

from fastapi import FastAPI, HTTPException, Depends, Security, Request
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from contextlib import asynccontextmanager
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.utils import greet, validate_github_url
from src.models import GreetingResponse, RepositoryValidation, AnalysisRequest
from src.database import get_db, init_db
from src.db_models import AnalysisResult
from src.auth import verify_api_key
from src.rate_limit import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


app = FastAPI(
    title="AI Code Archaeologist",
    description="Intelligent code analysis powered by AI",
    version="0.1.0",
    lifespan=lifespan,
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/")
@limiter.limit("10/minute")
async def root(request: Request):
    """Root endpoint - API health check."""
    return {
        "message": "AI Code Archaeologist API",
        "status": "running",
        "version": "0.1.0",
        "note": "Use X-API-Key header for authenticated endpoints",
    }


@app.get("/greet/{name}", response_model=GreetingResponse)
@limiter.limit("20/minute")
async def greet_user(request: Request, name: str):
    """Greet a user by name."""
    if not name.strip():
        raise HTTPException(status_code=400, detail="Name cannot be empty")

    return GreetingResponse(greeting=greet(name), timestamp=datetime.now().isoformat())


@app.get("/validate-repo", response_model=RepositoryValidation)
@limiter.limit("30/minute")
async def validate_repository(request: Request, url: str):
    """Validate if a GitHub repository URL is valid."""
    is_valid = validate_github_url(url)

    return RepositoryValidation(
        url=url,
        is_valid=is_valid,
        message="Valid GitHub repository URL" if is_valid else "Invalid URL format",
        details="Repository structure: owner/repo" if not is_valid else None,
    )


@app.post("/analyze")
@limiter.limit("5/minute")
async def analyze_repository(
    request: Request,
    analysis_request: AnalysisRequest,
    db: AsyncSession = Depends(get_db),
    api_key_info: dict = Security(verify_api_key),
):
    """
    Analyze a GitHub repository and store results in database.
    Requires API key authentication.
    """
    # Validate URL
    if not validate_github_url(str(analysis_request.repo_url)):
        raise HTTPException(status_code=400, detail="Invalid GitHub repository URL")

    # Create analysis record
    analysis = AnalysisResult(
        repo_url=str(analysis_request.repo_url),
        status="queued",
        analyzed_dependencies=analysis_request.analyze_dependencies,
        analyzed_bugs=analysis_request.detect_bugs,
    )

    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)

    return {
        "id": analysis.id,
        "status": analysis.status,
        "repo_url": analysis.repo_url,
        "message": "Analysis queued successfully",
        "created_at": analysis.analyzed_at.isoformat(),
        "api_key": api_key_info["name"],
    }


@app.get("/analysis/{analysis_id}")
@limiter.limit("50/minute")
async def get_analysis(
    request: Request,
    analysis_id: int,
    db: AsyncSession = Depends(get_db),
    api_key_info: dict = Security(verify_api_key),
):
    """Get analysis result by ID. Requires API key."""
    from sqlalchemy import select

    result = await db.execute(
        select(AnalysisResult).where(AnalysisResult.id == analysis_id)
    )
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "id": analysis.id,
        "repo_url": analysis.repo_url,
        "status": analysis.status,
        "analyzed_at": analysis.analyzed_at.isoformat(),
        "total_files": analysis.total_files,
        "bugs_found": analysis.bugs_found,
        "architecture_summary": analysis.architecture_summary,
    }
