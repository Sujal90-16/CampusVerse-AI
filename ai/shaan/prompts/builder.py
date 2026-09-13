"""
Prompt construction utilities for SHAAN.
"""

from typing import Any

from ..models import AIRequest
from ..services.grounding import GroundingContext
from .system import SHAAN_SYSTEM_PROMPT


class PromptBuilder:
    """
    Builds the final prompt sent to an LLM provider.

    This layer keeps prompt construction separate from:
    - intent detection
    - campus data retrieval
    - RAG
    - LLM provider implementations
    """

    def build(
        self,
        request: AIRequest,
        grounding: GroundingContext | None = None,
        intent: str | None = None,
    ) -> str:
        """
        Build a complete SHAAN prompt.
        """

        grounding_text = (
            grounding.to_prompt()
            if grounding is not None
            else "No verified campus information is available."
        )

        user_context = self._build_user_context(request)

        intent_text = intent or "general_campus"

        return f"""
{SHAAN_SYSTEM_PROMPT}

REQUEST INFORMATION
-------------------
Detected intent:
{intent_text}

User context:
{user_context}

VERIFIED CAMPUS CONTEXT
-----------------------
{grounding_text}

USER QUESTION
-------------
{request.message}

ANSWERING INSTRUCTIONS
----------------------
Answer the user's question using the rules above.

For campus-specific questions:
- Use the verified campus context.
- Do not invent missing information.
- If the required information is unavailable, say so clearly.

For general questions:
- Provide a useful answer using general knowledge.

Return only the answer that should be shown to the user.
""".strip()

    @staticmethod
    def _build_user_context(request: AIRequest) -> dict[str, Any]:
        """
        Convert UserContext into a prompt-safe dictionary.
        """

        user = request.user

        context: dict[str, Any] = {
            "role": user.role,
            "department": user.department,
            "semester": user.semester,
        }

        if user.extra:
            context["additional_context"] = user.extra

        return context