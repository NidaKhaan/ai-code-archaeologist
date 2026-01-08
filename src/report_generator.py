"""Generate beautiful analysis reports in multiple formats."""

import json
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate formatted reports from analysis results."""

    def generate_markdown_report(
        self, analysis_data: Dict[str, Any], repo_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a beautiful Markdown report.

        Args:
            analysis_data: Complete analysis results
            repo_info: Optional repository metadata

        Returns:
            Markdown formatted report as string
        """
        try:
            report_lines = []

            # Header
            report_lines.append("# 🔍 AI Code Archaeologist - Analysis Report")
            report_lines.append("")
            report_lines.append(
                f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            report_lines.append("")
            report_lines.append("---")
            report_lines.append("")

            # Repository Info (if available)
            if repo_info:
                report_lines.append("## 📦 Repository Information")
                report_lines.append("")
                report_lines.append(f"**Name:** {repo_info.get('name', 'N/A')}")
                report_lines.append(f"**URL:** {repo_info.get('url', 'N/A')}")
                report_lines.append(f"**Language:** {repo_info.get('language', 'N/A')}")
                report_lines.append(f"**Stars:** ⭐ {repo_info.get('stars', 0)}")
                report_lines.append(f"**Forks:** 🍴 {repo_info.get('forks', 0)}")

                if repo_info.get("description"):
                    report_lines.append(f"**Description:** {repo_info['description']}")

                report_lines.append("")
                report_lines.append("---")
                report_lines.append("")

            # Overall Score
            if "overall_score" in analysis_data:
                score = analysis_data["overall_score"]
                report_lines.append("## 🎯 Overall Quality Score")
                report_lines.append("")
                report_lines.append(
                    f"### Grade: **{score.get('grade', 'N/A')}** ({score.get('score', 0)}/100)"
                )
                report_lines.append(f"*{score.get('description', '')}*")
                report_lines.append("")

                if "component_scores" in score:
                    comp = score["component_scores"]
                    report_lines.append("**Component Scores:**")
                    report_lines.append(
                        f"- 📊 Complexity: {comp.get('complexity', 0)}/100"
                    )
                    report_lines.append(
                        f"- ✅ Best Practices: {comp.get('best_practices', 0)}/100"
                    )
                    report_lines.append(f"- 🔒 Security: {comp.get('security', 0)}/100")

                report_lines.append("")
                report_lines.append("---")
                report_lines.append("")

            # Summary Statistics
            if "summary" in analysis_data:
                summary = analysis_data["summary"]
                report_lines.append("## 📈 Summary Statistics")
                report_lines.append("")
                report_lines.append(
                    f"- **Total Python Files:** {summary.get('total_python_files', 0)}"
                )
                report_lines.append(
                    f"- **Files Analyzed:** {summary.get('files_analyzed', 0)}"
                )
                report_lines.append(
                    f"- **Total Lines of Code:** {summary.get('total_lines_of_code', 0):,}"
                )
                report_lines.append(
                    f"- **Average Maintainability:** {summary.get('average_maintainability', 0):.1f}/100"
                )
                report_lines.append("")
                report_lines.append("---")
                report_lines.append("")

            # Detailed Analysis
            detailed = analysis_data.get("detailed_analysis", {})

            # AST Analysis
            if "ast_structure" in detailed:
                ast_data = detailed["ast_structure"]
                report_lines.append("## 🌳 Code Structure (AST Analysis)")
                report_lines.append("")
                report_lines.append(
                    f"- **Total Lines:** {ast_data.get('total_lines', 0)}"
                )
                report_lines.append(
                    f"- **Functions:** {len(ast_data.get('functions', []))}"
                )
                report_lines.append(
                    f"- **Classes:** {len(ast_data.get('classes', []))}"
                )
                report_lines.append(
                    f"- **Imports:** {len(ast_data.get('imports', []))}"
                )

                if ast_data.get("functions"):
                    report_lines.append("")
                    report_lines.append("### Top Functions by Complexity:")
                    functions = sorted(
                        ast_data["functions"],
                        key=lambda x: x.get("complexity", 0),
                        reverse=True,
                    )[:5]

                    for func in functions:
                        report_lines.append(
                            f"- `{func['name']}()` - Complexity: {func.get('complexity', 0)}"
                        )

                report_lines.append("")
                report_lines.append("---")
                report_lines.append("")

            # Complexity Metrics
            if "complexity_metrics" in detailed:
                complexity = detailed["complexity_metrics"]
                report_lines.append("## 📊 Complexity Analysis")
                report_lines.append("")

                if "maintainability_index" in complexity:
                    mi = complexity["maintainability_index"]
                    report_lines.append(
                        f"### Maintainability Index: {mi.get('score', 0):.1f}/100"
                    )
                    report_lines.append(
                        f"**Rank:** {mi.get('rank', 'N/A')} - *{mi.get('description', '')}*"
                    )
                    report_lines.append("")

                if "quality_grade" in complexity:
                    qg = complexity["quality_grade"]
                    report_lines.append(
                        f"### Quality Grade: **{qg.get('grade', 'N/A')}**"
                    )
                    report_lines.append(f"*{qg.get('description', '')}*")
                    report_lines.append("")

                if "raw_metrics" in complexity:
                    raw = complexity["raw_metrics"]
                    report_lines.append("### Code Metrics:")
                    report_lines.append(f"- Lines of Code (LOC): {raw.get('loc', 0)}")
                    report_lines.append(f"- Logical Lines (LLOC): {raw.get('lloc', 0)}")
                    report_lines.append(f"- Comments: {raw.get('comments', 0)}")
                    report_lines.append(
                        f"- Comment Ratio: {raw.get('comment_ratio', 0):.1f}%"
                    )

                report_lines.append("")
                report_lines.append("---")
                report_lines.append("")

            # Security Analysis
            if "security_scan" in detailed:
                security = detailed["security_scan"]
                report_lines.append("## 🔒 Security Analysis")
                report_lines.append("")

                if "summary" in security:
                    summary = security["summary"]
                    report_lines.append(
                        f"**Total Issues Found:** {summary.get('total_issues', 0)}"
                    )
                    report_lines.append(
                        f"- 🔴 High Severity: {summary.get('high_severity', 0)}"
                    )
                    report_lines.append(
                        f"- 🟡 Medium Severity: {summary.get('medium_severity', 0)}"
                    )
                    report_lines.append(
                        f"- 🟢 Low Severity: {summary.get('low_severity', 0)}"
                    )
                    report_lines.append("")
                    report_lines.append(
                        f"**Risk Level:** {security.get('risk_level', 'UNKNOWN')}"
                    )
                    report_lines.append("")

                if security.get("issues"):
                    report_lines.append("### Security Issues:")
                    report_lines.append("")
                    for issue in security["issues"][:5]:  # Top 5 issues
                        severity_emoji = {
                            "HIGH": "🔴",
                            "MEDIUM": "🟡",
                            "LOW": "🟢",
                        }.get(issue.get("severity", ""), "⚪")
                        report_lines.append(
                            f"#### {severity_emoji} {issue.get('issue_type', 'Unknown')}"
                        )
                        report_lines.append(
                            f"**Line:** {issue.get('line_number', 'N/A')}"
                        )
                        report_lines.append(
                            f"**Description:** {issue.get('description', '')}"
                        )
                        report_lines.append(
                            f"**Recommendation:** {issue.get('recommendation', '')}"
                        )
                        report_lines.append("")

                report_lines.append("---")
                report_lines.append("")

            # Architecture Analysis
            if "architecture" in detailed:
                arch = detailed["architecture"]
                report_lines.append("## 🏗️ Architecture Analysis")
                report_lines.append("")

                if "architectural_style" in arch:
                    style = arch["architectural_style"]
                    report_lines.append(
                        f"**Architectural Style:** {style.get('style', 'Unknown')}"
                    )
                    report_lines.append(
                        f"**Confidence:** {style.get('confidence', 'low')}"
                    )
                    report_lines.append("")

                if arch.get("design_patterns"):
                    report_lines.append("### Design Patterns Detected:")
                    for pattern in arch["design_patterns"]:
                        report_lines.append(
                            f"- **{pattern['pattern']}** in `{pattern['class']}`"
                        )
                        report_lines.append(f"  - *{pattern['description']}*")
                    report_lines.append("")

                if arch.get("code_smells"):
                    report_lines.append("### ⚠️ Code Smells:")
                    for smell in arch["code_smells"][:5]:
                        report_lines.append(
                            f"- **{smell['smell']}** - {smell['location']}"
                        )
                        report_lines.append(f"  - {smell['description']}")
                    report_lines.append("")

                if arch.get("recommendations"):
                    report_lines.append("### 💡 Recommendations:")
                    for rec in arch["recommendations"]:
                        report_lines.append(f"- {rec}")

                report_lines.append("")
                report_lines.append("---")
                report_lines.append("")

            # Dependencies
            if "dependencies" in detailed:
                deps = detailed["dependencies"]
                report_lines.append("## 📦 Dependencies")
                report_lines.append("")
                report_lines.append(
                    f"**Total Imports:** {deps.get('total_imports', 0)}"
                )
                report_lines.append("")

                if deps.get("stdlib_imports"):
                    report_lines.append(
                        f"**Standard Library:** {', '.join(deps['stdlib_imports'][:10])}"
                    )
                if deps.get("third_party_imports"):
                    report_lines.append(
                        f"**Third Party:** {', '.join(deps['third_party_imports'][:10])}"
                    )

                report_lines.append("")
                report_lines.append("---")
                report_lines.append("")

            # Footer
            report_lines.append("---")
            report_lines.append("")
            report_lines.append("*Report generated by **AI Code Archaeologist***")
            report_lines.append("")
            report_lines.append(
                "🤖 Powered by Local AI (Ollama) + Advanced Static Analysis"
            )

            return "\n".join(report_lines)

        except Exception as e:
            logger.error(f"Error generating report: {e}", exc_info=True)
            return f"# Error Generating Report\n\n{str(e)}"

    def generate_json_report(self, analysis_data: Dict[str, Any]) -> str:
        """
        Generate JSON report for programmatic use.

        Args:
            analysis_data: Complete analysis results

        Returns:
            JSON formatted string
        """
        try:
            report = {
                "generated_at": datetime.now().isoformat(),
                "version": "1.0",
                "analysis": analysis_data,
            }
            return json.dumps(report, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error generating JSON report: {e}", exc_info=True)
            return json.dumps({"error": str(e)})


# Global instance
report_generator = ReportGenerator()
