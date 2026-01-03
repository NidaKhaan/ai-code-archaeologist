"""Dependency and architecture analysis."""

import ast
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class DependencyAnalyzer:
    """Analyze code dependencies and architecture patterns."""

    def analyze_dependencies(
        self, code: str, filename: str = "main.py"
    ) -> Dict[str, Any]:
        """
        Analyze import dependencies and relationships.

        Args:
            code: Python source code
            filename: Name of the file being analyzed

        Returns:
            Dictionary with dependency information
        """
        try:
            tree = ast.parse(code)

            imports = self._extract_detailed_imports(tree)
            dependencies = self._categorize_dependencies(imports)
            graph = self._build_dependency_graph(imports, filename)

            return {
                "total_imports": len(imports),
                "stdlib_imports": dependencies["stdlib"],
                "third_party_imports": dependencies["third_party"],
                "local_imports": dependencies["local"],
                "dependency_graph": graph,
                "import_complexity": self._calculate_import_complexity(imports),
                "potential_circular": self._detect_potential_circular(imports),
            }

        except Exception as e:
            logger.error(f"Error analyzing dependencies: {e}", exc_info=True)
            return {"error": str(e)}

    def _extract_detailed_imports(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract detailed import information."""
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(
                        {
                            "type": "import",
                            "module": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno,
                            "level": 0,
                        }
                    )
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(
                        {
                            "type": "from_import",
                            "module": module,
                            "name": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno,
                            "level": node.level,  # Relative import level
                        }
                    )

        return imports

    def _categorize_dependencies(self, imports: List[Dict]) -> Dict[str, List[str]]:
        """Categorize imports into stdlib, third-party, and local."""
        # Common Python stdlib modules (partial list)
        stdlib_modules = {
            "os",
            "sys",
            "json",
            "math",
            "datetime",
            "re",
            "collections",
            "itertools",
            "functools",
            "typing",
            "pathlib",
            "logging",
            "unittest",
            "subprocess",
            "threading",
            "asyncio",
            "contextlib",
            "dataclasses",
            "enum",
            "abc",
            "copy",
            "pickle",
            "tempfile",
            "shutil",
            "glob",
            "time",
            "random",
            "string",
            "io",
            "csv",
        }

        categorized = {"stdlib": [], "third_party": [], "local": []}

        for imp in imports:
            module = imp["module"]
            base_module = module.split(".")[0] if module else ""

            if imp["level"] > 0:  # Relative import
                categorized["local"].append(module or imp.get("name", ""))
            elif base_module in stdlib_modules:
                categorized["stdlib"].append(module)
            elif base_module:
                categorized["third_party"].append(module)

        # Remove duplicates
        for key in categorized:
            categorized[key] = list(set(categorized[key]))

        return categorized

    def _build_dependency_graph(
        self, imports: List[Dict], filename: str
    ) -> Dict[str, Any]:
        """Build a dependency graph structure."""
        graph = {"nodes": [filename], "edges": []}

        for imp in imports:
            module = imp["module"]
            if module:
                if module not in graph["nodes"]:
                    graph["nodes"].append(module)
                graph["edges"].append(
                    {"from": filename, "to": module, "type": imp["type"]}
                )

        return graph

    def _calculate_import_complexity(self, imports: List[Dict]) -> Dict[str, Any]:
        """Calculate import complexity metrics."""
        total = len(imports)
        relative_imports = sum(1 for imp in imports if imp["level"] > 0)
        wildcard_imports = sum(1 for imp in imports if imp.get("name") == "*")

        return {
            "total_imports": total,
            "relative_imports": relative_imports,
            "wildcard_imports": wildcard_imports,
            "complexity_score": (relative_imports * 2 + wildcard_imports * 3)
            / max(total, 1),
        }

    def _detect_potential_circular(self, imports: List[Dict]) -> List[str]:
        """Detect potential circular import patterns."""
        # This is a simplified detection - real circular imports need multi-file analysis
        warnings = []

        # Check for same-package relative imports
        relative_imports = [imp for imp in imports if imp["level"] > 0]
        if len(relative_imports) > 3:
            warnings.append(
                f"High number of relative imports ({len(relative_imports)}) may indicate circular dependencies"
            )

        # Check for wildcard imports
        wildcard_imports = [imp for imp in imports if imp.get("name") == "*"]
        if wildcard_imports:
            warnings.append(
                f"High number of relative imports ({len(relative_imports)}) "
                "may indicate circular dependencies"
            )

        return warnings


# Global instance
dependency_analyzer = DependencyAnalyzer()
