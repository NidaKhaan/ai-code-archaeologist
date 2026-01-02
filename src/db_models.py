"""Database models for storing analysis results."""

from sqlalchemy import String, Boolean, DateTime, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from src.database import Base


class AnalysisResult(Base):
    """Store repository analysis results."""

    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    repo_url: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")

    # Analysis metadata
    analyzed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    total_files: Mapped[int] = mapped_column(Integer, default=0)
    total_lines: Mapped[int] = mapped_column(Integer, default=0)

    # Analysis results
    architecture_summary: Mapped[str] = mapped_column(Text, nullable=True)
    bugs_found: Mapped[int] = mapped_column(Integer, default=0)
    bug_details: Mapped[str] = mapped_column(Text, nullable=True)

    # Options
    analyzed_dependencies: Mapped[bool] = mapped_column(Boolean, default=False)
    analyzed_bugs: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, repo={self.repo_url}, status={self.status})>"
