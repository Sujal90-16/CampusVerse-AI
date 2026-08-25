from dataclasses import dataclass, field
from typing import Any

from .intent import Intent


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
    # These may come from RAG, campus APIs, database queries, etc.
    sources: list[dict[str, Any]] = field(default_factory=list)

    # Optional metadata useful for debugging, analytics,
    # evaluation, and future observability.
    metadata: dict[str, Any] = field(default_factory=dict)


class SHAANOrchestrator:
    """
    Central orchestration layer for SHAAN.

    The orchestrator will eventually coordinate:

        User Request
             ↓
        Intent Detection
             ↓
        Context Building
             ↓
        Campus Data / RAG
             ↓
        LLM Provider
             ↓
        Grounding
             ↓
        AIResponse

    The first version intentionally keeps the implementation
    lightweight. Individual services will be connected in
    subsequent development milestones.
    """

    def __init__(self) -> None:
        self.name = "SHAAN"

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