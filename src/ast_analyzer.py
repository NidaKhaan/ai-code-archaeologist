"""Abstract Syntax Tree (AST) analyzer for Python code."""

import ast
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class FunctionInfo:
    """Information about a function."""

    name: str
    line_number: int
    args: List[str]
    returns: Optional[str]
    docstring: Optional[str]
    is_async: bool
    complexity: int = 1  # Will calculate later


@dataclass
class ClassInfo:
    """Information about a class."""

    name: str
    line_number: int
    methods: List[str]
    bases: List[str]
    docstring: Optional[str]


@dataclass
class CodeStructure:
    """Complete code structure analysis."""

    total_lines: int
    imports: List[str]
    functions: List[FunctionInfo]
    classes: List[ClassInfo]
    global_variables: List[str]
    complexity_score: float


class ASTAnalyzer:
    """Analyze Python code using AST."""

    def analyze_code(self, code: str) -> Dict[str, Any]:
        """
        Analyze Python code and extract structure.

        Args:
            code: Python source code as string

        Returns:
            Dictionary with code structure information
        """
        try:
            tree = ast.parse(code)

            structure = CodeStructure(
                total_lines=len(code.splitlines()),
                imports=self._extract_imports(tree),
                functions=self._extract_functions(tree),
                classes=self._extract_classes(tree),
                global_variables=self._extract_globals(tree),
                complexity_score=0.0,
            )

            # Calculate overall complexity
            structure.complexity_score = self._calculate_complexity(tree)

            return asdict(structure)

        except SyntaxError as e:
            logger.error(f"Syntax error in code: {e}")
            return {"error": f"Syntax error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error analyzing code: {e}", exc_info=True)
            return {"error": f"Analysis error: {str(e)}"}

    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract all import statements."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}" if module else alias.name)
        return imports

    def _extract_functions(self, tree: ast.AST) -> List[FunctionInfo]:
        """Extract all function definitions."""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_info = FunctionInfo(
                    name=node.name,
                    line_number=node.lineno,
                    args=[arg.arg for arg in node.args.args],
                    returns=self._get_return_annotation(node),
                    docstring=ast.get_docstring(node),
                    is_async=isinstance(node, ast.AsyncFunctionDef),
                    complexity=self._calculate_function_complexity(node),
                )
                functions.append(func_info)
        return functions

    def _extract_classes(self, tree: ast.AST) -> List[ClassInfo]:
        """Extract all class definitions."""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [
                    n.name
                    for n in node.body
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                bases = [self._get_base_name(base) for base in node.bases]

                class_info = ClassInfo(
                    name=node.name,
                    line_number=node.lineno,
                    methods=methods,
                    bases=bases,
                    docstring=ast.get_docstring(node),
                )
                classes.append(class_info)
        return classes

    def _extract_globals(self, tree: ast.AST) -> List[str]:
        """Extract global variable assignments."""
        globals_vars = []
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        globals_vars.append(target.id)
        return globals_vars

    def _get_return_annotation(self, node: ast.FunctionDef) -> Optional[str]:
        """Get return type annotation if present."""
        if node.returns:
            return ast.unparse(node.returns)
        return None

    def _get_base_name(self, base: ast.expr) -> str:
        """Get base class name."""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return ast.unparse(base)
        return "Unknown"

    def _calculate_function_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def _calculate_complexity(self, tree: ast.AST) -> float:
        """Calculate overall code complexity score."""
        total_complexity = 0
        function_count = 0

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                total_complexity += self._calculate_function_complexity(node)
                function_count += 1

        return total_complexity / max(function_count, 1)


# Global instance
ast_analyzer = ASTAnalyzer()
