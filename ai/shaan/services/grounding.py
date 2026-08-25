import json
from typing import Any

from .context import CampusContext


class GroundingContext:
    """
    Represents trusted application data that SHAAN is allowed
    to use when answering campus-specific questions.
    """

    def __init__(self, data: dict[str, Any] | None = None) -> None:
        self.data = data or {}

    def is_empty(self) -> bool:
        return not bool(self.data)

    def to_dict(self) -> dict[str, Any]:
        return dict(self.data)

    def to_prompt(self) -> str:
        """
        Convert trusted campus data into a structured prompt block.
        """

        if self.is_empty():
            return "No verified campus information is available."

        return json.dumps(
            self.data,
            indent=2,
            ensure_ascii=False,
            default=str,
        )


class GroundingService:
    """
    Converts trusted CampusContext into a grounding context.

    The service does not retrieve data itself. Data can later come
    from the backend database, APIs, or the RAG pipeline.
    """

    def build(
        self,
        campus_context: CampusContext | None = None,
        *,
        campus_data: dict[str, Any] | None = None,
    ) -> GroundingContext:
        """
        Build grounding context from trusted campus data.

        CampusContext is the preferred input because it represents
        normalized application context.

        campus_data is retained as a simple compatibility/testing
        path for direct dictionary input.
        """

        if campus_context is not None:
            return GroundingContext(campus_context.to_dict())

        if campus_data:
            return GroundingContext(dict(campus_data))

        return GroundingContext()