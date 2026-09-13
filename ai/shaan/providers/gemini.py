import os

from google import genai

from .base import LLMProvider
from .exceptions import LLMProviderError


class GeminiProvider(LLMProvider):
    """
    Thin provider wrapper around Google's Gemini API.

    SHAAN business logic, campus retrieval, RAG, authorization,
    grounding, and prompt construction remain outside this provider.
    """

    DEFAULT_MODEL = "gemini-2.5-flash"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        """
        Initialize the Gemini client.

        The API key can be supplied directly for testing or loaded
        from the GEMINI_API_KEY environment variable.
        """

        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise LLMProviderError(
                "GEMINI_API_KEY is not configured.",
                provider="gemini",
            )

        self.model = (
            model
            or os.getenv("GEMINI_MODEL")
            or self.DEFAULT_MODEL
        )

        try:
            self.client = genai.Client(api_key=self.api_key)
        except Exception as exc:
            raise LLMProviderError(
                "Failed to initialize the Gemini client.",
                provider="gemini",
            ) from exc

    def generate(self, prompt: str) -> str:
        """
        Generate a response using Gemini.

        Provider-specific errors are converted into
        LLMProviderError before leaving this layer.
        """

        if not prompt.strip():
            raise LLMProviderError(
                "Cannot generate a response from an empty prompt.",
                provider="gemini",
            )

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
        except Exception as exc:
            raise LLMProviderError(
                "Gemini failed to generate a response.",
                provider="gemini",
            ) from exc

        answer = response.text

        if not answer or not answer.strip():
            raise LLMProviderError(
                "Gemini returned an empty response.",
                provider="gemini",
            )

        return answer.strip()