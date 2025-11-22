from typing import Optional

from src.components.sys_prompt.analyzers.target import TargetValidator

from ._schemas import Intent, Target, ExtractionField, Context, OutputSchema


class CLLMTokenizer:
    """Builds final compressed CLLM token sequence"""

    @staticmethod
    def build_sequence(
            intents: list[Intent],
            targets: list[Target],
            extractions: Optional[ExtractionField],
            contexts: list[Context],
            output_format: Optional[OutputSchema],
            quantifier: Optional[tuple[str, int]] = None,
            specifications=None,
    ) -> str:

        tokens = []

        for intent in intents:
            if intent.token == "EXTRACT" and extractions and extractions.fields:
                continue

            if intent.modifier:
                tokens.append(f"[REQ:{intent.token}:{intent.modifier}]")
            else:
                tokens.append(f"[REQ:{intent.token}]")

        validator = TargetValidator()
        clean_targets = validator.deduplicate(targets)
        target_tokens = validator.serialize_targets(clean_targets)
        tokens.extend(target_tokens)

        if extractions and extractions.fields:
            tokens.append(extractions.build_token())

        for ctx in contexts:
            # Avoid printing CTX modifier that was already consumed by REQ modifier
            if not any(ctx.value == intent.modifier for intent in intents):
                tokens.append(f"[CTX:{ctx.aspect}={ctx.value}]")

        if output_format:
            tokens.append(output_format.build_token())

        return " ".join(tokens)
