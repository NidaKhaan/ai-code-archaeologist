"""LLM provider abstraction - supports multiple AI providers."""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import httpx

load_dotenv()


class LLMProvider:
    """Base class for LLM providers."""

    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.default_provider = os.getenv("DEFAULT_LLM_PROVIDER", "ollama")

    async def generate(
        self,
        prompt: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 1000,
    ) -> Dict[str, Any]:
        """
        Generate response from LLM.

        Args:
            prompt: The prompt to send
            provider: 'ollama', 'groq', or None (uses default)
            model: Specific model to use
            max_tokens: Maximum tokens in response

        Returns:
            Dict with response text and metadata
        """
        provider = provider or self.default_provider

        if provider == "ollama":
            return await self._generate_ollama(prompt, model or "codellama:7b")
        elif provider == "groq":
            return await self._generate_groq(
                prompt, model or "llama3-8b-8192", max_tokens
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def _generate_ollama(self, prompt: str, model: str) -> Dict[str, Any]:
        """Generate using local Ollama."""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.ollama_base_url}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            data = response.json()

            return {
                "text": data.get("response", ""),
                "provider": "ollama",
                "model": model,
                "tokens_used": data.get("eval_count", 0),
            }

    async def _generate_groq(
        self, prompt: str, model: str, max_tokens: int
    ) -> Dict[str, Any]:
        """Generate using Groq API."""
        from groq import AsyncGroq

        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment")

        client = AsyncGroq(api_key=self.groq_api_key)

        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7,
        )

        return {
            "text": response.choices[0].message.content,
            "provider": "groq",
            "model": model,
            "tokens_used": response.usage.total_tokens,
        }


# Global instance
llm_provider = LLMProvider()
