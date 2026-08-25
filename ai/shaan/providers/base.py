from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """
    Common interface for all LLM providers used by SHAAN.
    """

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate a response from a complete prompt.
        """
        raise NotImplementedError