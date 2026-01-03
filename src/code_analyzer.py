"""Code analysis service using LLM."""

import logging
from typing import Dict, Any, Optional
from src.llm_provider import llm_provider


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """Analyze code repositories using AI."""

    def __init__(self):
        self.llm = llm_provider

    async def analyze_repository_summary(
        self, repo_url: str, provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a high-level summary of a repository.

        Args:
            repo_url: GitHub repository URL
            provider: LLM provider to use

        Returns:
            Analysis summary
        """
        prompt = f"""Analyze this GitHub repository: {repo_url}

Based on the URL pattern, provide:
1. What type of project this likely is
2. What programming language(s) it probably uses
3. Common architectural patterns for this type of project
4. Potential areas to investigate for bugs
5. Best practices for this type of codebase

Be concise and practical."""

        response = await self.llm.generate(
            prompt=prompt, provider=provider, max_tokens=500
        )

        return {
            "summary": response["text"],
            "provider_used": response["provider"],
            "model_used": response["model"],
            "tokens": response["tokens_used"],
        }

    async def explain_code_snippet(
        self, code: str, language: str = "python", provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Explain what a code snippet does.
        """
        prompt = f"""Explain this {language} code in simple terms:
```{language}
{code}
```

Provide:
1. What it does (1-2 sentences)
2. Key functions/methods
3. Any potential issues or improvements"""

        try:
            logger.info(f"Sending prompt to LLM provider: {provider or 'default'}")
            response = await self.llm.generate(
                prompt=prompt, provider=provider, max_tokens=400
            )
            logger.info(f"Got response from {response['provider']}")

            return {
                "explanation": response["text"],
                "language": language,
                "provider_used": response["provider"],
                "tokens": response["tokens_used"],
            }
        except Exception as e:
            logger.error(f"Error in explain_code_snippet: {e}", exc_info=True)
            raise

    async def suggest_improvements(
        self, code: str, language: str = "python", provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Suggest improvements for code.

        Args:
            code: The code to improve
            language: Programming language
            provider: LLM provider to use

        Returns:
            Improvement suggestions
        """
        prompt = f"""Review this {language} code and suggest improvements:
```{language}
{code}
```

Focus on:
1. Code quality and readability
2. Performance optimizations
3. Potential bugs or edge cases
4. Best practices

Be specific and actionable."""

        response = await self.llm.generate(
            prompt=prompt, provider=provider, max_tokens=600
        )

        return {
            "suggestions": response["text"],
            "language": language,
            "provider_used": response["provider"],
            "tokens": response["tokens_used"],
        }


# Global instance
code_analyzer = CodeAnalyzer()
