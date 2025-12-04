from typing import Optional


from ._schemas import Intent, Target, ExtractionField, Context, OutputSchema


class CLLMTokenizer:
    """Builds final compressed CLLM token sequence"""

    @staticmethod
    def build_sequence(
        intents: list[Intent],
        target: Target,
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

        tokens.append(target.build_token())

        if extractions and extractions.fields:
            tokens.append(extractions.build_token())

        for ctx in contexts:
            if not any(ctx.value == intent.modifier for intent in intents):
                tokens.append(f"[CTX:{ctx.aspect}={ctx.value}]")

        if output_format:
            tokens.append(output_format.build_token())

        return " ".join(tokens)
