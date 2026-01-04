"""Detect architectural patterns and project structure."""

import ast
from typing import Dict, List, Any
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class ArchitectureDetector:
    """Detect architectural patterns and design structures."""

    def detect_patterns(self, code: str) -> Dict[str, Any]:
        """
        Detect architectural and design patterns in code.

        Args:
            code: Python source code

        Returns:
            Dictionary with detected patterns
        """
        try:
            tree = ast.parse(code)

            patterns = {
                "design_patterns": self._detect_design_patterns(tree),
                "architectural_style": self._detect_architectural_style(tree),
                "code_smells": self._detect_code_smells(tree, code),
                "best_practices": self._check_best_practices(tree, code),
                "recommendations": [],
            }

            # Generate recommendations
            patterns["recommendations"] = self._generate_recommendations(patterns)

            return patterns

        except Exception as e:
            logger.error(f"Error detecting patterns: {e}", exc_info=True)
            return {"error": str(e)}

    def _detect_design_patterns(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Detect common design patterns."""
        patterns = []

        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

        for cls in classes:
            # Singleton pattern detection
            if self._is_singleton(cls):
                patterns.append(
                    {
                        "pattern": "Singleton",
                        "class": cls.name,
                        "confidence": "medium",
                        "description": "Class appears to implement Singleton pattern",
                    }
                )

            # Factory pattern detection
            if self._is_factory(cls):
                patterns.append(
                    {
                        "pattern": "Factory",
                        "class": cls.name,
                        "confidence": "medium",
                        "description": "Class appears to implement Factory pattern",
                    }
                )

            # Observer pattern detection
            if self._is_observer(cls):
                patterns.append(
                    {
                        "pattern": "Observer",
                        "class": cls.name,
                        "confidence": "low",
                        "description": "Class may implement Observer pattern",
                    }
                )

            # Decorator pattern detection
            if self._is_decorator_pattern(cls):
                patterns.append(
                    {
                        "pattern": "Decorator",
                        "class": cls.name,
                        "confidence": "medium",
                        "description": "Class appears to implement Decorator pattern",
                    }
                )

        return patterns

    def _detect_architectural_style(self, tree: ast.AST) -> Dict[str, Any]:
        """Detect overall architectural style."""
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        functions = [
            node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        ]

        class_count = len(classes)
        function_count = len(functions)

        # Determine style
        if class_count == 0 and function_count > 5:
            style = "Procedural"
            confidence = "high"
        elif class_count > 3 and class_count / max(function_count, 1) > 0.5:
            style = "Object-Oriented"
            confidence = "high"
        elif any(
            "async" in node.name.lower() for node in functions if hasattr(node, "name")
        ):
            style = "Async/Event-Driven"
            confidence = "medium"
        elif function_count > 10 and class_count < 2:
            style = "Functional"
            confidence = "medium"
        else:
            style = "Mixed/Hybrid"
            confidence = "low"

        return {
            "style": style,
            "confidence": confidence,
            "metrics": {
                "classes": class_count,
                "functions": function_count,
                "ratio": round(class_count / max(function_count, 1), 2),
            },
        }

    def _detect_code_smells(self, tree: ast.AST, code: str) -> List[Dict[str, Any]]:
        """Detect code smells and anti-patterns."""
        smells = []

        # Long method detection
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                lines = len([n for n in ast.walk(node) if isinstance(n, ast.stmt)])
                if lines > 50:
                    smells.append(
                        {
                            "smell": "Long Method",
                            "location": f"{node.name} (line {node.lineno})",
                            "severity": "medium",
                            "description": f"Method has {lines} statements - consider breaking it down",
                        }
                    )

        # God class detection
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        for cls in classes:
            methods = [
                n
                for n in cls.body
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            if len(methods) > 20:
                smells.append(
                    {
                        "smell": "God Class",
                        "location": f"{cls.name} (line {cls.lineno})",
                        "severity": "high",
                        "description": f"Class has {len(methods)} methods - too many responsibilities",
                    }
                )

        # Deeply nested code
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                depth = self._calculate_nesting_depth(node)
                if depth > 4:
                    smells.append(
                        {
                            "smell": "Deep Nesting",
                            "location": f"{node.name} (line {node.lineno})",
                            "severity": "medium",
                            "description": f"Nesting depth of {depth} - hard to read and test",
                        }
                    )

        # Duplicate code (simple check)
        lines = code.split("\n")
        duplicates = self._find_duplicate_lines(lines)
        if duplicates > 10:
            smells.append(
                {
                    "smell": "Code Duplication",
                    "location": "Multiple locations",
                    "severity": "medium",
                    "description": f"Found {duplicates} potentially duplicate lines",
                }
            )

        return smells

    def _check_best_practices(self, tree: ast.AST, code: str) -> Dict[str, Any]:
        """Check adherence to Python best practices."""
        checks = {
            "has_docstrings": self._check_docstrings(tree),
            "has_type_hints": self._check_type_hints(tree),
            "proper_naming": self._check_naming_conventions(tree),
            "error_handling": self._check_error_handling(tree),
            "score": 0,
        }

        # Calculate score
        score = sum(
            [
                25 if checks["has_docstrings"]["percentage"] > 50 else 0,
                25 if checks["has_type_hints"]["percentage"] > 30 else 0,
                25 if checks["proper_naming"]["issues"] == 0 else 0,
                25 if checks["error_handling"]["has_try_except"] else 0,
            ]
        )

        checks["score"] = score
        checks["grade"] = self._score_to_grade(score)

        return checks

    def _is_singleton(self, cls: ast.ClassDef) -> bool:
        """Check if class implements Singleton pattern."""
        for node in cls.body:
            if isinstance(node, ast.FunctionDef):
                if node.name in ["__new__", "instance", "get_instance"]:
                    return True
        return False

    def _is_factory(self, cls: ast.ClassDef) -> bool:
        """Check if class implements Factory pattern."""
        method_names = [n.name for n in cls.body if isinstance(n, ast.FunctionDef)]
        factory_keywords = ["create", "build", "make", "factory"]
        return any(
            keyword in method.lower()
            for method in method_names
            for keyword in factory_keywords
        )

    def _is_observer(self, cls: ast.ClassDef) -> bool:
        """Check if class implements Observer pattern."""
        method_names = [n.name for n in cls.body if isinstance(n, ast.FunctionDef)]
        observer_keywords = ["attach", "detach", "notify", "subscribe", "unsubscribe"]
        return any(
            keyword in method.lower()
            for method in method_names
            for keyword in observer_keywords
        )

    def _is_decorator_pattern(self, cls: ast.ClassDef) -> bool:
        """Check if class implements Decorator pattern."""
        # Look for wrapping behavior
        for base in cls.bases:
            if isinstance(base, ast.Name):
                for node in cls.body:
                    if isinstance(node, ast.FunctionDef) and node.name == "__init__":
                        return True
        return False

    def _calculate_nesting_depth(self, node: ast.AST, depth: int = 0) -> int:
        """Calculate maximum nesting depth in a function."""
        max_depth = depth
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                child_depth = self._calculate_nesting_depth(child, depth + 1)
                max_depth = max(max_depth, child_depth)
        return max_depth

    def _find_duplicate_lines(self, lines: List[str]) -> int:
        """Find potentially duplicate lines."""
        line_counts = defaultdict(int)
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and len(stripped) > 20:
                line_counts[stripped] += 1
        return sum(count - 1 for count in line_counts.values() if count > 1)

    def _check_docstrings(self, tree: ast.AST) -> Dict[str, Any]:
        """Check for docstring presence."""
        functions = [
            n
            for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]

        total = len(functions) + len(classes)
        with_docs = sum(1 for n in functions + classes if ast.get_docstring(n))

        return {
            "total": total,
            "with_docstrings": with_docs,
            "percentage": round((with_docs / max(total, 1)) * 100, 1),
        }

    def _check_type_hints(self, tree: ast.AST) -> Dict[str, Any]:
        """Check for type hint usage."""
        functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]

        total_params = 0
        annotated_params = 0

        for func in functions:
            for arg in func.args.args:
                total_params += 1
                if arg.annotation:
                    annotated_params += 1

        return {
            "total_parameters": total_params,
            "annotated": annotated_params,
            "percentage": round((annotated_params / max(total_params, 1)) * 100, 1),
        }

    def _check_naming_conventions(self, tree: ast.AST) -> Dict[str, Any]:
        """Check PEP 8 naming conventions."""
        issues = []

        # Check function names (should be snake_case)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if (
                    not node.name.islower()
                    and "_" not in node.name
                    and not node.name.startswith("__")
                ):
                    issues.append(f"Function '{node.name}' should use snake_case")

        # Check class names (should be PascalCase)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if not node.name[0].isupper():
                    issues.append(f"Class '{node.name}' should use PascalCase")

        return {"issues": len(issues), "details": issues[:5]}  # First 5 issues

    def _check_error_handling(self, tree: ast.AST) -> Dict[str, Any]:
        """Check for error handling."""
        has_try = any(isinstance(node, ast.Try) for node in ast.walk(tree))
        has_raise = any(isinstance(node, ast.Raise) for node in ast.walk(tree))

        return {
            "has_try_except": has_try,
            "has_raise": has_raise,
            "adequate": has_try or has_raise,
        }

    def _score_to_grade(self, score: int) -> str:
        """Convert score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 75:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 40:
            return "D"
        else:
            return "F"

    def _generate_recommendations(self, patterns: Dict) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Based on code smells
        if patterns["code_smells"]:
            high_severity = [
                s for s in patterns["code_smells"] if s["severity"] == "high"
            ]
            if high_severity:
                recommendations.append(
                    "🔴 Critical: Address high-severity code smells first"
                )

        # Based on best practices
        bp = patterns["best_practices"]
        if bp["has_docstrings"]["percentage"] < 50:
            recommendations.append("📝 Add docstrings to improve code documentation")
        if bp["has_type_hints"]["percentage"] < 30:
            recommendations.append(
                "🔤 Add type hints for better code clarity and IDE support"
            )
        if not bp["error_handling"]["adequate"]:
            recommendations.append(
                "⚠️ Implement proper error handling with try-except blocks"
            )

        # Based on architectural style
        style = patterns["architectural_style"]["style"]
        if style == "Mixed/Hybrid":
            recommendations.append(
                "🏗️ Consider establishing a consistent architectural pattern"
            )

        if not recommendations:
            recommendations.append("✅ Code follows good practices! Keep it up!")

        return recommendations


# Global instance
architecture_detector = ArchitectureDetector()
