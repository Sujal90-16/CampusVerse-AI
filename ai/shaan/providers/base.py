from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Common interface for all LLM providers used by SHAAN."""

    @abstractmethod
    def chat(
        self,
        system_context: str,
        user_message: str,
    ) -> str:
        """Generate a response using the configured LLM."""
        raise NotImplementedError