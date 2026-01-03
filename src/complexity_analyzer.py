"""Code complexity and quality metrics using Radon."""

from typing import Dict, Any, List
from radon.complexity import cc_visit
from radon.metrics import mi_visit, h_visit
from radon.raw import analyze
import logging

logger = logging.getLogger(__name__)


class ComplexityAnalyzer:
    """Analyze code complexity and maintainability."""

    def analyze_complexity(
        self, code: str, filename: str = "code.py"
    ) -> Dict[str, Any]:
        """
        Analyze code complexity metrics.

        Args:
            code: Python source code
            filename: Name of the file (for reporting)

        Returns:
            Dictionary with complexity metrics
        """
        try:
            return {
                "cyclomatic_complexity": self._cyclomatic_complexity(code),
                "maintainability_index": self._maintainability_index(code),
                "halstead_metrics": self._halstead_metrics(code),
                "raw_metrics": self._raw_metrics(code),
                "quality_grade": self._get_quality_grade(code),
            }
        except Exception as e:
            logger.error(f"Error analyzing complexity: {e}", exc_info=True)
            return {"error": str(e)}

    def _cyclomatic_complexity(self, code: str) -> List[Dict[str, Any]]:
        """Calculate cyclomatic complexity for all functions."""
        try:
            results = cc_visit(code)
            return [
                {
                    "name": result.name,
                    "complexity": result.complexity,
                    "rank": result.letter,
                    "line": result.lineno,
                    "type": result.classname or "function",
                }
                for result in results
            ]
        except Exception as e:
            logger.warning(f"Could not calculate cyclomatic complexity: {e}")
            return []

    def _maintainability_index(self, code: str) -> Dict[str, Any]:
        """Calculate maintainability index (0-100, higher is better)."""
        try:
            mi = mi_visit(code, multi=True)
            return {
                "score": round(mi, 2),
                "rank": self._mi_rank(mi),
                "description": self._mi_description(mi),
            }
        except Exception as e:
            logger.warning(f"Could not calculate maintainability index: {e}")
            return {"score": 0, "rank": "F", "description": "Unable to calculate"}

    def _halstead_metrics(self, code: str) -> Dict[str, Any]:
        """Calculate Halstead complexity metrics."""
        try:
            report = h_visit(code)
            return {
                "vocabulary": report.total.vocabulary,
                "length": report.total.length,
                "calculated_length": round(report.total.calculated_length, 2),
                "volume": round(report.total.volume, 2),
                "difficulty": round(report.total.difficulty, 2),
                "effort": round(report.total.effort, 2),
                "time_to_program": round(report.total.time, 2),
                "bugs_estimate": round(report.total.bugs, 2),
            }
        except Exception as e:
            logger.warning(f"Could not calculate Halstead metrics: {e}")
            return {}

    def _raw_metrics(self, code: str) -> Dict[str, Any]:
        """Calculate raw code metrics."""
        try:
            metrics = analyze(code)
            return {
                "loc": metrics.loc,  # Lines of code
                "lloc": metrics.lloc,  # Logical lines of code
                "sloc": metrics.sloc,  # Source lines of code
                "comments": metrics.comments,
                "multi_line_strings": metrics.multi,
                "blank_lines": metrics.blank,
                "comment_ratio": round(
                    (metrics.comments / max(metrics.loc, 1)) * 100, 2
                ),
            }
        except Exception as e:
            logger.warning(f"Could not calculate raw metrics: {e}")
            return {}

    def _get_quality_grade(self, code: str) -> Dict[str, str]:
        """Get overall quality grade based on metrics."""
        try:
            mi = mi_visit(code, multi=True)
            cc_results = cc_visit(code)

            # Average complexity
            avg_complexity = sum(r.complexity for r in cc_results) / max(
                len(cc_results), 1
            )

            # Determine grade
            if mi >= 80 and avg_complexity <= 5:
                grade = "A"
                description = "Excellent - Highly maintainable"
            elif mi >= 60 and avg_complexity <= 10:
                grade = "B"
                description = "Good - Maintainable"
            elif mi >= 40 and avg_complexity <= 15:
                grade = "C"
                description = "Fair - Needs improvement"
            elif mi >= 20:
                grade = "D"
                description = "Poor - Difficult to maintain"
            else:
                grade = "F"
                description = "Critical - Very difficult to maintain"

            return {
                "grade": grade,
                "description": description,
                "maintainability_index": round(mi, 2),
                "average_complexity": round(avg_complexity, 2),
            }
        except Exception as e:
            logger.warning(f"Could not calculate quality grade: {e}")
            return {"grade": "?", "description": "Unable to calculate"}

    def _mi_rank(self, mi: float) -> str:
        """Get maintainability index rank."""
        if mi >= 80:
            return "A"
        elif mi >= 60:
            return "B"
        elif mi >= 40:
            return "C"
        elif mi >= 20:
            return "D"
        else:
            return "F"

    def _mi_description(self, mi: float) -> str:
        """Get maintainability index description."""
        if mi >= 80:
            return "Highly maintainable"
        elif mi >= 60:
            return "Moderately maintainable"
        elif mi >= 40:
            return "Somewhat maintainable"
        elif mi >= 20:
            return "Difficult to maintain"
        else:
            return "Very difficult to maintain"


# Global instance
complexity_analyzer = ComplexityAnalyzer()
