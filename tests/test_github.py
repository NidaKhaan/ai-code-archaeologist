"""Tests for GitHub analyzer."""

import pytest
from src.github_analyzer import GitHubAnalyzer


@pytest.fixture
def analyzer():
    """Create GitHub analyzer instance."""
    return GitHubAnalyzer()


def test_parse_repo_url(analyzer):
    """Test parsing GitHub URLs."""
    owner, repo = analyzer._parse_repo_url("https://github.com/psf/requests")
    assert owner == "psf"
    assert repo == "requests"

    # Test without https
    owner, repo = analyzer._parse_repo_url("github.com/python/cpython")
    assert owner == "python"
    assert repo == "cpython"

    # Test with .git
    owner, repo = analyzer._parse_repo_url("https://github.com/torvalds/linux.git")
    assert owner == "torvalds"
    assert repo == "linux"


def test_parse_invalid_url(analyzer):
    """Test parsing invalid URLs."""
    with pytest.raises(ValueError):
        analyzer._parse_repo_url("not-a-url")

    with pytest.raises(ValueError):
        analyzer._parse_repo_url("https://github.com/onlyowner")


def test_get_repository_info(analyzer):
    """Test fetching repository info from GitHub API."""
    # Use a well-known stable repo
    info = analyzer.get_repository_info("https://github.com/psf/requests")

    assert "error" not in info
    assert info["name"] == "requests"
    assert info["language"] == "Python"
    assert "stars" in info
    assert "forks" in info
    assert info["stars"] > 0  # Popular repo should have stars


def test_get_repository_info_invalid(analyzer):
    """Test fetching info for invalid/non-existent repo."""
    info = analyzer.get_repository_info("https://github.com/nonexistent/fakerepo12345")

    assert "error" in info


def test_get_file_structure(analyzer):
    """Test getting repository file structure."""
    structure = analyzer.get_file_structure(
        "https://github.com/psf/requests", max_depth=2
    )

    assert "error" not in structure
    assert "total_files" in structure
    assert "file_types" in structure
    assert structure["total_files"] > 0
    assert ".py" in structure["file_types"]  # Should have Python files


def test_count_files_by_type(analyzer):
    """Test file counting by extension."""
    mock_structure = {
        "tree": [
            {"name": "file1.py", "type": "file"},
            {"name": "file2.py", "type": "file"},
            {"name": "readme.md", "type": "file"},
            {
                "name": "folder",
                "type": "directory",
                "children": [
                    {"name": "file3.py", "type": "file"},
                    {"name": "config.json", "type": "file"},
                ],
            },
        ]
    }

    counts = analyzer._count_files_by_type(mock_structure)

    assert counts[".py"] == 3
    assert counts[".md"] == 1
    assert counts[".json"] == 1


def test_cleanup(analyzer):
    """Test cleanup method doesn't crash."""
    # Should not raise error even if temp_dir is None
    analyzer.cleanup()
    assert analyzer.temp_dir is None


@pytest.mark.skip(reason="Cloning takes time, skip in CI")
def test_clone_repository(analyzer):
    """Test cloning a small repository."""
    # Use a very small repo for testing
    repo_path = analyzer.clone_repository("https://github.com/kennethreitz/setup.py")

    try:
        assert repo_path is not None
        assert analyzer.temp_dir is not None

        # Check if Python files can be found
        python_files = analyzer.get_python_files(repo_path)
        assert len(python_files) > 0

    finally:
        analyzer.cleanup()
