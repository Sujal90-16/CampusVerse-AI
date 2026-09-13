from dataclasses import dataclass, field
from typing import Any

from ..prompts.builder import PromptBuilder
from ..providers.base import LLMProvider
from .context import CampusContext
from .grounding import GroundingService
from .intent import Intent, detect_intent


@dataclass(slots=True)
class UserContext:
    """
    Information about the current CampusVerse user.

    This context can later be populated from the CampusVerse
    backend authentication/database layer.
    """

    user_id: str | None = None
    role: str | None = None
    department: str | None = None
    semester: str | None = None

    # Additional information that may be useful to SHAAN.
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AIRequest:
    """
    Standard request object passed into SHAAN.
    """

    message: str

    # User context is optional because some campus questions
    # do not require authentication.
    user: UserContext = field(default_factory=UserContext)


@dataclass(slots=True)
class AIResponse:
    """
    Standard response returned by SHAAN.
    """

    answer: str

    # Intent detected by the SHAAN routing layer.
    intent: Intent

    # Sources used to construct the answer.
    sources: list[dict[str, Any]] = field(default_factory=list)

    # Optional metadata useful for debugging, analytics,
    # evaluation, and future observability.
    metadata: dict[str, Any] = field(default_factory=dict)


class SHAANOrchestrator:
    """
    Central orchestration layer for SHAAN.

    The orchestrator coordinates the major SHAAN components:

        User Request
             ↓
        Intent Detection
             ↓
        Campus Context
             ↓
        Grounding
             ↓
        Prompt Builder
             ↓
        LLM Provider
             ↓
        AIResponse

    The orchestrator does not depend on a specific LLM provider.
    Any implementation of LLMProvider can be injected.
    """

    def __init__(
        self,
        provider: LLMProvider,
        *,
        prompt_builder: PromptBuilder | None = None,
        grounding_service: GroundingService | None = None,
    ) -> None:
        """
        Initialize the SHAAN orchestration layer.

        The LLM provider is injected so SHAAN remains independent
        from Gemini, OpenAI, local models, or any other provider.
        """

        self.name = "SHAAN"
        self.provider = provider
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.grounding_service = (
            grounding_service or GroundingService()
        )

    def create_request(
        self,
        message: str,
        user: UserContext | None = None,
    ) -> AIRequest:
        """
        Create a normalized SHAAN request.
        """

        return AIRequest(
            message=message.strip(),
            user=user or UserContext(),
        )

    def create_response(
        self,
        answer: str,
        intent: Intent,
        sources: list[dict[str, Any]] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AIResponse:
        """
        Create a normalized SHAAN response.
        """

        return AIResponse(
            answer=answer,
            intent=intent,
            sources=sources or [],
            metadata=metadata or {},
        )

    def process(
        self,
        request: AIRequest,
        campus_context: CampusContext | None = None,
    ) -> AIResponse:
        """
        Process a complete SHAAN request.

        This method coordinates intent detection, grounding,
        prompt construction, and LLM generation.
        """

        # Step 1: Detect the user's intent.
        intent = detect_intent(request.message)

        # Step 2: Convert trusted campus context into a
        # grounding context for the LLM.
        grounding = self.grounding_service.build(
            campus_context
        )

        # Step 3: Build the complete provider-independent prompt.
        prompt = self.prompt_builder.build(
            request=request,
            grounding=grounding,
            intent=intent.value,
        )

        # Step 4: Ask the injected LLM provider for an answer.
        answer = self.provider.generate(prompt)

        # Step 5: Return a normalized SHAAN response.
        return self.create_response(
            answer=answer,
            intent=intent,
            metadata={
                "provider": self.provider.__class__.__name__,
            },
        )