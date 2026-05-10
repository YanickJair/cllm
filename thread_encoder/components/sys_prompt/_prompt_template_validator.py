import re
from typing import Annotated

from annotated_doc import Doc
from thread_encoder.components.sys_prompt._schemas import (
    ValidationIssue,
    ValidationLevel,
    PromptTemplate,
)


_PLACEHOLDER_PATTERN = re.compile(r"\{\{([^}]+)\}\}")


class PromptTemplateValidator:
    @staticmethod
    def validate(
        template: Annotated[
            PromptTemplate,
            Doc(
                "The PromptTemplate to validate against rules: non-empty placeholder names, no duplicates, priority requires rules, role is present."
            ),
        ],
    ) -> list[ValidationIssue]:
        """
        Validates a PromptTemplate and returns any issues found.

        Rules applied:
          1. Placeholder names must be non-empty and valid identifiers.
          2. No duplicate placeholders.
          3. Priority requires at least one rule to be defined.
          4. Role presence is expected (soft warning if absent).
        """
        issues: list[ValidationIssue] = []

        for p in template.placeholders:
            if not p.strip():
                issues.append(
                    ValidationIssue(
                        level=ValidationLevel.ERROR,
                        message="Empty placeholder detected",
                    )
                )
            elif not p.replace("_", "").isalnum():
                issues.append(
                    ValidationIssue(
                        level=ValidationLevel.WARNING,
                        message=f"Non-standard placeholder name: '{p}'",
                    )
                )

        if len(template.placeholders) != len(set(template.placeholders)):
            issues.append(
                ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message="Duplicate placeholders detected",
                )
            )

        if template.priority and not template.rules:
            issues.append(
                ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message="Priority defined but no rules detected",
                )
            )

        if template.role is None:
            issues.append(
                ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message="No role detected in configuration prompt",
                )
            )

        return issues


class BoundPromptValidator:
    @staticmethod
    def validate(
        bound_prompt: Annotated[
            str,
            Doc(
                "The fully-bound prompt string (all placeholders replaced). Validated for unresolved placeholders and emptiness."
            ),
        ],
    ) -> list[ValidationIssue]:
        """
        Validates a bound prompt string.

        Rules applied:
          1. No unresolved placeholders ({{...}}) may remain.
          2. The prompt must not be empty after binding.
        """
        issues: list[ValidationIssue] = []

        unresolved = _PLACEHOLDER_PATTERN.findall(bound_prompt)
        if unresolved:
            issues.append(
                ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message=f"Unresolved placeholders remain: {unresolved}",
                )
            )

        if not bound_prompt.strip():
            issues.append(
                ValidationIssue(
                    level=ValidationLevel.ERROR, message="Bound prompt is empty"
                )
            )

        return issues
