"""Tests for database operations."""

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from src.database import Base
from src.db_models import AnalysisResult


# Test database URL (in-memory)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_db():
    """Create a test database."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_create_analysis_result(test_db):
    """Test creating an analysis result."""
    analysis = AnalysisResult(
        repo_url="https://github.com/test/repo",
        status="queued",
        analyzed_dependencies=True,
        analyzed_bugs=True,
    )

    test_db.add(analysis)
    await test_db.commit()
    await test_db.refresh(analysis)

    assert analysis.id is not None
    assert analysis.repo_url == "https://github.com/test/repo"
    assert analysis.status == "queued"


@pytest.mark.asyncio
async def test_query_analysis_result(test_db):
    """Test querying analysis results."""
    from sqlalchemy import select

    # Create test data
    analysis = AnalysisResult(
        repo_url="https://github.com/python/cpython",
        status="completed",
        total_files=100,
        bugs_found=5,
    )

    test_db.add(analysis)
    await test_db.commit()

    # Query it back
    result = await test_db.execute(
        select(AnalysisResult).where(AnalysisResult.status == "completed")
    )
    found = result.scalar_one_or_none()

    assert found is not None
    assert found.repo_url == "https://github.com/python/cpython"
    assert found.total_files == 100
    assert found.bugs_found == 5
