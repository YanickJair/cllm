# CLLM tokenizer
from typing import Optional
from src.core import Intent, Target, ExtractionField, Context, OutputFormat


class CLLMTokenizer:
    """Builds final compressed token sequence"""
    @staticmethod
    def build_sequence(
        intents: list[Intent],
        targets: list[Target],
        extractions: Optional[ExtractionField],
        contexts: list[Context],
        output_format: Optional[OutputFormat],
        quantifier=None,
        specifications=None
    ):
        """
        Build CLLM token sequence (V2.0 with quantifiers and specs)

        NEW Format:
        [REQ] [QUANTIFIER] [TARGET:SUBJECT=X:TOPIC=Y] [SPEC:COUNT=3] [EXTRACT] [CTX] [OUT]
        """
        tokens = []

        # 1. REQ tokens
        for intent in intents:
            if intent.modifier:
                tokens.append(f"[REQ:{intent.token}:{intent.modifier}]")
            else:
                tokens.append(f"[REQ:{intent.token}]")

        # 2. QUANTIFIER tokens (NEW!)
        if quantifier:
            tokens.append(f"[QUANTIFIER:{quantifier[0]}]")

        # 3. TARGET tokens (with enhanced attributes)
        for target in targets:
            target_str = f"[TARGET:{target.token}"

            # Add attributes
            if target.attributes:
                for key, value in target.attributes.items():
                    target_str += f":{key}={value}"

            target_str += "]"
            tokens.append(target_str)

        # 4. SPEC tokens (NEW!)
        if specifications:
            spec_parts = [f"{k}={v}" for k, v in specifications.items()]
            tokens.append(f"[SPEC:{'+'.join(spec_parts)}]")

        # 5. EXTRACT tokens (existing)
        if extractions and extractions.fields:
            extract_str = "[EXTRACT:" + "+".join(extractions.fields) + "]"
            tokens.append(extract_str)

        # 6. CTX tokens (existing, but now with AUDIENCE!)
        for ctx in contexts:
            tokens.append(f"[CTX:{ctx.aspect}={ctx.value}]")

        # 7. OUT tokens (existing)
        if output_format:
            tokens.append(f"[OUT:{output_format.format_type}]")

        return " ".join(tokens)