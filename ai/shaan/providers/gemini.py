import os

from google import genai

from .base import LLMProvider


class GeminiProvider(LLMProvider):
    """
    Thin provider wrapper around Google's Gemini API.

    SHAAN business logic, campus retrieval, RAG, authorization,
    and grounding should remain outside this provider.
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

    def chat(
        self,
        system_context: str,
        user_message: str,
    ) -> str:
        """
        Generate a response using Gemini.

        Campus-specific information must come from application
        context rather than being invented by the model.
        """

        prompt = f"""
You are SHAAN, the AI intelligence layer of CampusVerse,
an intelligent ecosystem for college.

Rules:
- Use only the application context for campus-specific facts.
- Never invent campus dates, rooms, policies, schedules,
  attendance values, notices, assignments, examinations,
  events, or placement information.
- If required campus information is unavailable, clearly
  say that the information is unavailable.
- Be helpful, professional, friendly, concise, and easy
  to understand.
- Do not claim to be Gemini or Google AI.

Application context:
{system_context}

User question:
{user_message}
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        return response.text or (
            "I could not generate a response right now."
        )