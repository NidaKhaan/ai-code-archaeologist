"""Utility functions for AI Code Archaeologist."""


def greet(name: str) -> str:
    """
    Generate a greeting message.

    Args:
        name: The name to greet

    Returns:
        A greeting string
    """
    return f"Hello, {name}! Welcome to AI Code Archaeologist."


def validate_github_url(url: str) -> bool:
    """
    Validate if a string is a valid GitHub repository URL.

    Args:
        url: The URL to validate

    Returns:
        True if valid GitHub URL, False otherwise
    """
    if not url.startswith("https://github.com/"):
        return False

    parts = url.replace("https://github.com/", "").split("/")
    return len(parts) >= 2 and all(part.strip() for part in parts[:2])
