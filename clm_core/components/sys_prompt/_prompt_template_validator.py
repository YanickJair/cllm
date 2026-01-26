import re
from clm_core.components.sys_prompt._schemas import (
    ValidationIssue,
    ValidationLevel,
    PromptTemplate,
)


_PLACEHOLDER_PATTERN = re.compile(r"\{\{([^}]+)\}\}")


class PromptTemplateValidator:
    @staticmethod
    def validate(template: PromptTemplate) -> list[ValidationIssue]:
        """
        Rule 1: Placeholder names must be non-empty and valid identifiers
        Rule 2: Duplicate placeholders (should not happen, but defensive)
        Rule 3: Priority sanity
        Rule 4: Role presence (soft rule)

        Parameters
        ----------
        template

        Returns
        -------

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

        #
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
    def validate(bound_prompt: str) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []

        # Rule 1: No unresolved placeholders
        unresolved = _PLACEHOLDER_PATTERN.findall(bound_prompt)
        if unresolved:
            issues.append(
                ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message=f"Unresolved placeholders remain: {unresolved}",
                )
            )

        # Rule 2: Empty prompt (paranoia rule)
        if not bound_prompt.strip():
            issues.append(
                ValidationIssue(
                    level=ValidationLevel.ERROR, message="Bound prompt is empty"
                )
            )

        return issues
