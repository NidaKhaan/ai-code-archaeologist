"""Main FastAPI application for AI Code Archaeologist."""

from src.db_models import AnalysisResult, GitHubAnalysis
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Depends, Security, Request
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.utils import greet, validate_github_url
from src.models import (
    GreetingResponse,
    RepositoryValidation,
    AnalysisRequest,
    CodeSnippet,
    AIAnalysisResponse,
    CodeAnalysisRequest,
)
from src.database import get_db, init_db
from src.auth import verify_api_key
from src.rate_limit import limiter
from src.code_analyzer import code_analyzer
from src.ast_analyzer import ast_analyzer
from src.complexity_analyzer import complexity_analyzer
from src.security_analyzer import security_analyzer
from src.dependency_analyzer import dependency_analyzer
from src.architecture_detector import architecture_detector
from src.github_analyzer import github_analyzer

logger = logging.getLogger(__name__)


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


@app.post("/ai/analyze-repo", response_model=AIAnalysisResponse)
@limiter.limit("3/minute")
async def ai_analyze_repo(
    request: Request,
    repo_url: str,
    provider: Optional[str] = None,
    api_key_info: dict = Security(verify_api_key),
):
    """
    Use AI to analyze a GitHub repository.
    Requires API key authentication.
    """
    if not validate_github_url(repo_url):
        raise HTTPException(status_code=400, detail="Invalid GitHub URL")

    try:
        result = await code_analyzer.analyze_repository_summary(repo_url, provider)
        return AIAnalysisResponse(
            result=result["summary"],
            provider_used=result["provider_used"],
            model_used=result["model_used"],
            tokens_used=result["tokens"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/ai/explain-code", response_model=AIAnalysisResponse)
@limiter.limit("5/minute")
async def ai_explain_code(
    request: Request,
    snippet: CodeSnippet,
    api_key_info: dict = Security(verify_api_key),
):
    """
    Use AI to explain code snippet.
    Requires API key authentication.
    """
    try:
        result = await code_analyzer.explain_code_snippet(
            snippet.code, snippet.language, snippet.provider
        )
        return AIAnalysisResponse(
            result=result["explanation"],
            provider_used=result["provider_used"],
            model_used="codellama:7b",
            tokens_used=result["tokens"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")


@app.post("/ai/improve-code", response_model=AIAnalysisResponse)
@limiter.limit("5/minute")
async def ai_improve_code(
    request: Request,
    snippet: CodeSnippet,
    api_key_info: dict = Security(verify_api_key),
):
    """
    Use AI to suggest code improvements.
    Requires API key authentication.
    """
    try:
        result = await code_analyzer.suggest_improvements(
            snippet.code, snippet.language, snippet.provider
        )
        return AIAnalysisResponse(
            result=result["suggestions"],
            provider_used=result["provider_used"],
            model_used="codellama:7b",
            tokens_used=result["tokens"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Improvement suggestion failed: {str(e)}"
        )


@app.post("/analyze/deep-scan")
@limiter.limit("3/minute")
async def deep_code_scan(
    request: Request,
    analysis_request: CodeAnalysisRequest,
    api_key_info: dict = Security(verify_api_key),
):
    """
    Perform deep code analysis: AST, complexity, and security.
    Requires API key authentication.
    """
    results = {}

    try:
        # AST Analysis
        if analysis_request.include_ast:
            logger.info("Running AST analysis...")
            results["ast_analysis"] = ast_analyzer.analyze_code(analysis_request.code)

        # Complexity Analysis
        if analysis_request.include_complexity:
            logger.info("Running complexity analysis...")
            results["complexity_analysis"] = complexity_analyzer.analyze_complexity(
                analysis_request.code
            )

        # Security Scan
        if analysis_request.include_security:
            logger.info("Running security scan...")
            results["security_analysis"] = security_analyzer.scan_code(
                analysis_request.code
            )

        return {
            "status": "success",
            "analyses_performed": {
                "ast": analysis_request.include_ast,
                "complexity": analysis_request.include_complexity,
                "security": analysis_request.include_security,
            },
            "results": results,
            "api_key": api_key_info["name"],
        }

    except Exception as e:
        logger.error(f"Deep scan failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/analyze/dependencies")
@limiter.limit("5/minute")
async def analyze_dependencies(
    request: Request,
    code: str,
    filename: str = "main.py",
    api_key_info: dict = Security(verify_api_key),
):
    """
    Analyze code dependencies and import structure.
    Requires API key authentication.
    """
    try:
        result = dependency_analyzer.analyze_dependencies(code, filename)
        return {
            "status": "success",
            "filename": filename,
            "analysis": result,
            "api_key": api_key_info["name"],
        }
    except Exception as e:
        logger.error(f"Dependency analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/analyze/architecture")
@limiter.limit("5/minute")
async def analyze_architecture(
    request: Request, code: str, api_key_info: dict = Security(verify_api_key)
):
    """
    Detect architectural patterns and design smells.
    Requires API key authentication.
    """
    try:
        result = architecture_detector.detect_patterns(code)
        return {
            "status": "success",
            "analysis": result,
            "api_key": api_key_info["name"],
        }
    except Exception as e:
        logger.error(f"Architecture analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/analyze/complete")
@limiter.limit("2/minute")
async def complete_analysis(
    request: Request,
    code: str,
    filename: str = "main.py",
    api_key_info: dict = Security(verify_api_key),
):
    """
    Perform COMPLETE code analysis - all features combined!
    This is the ultimate endpoint that runs everything.
    Requires API key authentication.
    """
    try:
        logger.info("Starting complete code analysis...")

        results = {
            "ast_structure": ast_analyzer.analyze_code(code),
            "complexity_metrics": complexity_analyzer.analyze_complexity(code),
            "security_scan": security_analyzer.scan_code(code),
            "dependencies": dependency_analyzer.analyze_dependencies(code, filename),
            "architecture": architecture_detector.detect_patterns(code),
        }

        # Generate overall score
        overall_score = await _calculate_overall_score(results)

        return {
            "status": "success",
            "filename": filename,
            "overall_score": overall_score,
            "detailed_analysis": results,
            "api_key": api_key_info["name"],
        }

    except Exception as e:
        logger.error(f"Complete analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


async def _calculate_overall_score(results: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate overall code quality score from all analyses."""
    scores = []

    # Complexity score (inverse - lower is better)
    if "quality_grade" in results.get("complexity_metrics", {}):
        grade = results["complexity_metrics"]["quality_grade"].get("grade", "F")
        grade_scores = {"A": 100, "B": 80, "C": 60, "D": 40, "F": 20}
        scores.append(grade_scores.get(grade, 20))

    # Best practices score
    if "best_practices" in results.get("architecture", {}):
        bp_score = results["architecture"]["best_practices"].get("score", 0)
        scores.append(bp_score)

    # Security score (fewer issues = higher score)
    if "summary" in results.get("security_scan", {}):
        issues = results["security_scan"]["summary"].get("total_issues", 0)
        security_score = max(0, 100 - (issues * 10))
        scores.append(security_score)

    # Calculate average
    avg_score = sum(scores) / len(scores) if scores else 0

    # Determine grade
    if avg_score >= 90:
        grade, desc = "A", "Excellent"
    elif avg_score >= 75:
        grade, desc = "B", "Good"
    elif avg_score >= 60:
        grade, desc = "C", "Fair"
    elif avg_score >= 40:
        grade, desc = "D", "Poor"
    else:
        grade, desc = "F", "Critical"

    return {
        "score": round(avg_score, 1),
        "grade": grade,
        "description": desc,
        "component_scores": {
            "complexity": scores[0] if len(scores) > 0 else 0,
            "best_practices": scores[1] if len(scores) > 1 else 0,
            "security": scores[2] if len(scores) > 2 else 0,
        },
    }


@app.get("/github/info")
@limiter.limit("10/minute")
async def get_github_repo_info(
    request: Request, repo_url: str, api_key_info: dict = Security(verify_api_key)
):
    """
    Get GitHub repository information without cloning.
    Fast metadata retrieval via GitHub API.
    Requires API key authentication.
    """
    try:
        info = github_analyzer.get_repository_info(repo_url)

        if "error" in info:
            raise HTTPException(status_code=400, detail=info["error"])

        return {
            "status": "success",
            "repository": info,
            "api_key": api_key_info["name"],
        }
    except Exception as e:
        logger.error(f"Error fetching repo info: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/github/structure")
@limiter.limit("5/minute")
async def get_github_repo_structure(
    request: Request,
    repo_url: str,
    max_depth: int = 3,
    api_key_info: dict = Security(verify_api_key),
):
    """
    Get GitHub repository file structure.
    Analyzes structure without full clone.
    Requires API key authentication.
    """
    try:
        structure = github_analyzer.get_file_structure(repo_url, max_depth)

        if "error" in structure:
            raise HTTPException(status_code=400, detail=structure["error"])

        return {
            "status": "success",
            "repo_url": repo_url,
            "structure": structure,
            "api_key": api_key_info["name"],
        }
    except Exception as e:
        logger.error(f"Error getting repo structure: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/github/analyze-full")
@limiter.limit("2/minute")
async def analyze_github_repository(
    request: Request,
    repo_url: str,
    max_files: int = 10,
    db: AsyncSession = Depends(get_db),
    api_key_info: dict = Security(verify_api_key),
):
    """
    FULL GitHub repository analysis - clones, analyzes, and SAVES results!
    This is the ULTIMATE feature - analyzes entire repos and stores in database.

    Warning: This clones the repository and can take 1-3 minutes.
    Requires API key authentication.
    """
    try:
        logger.info(f"Starting full analysis of {repo_url}")

        # Step 1: Get repo info
        repo_info = github_analyzer.get_repository_info(repo_url)
        if "error" in repo_info:
            raise HTTPException(status_code=400, detail=repo_info["error"])

        # Step 2: Clone repository
        logger.info("Cloning repository...")
        repo_path = github_analyzer.clone_repository(repo_url)

        if not repo_path:
            raise HTTPException(status_code=500, detail="Failed to clone repository")

        try:
            # Step 3: Get Python files
            logger.info("Extracting Python files...")
            python_files = github_analyzer.get_python_files(repo_path)

            if not python_files:
                # Save minimal result
                analysis_record = GitHubAnalysis(
                    repo_url=repo_url,
                    repo_name=repo_info["name"],
                    language=repo_info.get("language"),
                    stars=repo_info.get("stars", 0),
                    forks=repo_info.get("forks", 0),
                    status="no_python_files",
                )
                db.add(analysis_record)
                await db.commit()
                await db.refresh(analysis_record)

                return {
                    "status": "success",
                    "analysis_id": analysis_record.id,
                    "message": "No Python files found in repository",
                    "repository": repo_info,
                }

            # Step 4: Analyze files (limit to max_files)
            files_to_analyze = python_files[:max_files]
            analyzed_files = []

            logger.info(f"Analyzing {len(files_to_analyze)} Python files...")

            for file_data in files_to_analyze:
                if file_data["content"]:
                    try:
                        # Run quick analysis on each file
                        analysis = {
                            "path": file_data["path"],
                            "lines": file_data["line_count"],
                            "size": file_data["size_bytes"],
                            "ast": ast_analyzer.analyze_code(file_data["content"]),
                            "complexity": complexity_analyzer.analyze_complexity(
                                file_data["content"]
                            ),
                        }
                        analyzed_files.append(analysis)
                    except Exception as e:
                        logger.warning(f"Failed to analyze {file_data['path']}: {e}")
                        continue

            # Step 5: Generate summary
            total_lines = sum(f["line_count"] for f in python_files)
            avg_complexity = sum(
                f.get("complexity", {}).get("maintainability_index", {}).get("score", 0)
                for f in analyzed_files
            ) / max(len(analyzed_files), 1)

            # Step 6: Save to database
            import json

            analysis_record = GitHubAnalysis(
                repo_url=repo_url,
                repo_name=repo_info["name"],
                language=repo_info.get("language"),
                stars=repo_info.get("stars", 0),
                forks=repo_info.get("forks", 0),
                total_python_files=len(python_files),
                files_analyzed=len(analyzed_files),
                total_lines=total_lines,
                average_maintainability=round(avg_complexity, 2),
                analysis_summary=json.dumps(
                    {
                        "description": repo_info.get("description"),
                        "topics": repo_info.get("topics", []),
                        "created_at": repo_info.get("created_at"),
                    }
                ),
                file_analyses=json.dumps(analyzed_files),
                status="completed",
            )

            db.add(analysis_record)
            await db.commit()
            await db.refresh(analysis_record)

            logger.info(f"Analysis saved with ID: {analysis_record.id}")

            result = {
                "status": "success",
                "analysis_id": analysis_record.id,
                "repository": repo_info,
                "summary": {
                    "total_python_files": len(python_files),
                    "files_analyzed": len(analyzed_files),
                    "total_lines_of_code": total_lines,
                    "average_maintainability": round(avg_complexity, 2),
                },
                "analyzed_files": analyzed_files[:3],  # Return first 3 for preview
                "message": f"Successfully analyzed and saved {len(analyzed_files)} files from {repo_info['name']}",
            }

            return result

        finally:
            # Always cleanup
            github_analyzer.cleanup()

    except Exception as e:
        github_analyzer.cleanup()
        logger.error(f"Full analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/github/analyses")
@limiter.limit("20/minute")
async def list_github_analyses(
    request: Request,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    api_key_info: dict = Security(verify_api_key),
):
    """
    List all saved GitHub repository analyses.
    Paginated results.
    Requires API key authentication.
    """
    try:
        from sqlalchemy import select

        result = await db.execute(
            select(GitHubAnalysis)
            .order_by(GitHubAnalysis.analyzed_at.desc())
            .offset(skip)
            .limit(limit)
        )
        analyses = result.scalars().all()

        return {
            "status": "success",
            "count": len(analyses),
            "analyses": [
                {
                    "id": a.id,
                    "repo_name": a.repo_name,
                    "repo_url": a.repo_url,
                    "language": a.language,
                    "stars": a.stars,
                    "analyzed_at": a.analyzed_at.isoformat(),
                    "files_analyzed": a.files_analyzed,
                    "total_lines": a.total_lines,
                    "average_maintainability": a.average_maintainability,
                    "status": a.status,
                }
                for a in analyses
            ],
        }
    except Exception as e:
        logger.error(f"Error listing analyses: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/github/analyses/{analysis_id}")
@limiter.limit("20/minute")
async def get_github_analysis(
    request: Request,
    analysis_id: int,
    db: AsyncSession = Depends(get_db),
    api_key_info: dict = Security(verify_api_key),
):
    """
    Get detailed GitHub analysis by ID.
    Returns full analysis including all file results.
    Requires API key authentication.
    """
    try:
        from sqlalchemy import select
        import json

        result = await db.execute(
            select(GitHubAnalysis).where(GitHubAnalysis.id == analysis_id)
        )
        analysis = result.scalar_one_or_none()

        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        # Parse JSON fields
        summary = (
            json.loads(analysis.analysis_summary) if analysis.analysis_summary else {}
        )
        file_analyses = (
            json.loads(analysis.file_analyses) if analysis.file_analyses else []
        )

        return {
            "status": "success",
            "analysis": {
                "id": analysis.id,
                "repo_name": analysis.repo_name,
                "repo_url": analysis.repo_url,
                "language": analysis.language,
                "stars": analysis.stars,
                "forks": analysis.forks,
                "analyzed_at": analysis.analyzed_at.isoformat(),
                "total_python_files": analysis.total_python_files,
                "files_analyzed": analysis.files_analyzed,
                "total_lines": analysis.total_lines,
                "average_maintainability": analysis.average_maintainability,
                "status": analysis.status,
                "summary": summary,
                "file_analyses": file_analyses,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
