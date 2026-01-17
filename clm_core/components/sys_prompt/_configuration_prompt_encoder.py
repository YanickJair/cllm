import re
from clm_core import CLMOutput
from clm_core.components.sys_prompt.base_encoder import BasePromptEncoder
from clm_core.components.sys_prompt._schemas import PromptTemplate
from clm_core.components.sys_prompt._prompt_template_validator import PromptTemplateValidator

_ROLE_PATTERN = re.compile(
    r"(you are|your role is)\s+(?:an?|the)?\s*([a-zA-Z_ ]{3,50})",
    re.IGNORECASE,
)
_PLACEHOLDER_PATTERN = re.compile(r"\{\{([^}]+)\}\}")


class ConfigurationPromptEncoder(BasePromptEncoder):
    def __init__(self):
        self._template_validator = PromptTemplateValidator()

    def compress(self, prompt: str, verbose: bool = False) -> CLMOutput:
        template = self._build_template(prompt)
        validation_issues = self._template_validator.validate(template)

        return CLMOutput(
            original=template.raw_template,
            component="System Prompt",
            compressed=template.compressed,
            metadata={
                "prompt_mode": "CONFIGURATION",
                "role": template.role,
                "rules": template.rules,
                "priority": template.priority,
                "placeholders": template.placeholders,
                "validation": [issue.model_dump() for issue in validation_issues]
            },
        )

    def compress_batch(
        self, prompts: list[str], verbose: bool = False
    ) -> list[CLMOutput]:
        return [self.compress(p, verbose=verbose) for p in prompts]

    @staticmethod
    def _build_template(prompt: str) -> PromptTemplate:
        role = None
        rules = {
            "basic": False,
            "custom": False,
        }
        priority = None

        m = _ROLE_PATTERN.search(prompt)
        if m:
            role = m.group(2).strip().upper().replace(" ", "_")

        if re.search(
                r"<basic_rules>|basic rules|core capabilities",
                prompt,
                re.IGNORECASE,
        ):
            rules["basic"] = True

        if re.search(
                r"<custom_rules>|custom instructions",
                prompt,
                re.IGNORECASE,
        ):
            rules["custom"] = True

        if re.search(
                r"(custom instructions.*(override|prioritize)|custom.*paramount)",
                prompt,
                re.IGNORECASE,
        ):
            priority = "CUSTOM_OVER_BASIC"

        placeholders = sorted(
            set(_PLACEHOLDER_PATTERN.findall(prompt))
        )

        parts = ["[PROMPT_MODE:CONFIGURATION]"]
        if role:
            parts.append(f"[ROLE:{role}]")

        if rules["basic"] or rules["custom"]:
            active = []
            if rules["basic"]:
                active.append("BASIC")
            if rules["custom"]:
                active.append("CUSTOM")
            parts.append(f"[RULES:{','.join(active)}]")

        if priority:
            parts.append(f"[PRIORITY:{priority}]")

        compressed = "".join(parts)

        return PromptTemplate(
            raw_template=prompt,
            placeholders=placeholders,
            role=role,
            rules=rules,
            priority=priority,
            compressed=compressed,
        )
