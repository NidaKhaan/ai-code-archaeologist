"""GitHub repository analysis and cloning."""

import os
import tempfile
import shutil
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
from github import Github, GithubException
from git import Repo, GitCommandError

logger = logging.getLogger(__name__)


class GitHubAnalyzer:
    """Analyze GitHub repositories."""

    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize GitHub analyzer.

        Args:
            github_token: GitHub personal access token (optional, for higher rate limits)
        """
        self.github = Github(github_token) if github_token else Github()
        self.temp_dir = None

    def get_repository_info(self, repo_url: str) -> Dict[str, Any]:
        """
        Get basic repository information from GitHub API.

        Args:
            repo_url: GitHub repository URL

        Returns:
            Dictionary with repository information
        """
        try:
            # Extract owner/repo from URL
            owner, repo_name = self._parse_repo_url(repo_url)

            # Fetch repo from GitHub
            repo = self.github.get_repo(f"{owner}/{repo_name}")

            return {
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "language": repo.language,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "open_issues": repo.open_issues_count,
                "size_kb": repo.size,
                "created_at": repo.created_at.isoformat(),
                "updated_at": repo.updated_at.isoformat(),
                "default_branch": repo.default_branch,
                "topics": repo.get_topics(),
                "license": repo.license.name if repo.license else None,
                "has_wiki": repo.has_wiki,
                "has_issues": repo.has_issues,
                "url": repo.html_url,
                "clone_url": repo.clone_url,
            }

        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            return {"error": f"Failed to fetch repository: {str(e)}"}
        except Exception as e:
            logger.error(f"Error getting repo info: {e}", exc_info=True)
            return {"error": str(e)}

    def get_file_structure(self, repo_url: str, max_depth: int = 3) -> Dict[str, Any]:
        """
        Get repository file structure without cloning.

        Args:
            repo_url: GitHub repository URL
            max_depth: Maximum directory depth to traverse

        Returns:
            File structure information
        """
        try:
            owner, repo_name = self._parse_repo_url(repo_url)
            repo = self.github.get_repo(f"{owner}/{repo_name}")

            # Get default branch contents
            contents = repo.get_contents("")
            structure = self._build_tree(contents, max_depth)

            # Count files by extension
            file_counts = self._count_files_by_type(structure)

            return {
                "total_files": structure["file_count"],
                "total_directories": structure["dir_count"],
                "file_types": file_counts,
                "structure": structure["tree"],
                "size_estimate_kb": structure["total_size"],
            }

        except Exception as e:
            logger.error(f"Error getting file structure: {e}", exc_info=True)
            return {"error": str(e)}

    def clone_repository(self, repo_url: str) -> Optional[str]:
        """
        Clone a repository to temporary directory.

        Args:
            repo_url: GitHub repository URL

        Returns:
            Path to cloned repository or None if failed
        """
        try:
            # Create temp directory
            self.temp_dir = tempfile.mkdtemp(prefix="code_archaeologist_")
            logger.info(f"Cloning {repo_url} to {self.temp_dir}")

            # Clone repository
            Repo.clone_from(repo_url, self.temp_dir, depth=1)  # Shallow clone

            return self.temp_dir

        except GitCommandError as e:
            logger.error(f"Git clone error: {e}")
            self.cleanup()
            return None
        except Exception as e:
            logger.error(f"Error cloning repository: {e}", exc_info=True)
            self.cleanup()
            return None

    def get_python_files(self, repo_path: str) -> List[Dict[str, Any]]:
        """
        Get all Python files from cloned repository.

        Args:
            repo_path: Path to cloned repository

        Returns:
            List of Python files with metadata
        """
        python_files = []
        repo_path_obj = Path(repo_path)

        for py_file in repo_path_obj.rglob("*.py"):
            # Skip virtual environments and build directories
            if any(
                skip in py_file.parts
                for skip in ["venv", "env", ".venv", "build", "dist", "__pycache__"]
            ):
                continue

            try:
                relative_path = py_file.relative_to(repo_path_obj)
                file_size = py_file.stat().st_size

                # Read file content (with size limit)
                if file_size < 500000:  # Skip files larger than 500KB
                    with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        line_count = len(content.splitlines())
                else:
                    content = None
                    line_count = 0

                python_files.append(
                    {
                        "path": str(relative_path),
                        "size_bytes": file_size,
                        "line_count": line_count,
                        "content": content,
                    }
                )

            except Exception as e:
                logger.warning(f"Error reading file {py_file}: {e}")
                continue

        return python_files

    def cleanup(self):
        """Clean up temporary directory."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temp directory: {self.temp_dir}")
                self.temp_dir = None
            except Exception as e:
                logger.error(f"Error cleaning up temp dir: {e}")

    def _parse_repo_url(self, repo_url: str) -> tuple:
        """Parse owner and repo name from GitHub URL."""
        # Handle various URL formats
        url = repo_url.replace("https://github.com/", "").replace(".git", "")
        parts = url.split("/")

        if len(parts) < 2:
            raise ValueError(f"Invalid GitHub URL: {repo_url}")

        return parts[0], parts[1]

    def _build_tree(self, contents, max_depth: int, current_depth: int = 0) -> Dict:
        """Recursively build file tree."""
        tree = []
        file_count = 0
        dir_count = 0
        total_size = 0

        if current_depth >= max_depth:
            return {"tree": tree, "file_count": 0, "dir_count": 0, "total_size": 0}

        for content in contents:
            if content.type == "dir":
                dir_count += 1
                if current_depth < max_depth - 1:
                    try:
                        sub_contents = content.repository.get_contents(content.path)
                        sub_tree = self._build_tree(
                            sub_contents, max_depth, current_depth + 1
                        )
                        tree.append(
                            {
                                "name": content.name,
                                "type": "directory",
                                "children": sub_tree["tree"],
                            }
                        )
                        file_count += sub_tree["file_count"]
                        dir_count += sub_tree["dir_count"]
                        total_size += sub_tree["total_size"]
                    except Exception as e:
                        logger.debug(f"Could not fetch directory contents: {e}")
                        pass
                else:
                    tree.append({"name": content.name, "type": "directory"})
            else:
                file_count += 1
                total_size += content.size
                tree.append(
                    {"name": content.name, "type": "file", "size": content.size}
                )

        return {
            "tree": tree,
            "file_count": file_count,
            "dir_count": dir_count,
            "total_size": total_size,
        }

    def _count_files_by_type(self, structure: Dict) -> Dict[str, int]:
        """Count files by extension."""
        counts = {}

        def count_recursive(tree):
            for item in tree:
                if item["type"] == "file":
                    ext = Path(item["name"]).suffix or "no_extension"
                    counts[ext] = counts.get(ext, 0) + 1
                elif item["type"] == "directory" and "children" in item:
                    count_recursive(item["children"])

        count_recursive(structure.get("tree", []))
        return counts


# Global instance
github_analyzer = GitHubAnalyzer()
