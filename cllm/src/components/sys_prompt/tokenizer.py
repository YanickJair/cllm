from typing import Optional
from ._schemas import Intent, Target, ExtractionField, Context, OutputFormat, OutputSchema


class CLLMTokenizer:
    """Builds final compressed token sequence"""

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
        """Build compressed CLLM sequence"""
        tokens = []

        # Add REQ tokens
        for intent in intents:
            if intent.token == "EXTRACT" and extractions and extractions.fields:
                continue

            # Build REQ token with modifiers
            if intent.modifier:
                req_str = f"[REQ:{intent.token}:{intent.modifier}]"
            else:
                req_str = f"[REQ:{intent.token}]"
            tokens.append(req_str)

        # Add TARGET tokens
        for target in targets:
            target_str = f"[TARGET:{target.token}"
            if target.attributes:
                for key, value in sorted(target.attributes.items()):
                    target_str += f":{key}={value}"
            target_str += "]"
            tokens.append(target_str)

        # Add EXTRACT fields
        if extractions and extractions.fields:
            extract_str = "[EXTRACT:" + "+".join(extractions.fields) + "]"
            tokens.append(extract_str)

        # Add CTX tokens
        for ctx in contexts:
            if not any(ctx.value == intent.modifier for intent in intents):
                tokens.append(f"[CTX:{ctx.aspect}={ctx.value}]")

        # Add OUT token
        if output_format:
            tokens.append(output_format.build_token())

        return " ".join(tokens)
