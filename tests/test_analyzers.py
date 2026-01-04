"""Tests for code analysis engines."""

from src.ast_analyzer import ast_analyzer
from src.complexity_analyzer import complexity_analyzer
from src.dependency_analyzer import dependency_analyzer
from src.architecture_detector import architecture_detector

# Sample test code
SIMPLE_CODE = """
def greet(name: str) -> str:
    return f"Hello, {name}!"
"""

COMPLEX_CODE = """
import os
import sys
from typing import List

class Calculator:
    '''A simple calculator class.'''

    def __init__(self):
        self.history = []

    def add(self, a: int, b: int) -> int:
        '''Add two numbers.'''
        result = a + b
        self.history.append(result)
        return result

    def complex_calc(self, x):
        if x > 0:
            if x > 10:
                if x > 100:
                    return x * 2
                return x + 10
            return x + 1
        return 0

def fetch_data(url):
    return os.system(f'curl {url}')
"""


def test_ast_analyzer_simple_code():
    """Test AST analyzer with simple code."""
    result = ast_analyzer.analyze_code(SIMPLE_CODE)
    assert "functions" in result
    assert len(result["functions"]) == 1
    assert result["functions"][0]["name"] == "greet"
    assert "name" in result["functions"][0]["args"]


def test_ast_analyzer_complex_code():
    """Test AST analyzer with complex code."""
    result = ast_analyzer.analyze_code(COMPLEX_CODE)
    assert "classes" in result
    assert "functions" in result
    assert "imports" in result
    assert len(result["classes"]) == 1
    assert result["classes"][0]["name"] == "Calculator"


def test_complexity_analyzer():
    """Test complexity analyzer."""
    result = complexity_analyzer.analyze_complexity(COMPLEX_CODE)
    assert "cyclomatic_complexity" in result
    assert "maintainability_index" in result
    assert "quality_grade" in result
    assert isinstance(result["quality_grade"]["grade"], str)


def test_complexity_simple_code():
    """Test complexity with simple code."""
    result = complexity_analyzer.analyze_complexity(SIMPLE_CODE)
    assert "maintainability_index" in result
    # Simple code should have good maintainability
    assert result["maintainability_index"]["score"] > 50


def test_dependency_analyzer():
    """Test dependency analyzer."""
    result = dependency_analyzer.analyze_dependencies(COMPLEX_CODE)
    assert "stdlib_imports" in result
    assert "third_party_imports" in result
    assert "dependency_graph" in result
    assert "os" in result["stdlib_imports"]


def test_architecture_detector():
    """Test architecture pattern detector."""
    result = architecture_detector.detect_patterns(COMPLEX_CODE)
    assert "design_patterns" in result
    assert "architectural_style" in result
    assert "code_smells" in result
    assert "best_practices" in result
    assert "recommendations" in result


def test_architecture_best_practices():
    """Test best practices checking."""
    result = architecture_detector.detect_patterns(COMPLEX_CODE)
    assert "best_practices" in result
    bp = result["best_practices"]
    assert "has_docstrings" in bp
    assert "has_type_hints" in bp
    assert "score" in bp
    assert "grade" in bp


def test_code_smell_detection():
    """Test code smell detection."""
    result = architecture_detector.detect_patterns(COMPLEX_CODE)
    assert "code_smells" in result
    # Code smells may or may not be detected depending on thresholds
    # Just verify the structure is correct
    smells = result["code_smells"]
    assert isinstance(smells, list)
    # If smells are detected, verify they have proper structure
    if smells:
        assert "smell" in smells[0]
        assert "severity" in smells[0]


def test_ast_error_handling():
    """Test AST analyzer with invalid code."""
    invalid_code = "def broken syntax here"
    result = ast_analyzer.analyze_code(invalid_code)
    assert "error" in result


def test_dependency_empty_code():
    """Test dependency analyzer with minimal code."""
    minimal_code = "x = 1"
    result = dependency_analyzer.analyze_dependencies(minimal_code)
    assert result["total_imports"] == 0
    assert len(result["stdlib_imports"]) == 0
