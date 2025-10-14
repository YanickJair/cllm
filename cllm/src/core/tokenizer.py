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
        output_format: Optional[OutputFormat]
    ) -> str:
        """
        Build compressed token sequence
        
        Order: [REQ] [TARGET] [EXTRACT] [CTX] [OUT]
        """
        tokens: list[str] = []

        # REQ tokens
        for intent in intents:
            if intent.modifier:
                tokens.append(f"[REQ:{intent.token}:{intent.modifier}]")
            else:
                tokens.append(f"[REQ:{intent.token}]")

        # TARGET tokens
        for target in targets:
            token_str = f"[TARGET:{target.token}"
            if target.domain:
                token_str += f":DOMAIN={target.domain}"
            for attr_key, attr_val in target.attributes.items():
                token_str += f":{attr_key}={attr_val}"
            token_str += "]"
            tokens.append(token_str)

        # EXTRACT tokens
        if extractions and extractions.fields:
            fields_str = "+".join(extractions.fields)
            tokens.append(f"[EXTRACT:{fields_str}]")

        # CTX tokens
        for context in contexts:
            tokens.append(f"[CTX:{context.aspect}={context.value}]")
        
        # OUT tokens
        if output_format:
            token_str = f"[OUT:{output_format.format_type}"
            if output_format.attributes:
                for attr_key, attr_val in output_format.attributes.items():
                    token_str += f":{attr_key}={attr_val}"
            token_str += "]"
            tokens.append(token_str)
        
        return " ".join(tokens)