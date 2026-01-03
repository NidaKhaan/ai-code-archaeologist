"""Security vulnerability scanner using Bandit."""

from typing import Dict, Any
import tempfile
import os
import subprocess
import json
import logging

logger = logging.getLogger(__name__)


class SecurityAnalyzer:
    """Scan code for security vulnerabilities."""

    def scan_code(self, code: str) -> Dict[str, Any]:
        """
        Scan Python code for security issues using Bandit.

        Args:
            code: Python source code to scan

        Returns:
            Dictionary with security findings
        """
        try:
            # Write code to temporary file (Bandit needs a file)
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
            ) as temp_file:
                temp_file.write(code)
                temp_path = temp_file.name

            try:
                # Run Bandit
                result = subprocess.run(
                    ["bandit", "-f", "json", temp_path],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                # Parse results
                if result.stdout:
                    bandit_output = json.loads(result.stdout)
                    return self._parse_bandit_results(bandit_output)
                else:
                    return {
                        "issues": [],
                        "summary": {
                            "total_issues": 0,
                            "high_severity": 0,
                            "medium_severity": 0,
                            "low_severity": 0,
                        },
                        "message": "No security issues found",
                    }

            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass

        except subprocess.TimeoutExpired:
            logger.error("Bandit scan timed out")
            return {"error": "Security scan timed out"}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Bandit output: {e}")
            return {"error": "Failed to parse security scan results"}
        except Exception as e:
            logger.error(f"Error running security scan: {e}", exc_info=True)
            return {"error": f"Security scan failed: {str(e)}"}

    def _parse_bandit_results(self, bandit_output: Dict) -> Dict[str, Any]:
        """Parse Bandit JSON output into structured format."""
        results = bandit_output.get("results", [])
        metrics = bandit_output.get("metrics", {})

        issues = []
        severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}

        for result in results:
            severity = result.get("issue_severity", "UNKNOWN")
            if severity in severity_counts:
                severity_counts[severity] += 1

            issues.append(
                {
                    "severity": severity,
                    "confidence": result.get("issue_confidence", "UNKNOWN"),
                    "cwe_id": result.get("issue_cwe", {}).get("id"),
                    "issue_type": result.get("test_name", "Unknown"),
                    "line_number": result.get("line_number"),
                    "description": result.get("issue_text", ""),
                    "code_snippet": result.get("code", "").strip(),
                    "recommendation": self._get_recommendation(result.get("test_id")),
                }
            )

        # Sort by severity (HIGH -> MEDIUM -> LOW)
        severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "UNKNOWN": 3}
        issues.sort(key=lambda x: severity_order.get(x["severity"], 3))

        return {
            "issues": issues,
            "summary": {
                "total_issues": len(issues),
                "high_severity": severity_counts["HIGH"],
                "medium_severity": severity_counts["MEDIUM"],
                "low_severity": severity_counts["LOW"],
                "files_scanned": metrics.get("_totals", {}).get("loc", 0),
            },
            "risk_level": self._calculate_risk_level(severity_counts),
            "message": (
                f"Found {len(issues)} security issue(s)"
                if issues
                else "No security issues found"
            ),
        }

    def _calculate_risk_level(self, severity_counts: Dict[str, int]) -> str:
        """Calculate overall risk level."""
        if severity_counts["HIGH"] > 0:
            return "CRITICAL"
        elif severity_counts["MEDIUM"] > 2:
            return "HIGH"
        elif severity_counts["MEDIUM"] > 0:
            return "MEDIUM"
        elif severity_counts["LOW"] > 0:
            return "LOW"
        else:
            return "SAFE"

    def _get_recommendation(self, test_id: str) -> str:
        """Get security recommendation based on test ID."""
        recommendations = {
            "B201": "Avoid using flask with debug=True in production",
            "B301": "Avoid using pickle for untrusted data",
            "B303": "Avoid insecure MD5 and SHA1 hashing",
            "B304": "Use secure random number generation",
            "B305": "Avoid using cipher modes without authentication",
            "B306": "Use mkstemp() instead of mktemp()",
            "B307": "Use defusedxml for XML parsing",
            "B308": "Use mark_safe only on trusted data",
            "B309": "Avoid HTTPSConnection with context=None",
            "B310": "Validate URLs before use",
            "B311": "Use secrets module for cryptographic randomness",
            "B312": "Use Telnetlib with caution",
            "B313": "Avoid XML external entity processing",
            "B314": "Avoid XML entity expansion attacks",
            "B315": "Avoid XML bomb attacks",
            "B316": "Avoid XML external entity in lxml",
            "B317": "Avoid XML external entity in xmlrpc",
            "B318": "Avoid XML external entity in ElementTree",
            "B319": "Avoid XML external entity in pulldom",
            "B320": "Avoid XML external entity in etree",
            "B321": "Avoid FTP with cleartext",
            "B322": "Avoid insecure temporary files",
            "B323": "Avoid unverified SSL/TLS",
            "B324": "Use hashlib with secure algorithm",
            "B325": "Use tempfile securely",
            "B501": "Avoid shell injection",
            "B502": "Avoid SSL with bad defaults",
            "B503": "Avoid SSL with bad version",
            "B504": "Avoid SSL with bad ciphers",
            "B505": "Avoid weak cryptographic key",
            "B506": "Avoid YAML load",
            "B507": "Avoid SSH with exec_command",
            "B601": "Avoid shell=True in subprocess",
            "B602": "Avoid shell injection in popen",
            "B603": "Avoid untrusted input in subprocess",
            "B604": "Validate shell commands",
            "B605": "Avoid os.system with shell=True",
            "B606": "Avoid exec without validation",
            "B607": "Avoid starting processes with partial path",
            "B608": "Validate SQL queries",
            "B609": "Avoid wildcard injection in commands",
        }
        return recommendations.get(test_id, "Review and fix this security issue")


# Global instance
security_analyzer = SecurityAnalyzer()
