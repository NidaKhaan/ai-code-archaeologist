"""Tests for utility functions."""

from src.utils import greet, validate_github_url


def test_greet():
    """Test the greet function."""
    result = greet("Alice")
    assert result == "Hello, Alice! Welcome to AI Code Archaeologist."
    assert "Alice" in result


def test_greet_empty_name():
    """Test greet with empty string."""
    result = greet("")
    assert result == "Hello, ! Welcome to AI Code Archaeologist."


def test_validate_github_url_valid():
    """Test valid GitHub URLs."""
    assert validate_github_url("https://github.com/torvalds/linux") is True
    assert validate_github_url("https://github.com/microsoft/vscode") is True


def test_validate_github_url_invalid():
    """Test invalid GitHub URLs."""
    assert validate_github_url("https://gitlab.com/user/repo") is False
    assert validate_github_url("not-a-url") is False
    assert validate_github_url("https://github.com/") is False
    assert validate_github_url("https://github.com/onlyuser") is False
