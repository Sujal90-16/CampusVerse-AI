"""
Exceptions used by SHAAN LLM providers.
"""


class LLMProviderError(Exception):
    """
    Base exception for failures originating from an LLM provider.

    Provider-specific exceptions should be converted into this
    exception before they leave the provider layer.
    """

    def __init__(
        self,
        message: str,
        *,
        provider: str | None = None,
    ) -> None:
        super().__init__(message)
        self.provider = provider