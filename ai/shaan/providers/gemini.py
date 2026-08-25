import os

from google import genai

from .base import LLMProvider


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
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. "
                "Set it in the environment before using GeminiProvider."
            )

        self.model = (
            model
            or os.getenv("GEMINI_MODEL")
            or self.DEFAULT_MODEL
        )

        self.client = genai.Client(api_key=self.api_key)

    def generate(self, prompt: str) -> str:
        """
        Generate a response using Gemini.

        The prompt is constructed by SHAAN's PromptBuilder.
        This provider only handles communication with Gemini.
        """

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        return response.text or (
            "I could not generate a response right now."
        )