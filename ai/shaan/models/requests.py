from dataclasses import dataclass, field
from typing import Any

from ..services.intent import Intent


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