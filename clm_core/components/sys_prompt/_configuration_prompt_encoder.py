import re
from typing import Optional

from clm_core import CLMOutput
from spacy.language import Language

from clm_core.utils.parser_rules import BaseRules
from clm_core.utils.vocabulary import BaseVocabulary
from . import ConfigurationPromptMinimizer
from ._schemas import SysPromptConfig, ValidationLevel, PromptMode
from .analyzers.attribute_parser import AttributeParser

from clm_core.components.sys_prompt.base_encoder import BasePromptEncoder
from clm_core.components.sys_prompt._schemas import PromptTemplate
from clm_core.components.sys_prompt._prompt_template_validator import PromptTemplateValidator, BoundPromptValidator

_ROLE_PATTERN = re.compile(
    r"(you are|your role is)\s+(?:an?|the)?\s*"
    r"([a-zA-Z][a-zA-Z0-9_ &\-]+?)"
    r"(?=\s*(?:</role>|\.|\s+for\s|,?\s*(?:Follow|Please|Your task|that follows|who follows))|\s*$)",
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
        self._minimizer = ConfigurationPromptMinimizer(
            nlp=nlp,
            config=config
        )

    def bind(self, out: CLMOutput, **runtime_values: Optional[dict]) -> str:
        """
        compose CL + NL
        Args:
        out (CLMOutput)
        runtime_values (dict)
        ----------
        runtime_values

        Returns
        -------

        """
        if out.metadata.get("prompt_mode") != "CONFIGURATION":
            return out.compressed

        template = PromptTemplate(
            raw_template=out.original,
            placeholders=out.metadata["placeholders"],
            role=out.metadata.get("role"),
            rules=out.metadata.get("rules", {}),
            priority=out.metadata.get("priority"),
            compressed=out.compressed,
        )

        bound_nl = template.bind(**runtime_values)

        issues = BoundPromptValidator().validate(bound_nl)
        errors = [i for i in issues if i.level == ValidationLevel.ERROR]
        if errors:
            raise RuntimeError(f"Bound prompt invalid: {errors}")

        if out.metadata["prompt_mode"] == PromptMode.CONFIGURATION:
            bound_nl = self._minimizer.minimize(bound_nl, cl_metadata=out.metadata)

        result = f"{out.compressed}\n\n{bound_nl}"

        original_text = out.original if isinstance(out.original, str) else str(out.original)
        if len(result) > len(original_text):
            out.metadata["description"] = "CL Tokens greater than NL token. Keeping NL input"
            return original_text.format(**runtime_values)
        return result

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
