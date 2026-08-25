from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CampusContext:
    """
    Structured campus information supplied to SHAAN.

    The context is intentionally provider-agnostic. The backend,
    database, RAG system, or other CampusVerse services can populate
    this object without SHAAN needing to know where the data came from.
    """

    data: dict[str, Any] = field(default_factory=dict)

    def is_empty(self) -> bool:
        """Return True when no campus context is available."""
        return not bool(self.data)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Safely retrieve a value from the campus context.
        """
        return self.data.get(key, default)

    def update(self, values: dict[str, Any]) -> None:
        """
        Add or update campus context values.
        """
        self.data.update(values)

    def to_dict(self) -> dict[str, Any]:
        """
        Return a copy of the structured context.

        Returning a copy prevents callers from accidentally modifying
        the internal context dictionary.
        """
        return dict(self.data)


class CampusContextBuilder:
    """
    Builds normalized CampusContext objects for SHAAN.

    This is the first lightweight version. Later, the builder can
    receive data from CampusVerse backend services such as:

        - authenticated user profile
        - department and semester
        - timetable
        - attendance
        - assignments
        - examinations
        - notices
        - events
        - placements
        - campus policies
        - RAG retrieval results
    """

    def build(
        self,
        *,
        user: dict[str, Any] | None = None,
        academic: dict[str, Any] | None = None,
        campus: dict[str, Any] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> CampusContext:
        """
        Build a normalized CampusContext from available information.
        """

        context: dict[str, Any] = {}

        if user:
            context["user"] = dict(user)

        if academic:
            context["academic"] = dict(academic)

        if campus:
            context["campus"] = dict(campus)

        if extra:
            context["extra"] = dict(extra)

        return CampusContext(data=context)