from typing import Optional, Annotated

from annotated_doc import Doc

from ._schemas import Intent, Target, ExtractionField, Context, OutputSchema


class CLLMTokenizer:
    """Builds final compressed CLLM token sequence"""

    @staticmethod
    def build_sequence(
        intent: Annotated[
            Intent,
            Doc("The detected intent (REQ token) to encode first in the sequence."),
        ],
        target: Annotated[
            Target,
            Doc("The extracted target (TARGET token) to encode after the intent."),
        ],
        extractions: Annotated[
            Optional[ExtractionField],
            Doc(
                "Optional extraction fields (EXTRACT token); omitted if None or empty."
            ),
        ],
        contexts: Annotated[
            list[Context],
            Doc("List of context aspects (CTX tokens) to append after extractions."),
        ],
        output_format: Annotated[
            Optional[OutputSchema],
            Doc("Optional output schema (OUT token) to append at the end."),
        ],
        quantifier: Annotated[
            Optional[tuple[str, int]],
            Doc(
                "Optional (token_label, numeric_value) quantifier; not yet emitted but reserved for future use."
            ),
        ] = None,
        specifications: Annotated[
            Optional[dict],
            Doc(
                "Optional specification dict; not yet emitted but reserved for future use."
            ),
        ] = None,
    ) -> str:
        tokens = []

        exclude_extract_token = False
        """
        for intent in intents:
            if intent.token == "EXTRACT" and extractions and extractions.fields:
                exclude_extract_token = True
                extract_req = f"[REQ:{intent.token}:{','.join(extractions.fields)}"
                if extractions.attributes:
                    attr_parts = [f"{k}={v}" for k, v in extractions.attributes.items()]
                    extract_req += f":{','.join(attr_parts)}"
                extract_req += "]"
                tokens.append(extract_req)
                break

            if intent.modifier:
                tokens.append(f"[REQ:{intent.token}:{intent.modifier}]")
            else:
                tokens.append(f"[REQ:{intent.token}]")
        """
        tokens.append(intent.build_token())
        tokens.append(target.build_token())

        if extractions and extractions.fields and not exclude_extract_token:
            if extractions:
                tokens.append(extractions.build_token())

        for ctx in contexts:
            tokens.append(f"[CTX:{ctx.aspect}={ctx.value}]")

        if output_format:
            tokens.append(output_format.build_token())

        return " ".join(tokens)
