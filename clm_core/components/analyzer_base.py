from abc import ABC, abstractmethod
from typing import Annotated, Any, Dict, Optional

from annotated_doc import Doc


class AnalyzerBase(ABC):
    """
    Generic base class for analyzers.

    All analyzers (entity, sentiment, temporal, clm_core-level)
    should subclass this and implement the `analyze` method.
    """

    def __init__(
        self,
        name: Annotated[
            str, Doc("Human-readable identifier for this analyzer instance.")
        ],
        domain: Annotated[
            str,
            Doc(
                "Domain context for this analyzer (e.g. 'generic', 'support', 'finance')."
            ),
        ] = "generic",
        backend: Annotated[
            Optional[Any],
            Doc(
                "Optional backend object (e.g. spaCy model, LLM API client) used by the analyzer."
            ),
        ] = None,
    ):
        self.name = name
        self.domain = domain
        self.backend = backend  # e.g., spaCy model, LLM API client, etc.
        self.config: Dict[str, Any] = {}
        self.rules: Dict[str, Any] = {}

    def configure(
        self,
        **kwargs: Annotated[
            Any,
            Doc(
                "Key-value configuration entries to merge into this analyzer's config dict."
            ),
        ],
    ):
        """Set configuration dynamically."""
        self.config.update(kwargs)

    def register_rules(
        self,
        name: Annotated[str, Doc("Key under which to store the rule set.")],
        rules: Annotated[
            Dict[str, Any],
            Doc(
                "Rule set dict to register; overwrites any existing entry with the same name."
            ),
        ],
    ):
        """Register or update rule sets dynamically."""
        self.rules[name] = rules

    def get_rules(
        self, name: Annotated[str, Doc("Key of the rule set to retrieve.")]
    ) -> Optional[Dict[str, Any]]:
        return self.rules.get(name)

    def setup(self):
        """Optional setup hook for loading models, etc."""
        pass

    def teardown(self):
        """Optional cleanup hook."""
        pass

    @abstractmethod
    def analyze(
        self, text: Annotated[str, Doc("Input text to analyze.")], **kwargs
    ) -> Any:
        """Perform analysis on input text."""
        pass
