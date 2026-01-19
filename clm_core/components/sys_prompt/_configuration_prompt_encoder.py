import re
from clm_core import CLMOutput
from spacy.language import Language

from clm_core.utils.parser_rules import BaseRules
from clm_core.utils.vocabulary import BaseVocabulary
from ._schemas import SysPromptConfig
from .analyzers.attribute_parser import AttributeParser

from clm_core.components.sys_prompt.base_encoder import BasePromptEncoder
from clm_core.components.sys_prompt._schemas import PromptTemplate
from clm_core.components.sys_prompt._prompt_template_validator import PromptTemplateValidator

_ROLE_PATTERN = re.compile(
    r"(you are|your role is)\s+(?:an?|the)?\s*"
    r"([a-zA-Z][a-zA-Z_ ]*?)"
    r"(?=\s*(?:\.|,?\s*(?:Follow|Please|Your task|that follows|who follows))|\s*$)",
    re.IGNORECASE,
)
_PLACEHOLDER_PATTERN = re.compile(r"\{\{([^}]+)\}\}")


class ConfigurationPromptEncoder(BasePromptEncoder):
    def __init__(
        self,
        nlp: Language,
        vocab: BaseVocabulary,
        rules: BaseRules,
        config: SysPromptConfig = SysPromptConfig(),
    ):
        self._template_validator = PromptTemplateValidator()
        self._config = config
        self.attribute_parser = AttributeParser(
            nlp=nlp, config=config, vocab=vocab, rules=rules
        )

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
                "output_format": template.output_format,
                "validation": [issue.model_dump() for issue in validation_issues]
            },
        )

    def compress_batch(
        self, prompts: list[str], verbose: bool = False
    ) -> list[CLMOutput]:
        return [self.compress(p, verbose=verbose) for p in prompts]

    def _build_template(self, prompt: str) -> PromptTemplate:
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

        output_format = None
        if self._config.use_structured_output_abstraction:
            output_format = self.attribute_parser.parse_output_format(prompt).build_token()
            parts.append(output_format)

        return PromptTemplate(
            raw_template=prompt,
            placeholders=placeholders,
            output_format=output_format,
            role=role,
            rules=rules,
            priority=priority,
            compressed="".join(parts),
        )
