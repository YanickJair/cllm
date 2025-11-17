from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class AnalyzerBase(ABC):
    """
    Generic base class for analyzers.

    All analyzers (entity, sentiment, temporal, transcript-level)
    should subclass this and implement the `analyze` method.
    """

    def __init__(self, name: str, domain: str = "generic", backend: Optional[Any] = None):
        self.name = name
        self.domain = domain
        self.backend = backend  # e.g., spaCy model, LLM API client, etc.
        self.config: Dict[str, Any] = {}
        self.rules: Dict[str, Any] = {}

    def configure(self, **kwargs):
        """Set configuration dynamically."""
        self.config.update(kwargs)

    def register_rules(self, name: str, rules: Dict[str, Any]):
        """Register or update rule sets dynamically."""
        self.rules[name] = rules

    def get_rules(self, name: str) -> Optional[Dict[str, Any]]:
        return self.rules.get(name)

    def setup(self):
        """Optional setup hook for loading models, etc."""
        pass

    def teardown(self):
        """Optional cleanup hook."""
        pass

    @abstractmethod
    def analyze(self, text: str, **kwargs) -> Any:
        """Perform analysis on input text."""
        pass
