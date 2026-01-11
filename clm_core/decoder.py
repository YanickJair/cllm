import re
from typing import Dict, List


class CLLMDecoder:
    def __init__(self):
        self.req_to_action = {
            "ANALYZE": "Analyze",
            "EXTRACT": "Extract",
            "GENERATE": "Generate",
            "SUMMARIZE": "Summarize",
            "TRANSFORM": "Convert",
            "EXPLAIN": "Explain",
            "COMPARE": "Compare",
            "CLASSIFY": "Classify",
            "DEBUG": "Debug",
            "OPTIMIZE": "Improve",
            "VALIDATE": "Validate",
            "SEARCH": "Search for",
            "RANK": "Rank",
            "PREDICT": "Predict",
            "FORMAT": "Format",
            "DETECT": "Detect",
            "CALCULATE": "Calculate",
            "AGGREGATE": "Aggregate",
            "DETERMINE": "Determine",
            "ROUTE": "Route",
            "EXECUTE": "Use",
            "LIST": "List",
            "QUERY": "What",
        }

        self.target_to_noun = {
            "CODE": "the code",
            "DATA": "the data",
            "DOCUMENT": "the document",
            "TRANSCRIPT": "the transcript",
            "EMAIL": "the email",
            "TICKET": "the ticket",
            "REPORT": "the report",
            "CONCEPT": "the concept",
            "PROCEDURE": "the procedure",
            "ANSWER": "an answer",
            "ITEMS": "items",
            "CONTENT": "the content",
            "RESULT": "the result",
            "FEEDBACK": "feedback",
            "RESPONSE": "a response",
            "DESCRIPTION": "a description",
            "SUMMARY": "a summary",
            "PLAN": "a plan",
            "POST": "a post",
            "SYSTEM": "a system",
            "STRATEGY": "a strategy",
            "COMPLAINT": "a complaint",
            "METRICS": "the metrics",
            "ENDPOINT": "the API",
            "COMPONENT": "the component",
            "CONVERSATION": "the conversation",
            "RECORD": "the record",
            "PATTERN": "the pattern",
            "FEATURES": "the features",
            "LOGS": "the logs",
        }

        self.ctx_modifiers = {
            "TONE": {
                "PROFESSIONAL": "in a professional tone",
                "TECHNICAL": "in a technical tone",
                "CASUAL": "casually",
                "EMPATHETIC": "empathetically",
            },
            "STYLE": {
                "SIMPLE": "in simple terms",
                "DETAILED": "in detail",
                "CONCISE": "concisely",
            },
            "LENGTH": {
                "BRIEF": "briefly",
                "SHORT": "in short",
                "DETAILED": "in detail",
            },
        }

        self.out_formats = {
            "JSON": "in JSON format",
            "LIST": "as a list",
            "TABLE": "in a table",
            "MARKDOWN": "in markdown",
            "CSV": "as CSV",
        }

    def parse_token(self, token_str: str) -> Dict:
        """Parse CLLM token: [TYPE:VALUE:ATTR1=VAL1:ATTR2]"""
        parts = token_str.split(":")

        result = {
            "type": parts[0],
            "value": parts[1] if len(parts) > 1 else None,
            "attributes": {},
        }

        # Parse attributes (KEY=VALUE or standalone)
        for part in parts[2:]:
            if "=" in part:
                key, val = part.split("=", 1)
                result["attributes"][key] = val
            else:
                result["attributes"][part] = True

        return result

    def humanize_topic(self, topic: str) -> str:
        """
        Convert TOPIC to natural language
        THREE_PRIMARY_COLORS -> the three primary colors
        CAPITAL_OF_FRANCE -> the capital of France
        """
        # Replace underscores
        text = topic.replace("_", " ")

        # Lowercase
        text = text.lower()

        # Handle possessives
        text = text.replace("'s", "'s")

        # Add article if needed
        if not text.startswith(("the ", "a ", "an ")):
            # Add 'the' for most cases
            if not any(
                text.startswith(w)
                for w in ["what", "who", "where", "when", "why", "how"]
            ):
                text = "the " + text

        return text

    def format_question(self, topic: str, topic_type: str = None) -> str:
        """
        Format as a question
        topic='three primary colors' -> 'What are the three primary colors'
        topic='capital of france' -> 'What is the capital of France'
        """
        # Detect plural vs singular
        words = topic.split()
        is_plural = words and (
            words[0] in ["many", "few", "several", "some"]
            or (
                len(words) > 1
                and words[-1].endswith("s")
                and not words[-1].endswith("ss")
            )
        )

        # Choose "is" or "are"
        verb = "are" if is_plural else "is"

        # Format with proper article
        if topic.startswith(("the ", "a ", "an ")):
            return f"What {verb} {topic}"
        else:
            return f"What {verb} the {topic}"

    def combine_req_tokens(self, req_tokens: List[Dict]) -> str:
        """Intelligently combine multiple REQ tokens"""
        if not req_tokens:
            return ""

        if len(req_tokens) == 1:
            return self.req_to_action.get(
                req_tokens[0]["value"], req_tokens[0]["value"].lower()
            )

        reqs = [t["value"] for t in req_tokens]

        patterns = {
            ("GENERATE", "EXTRACT"): "Identify",
            ("TRANSFORM", "EXECUTE"): "Rewrite",
            ("TRANSFORM", "OPTIMIZE"): "Edit",
            ("GENERATE", "EXPLAIN"): "Generate",
            ("GENERATE", "OPTIMIZE"): "Generate",
            ("REQ:EXECUTE", "CALCULATE"): "Calculate",
            ("CLASSIFY", "GENERATE"): "Arrange",
            ("CLASSIFY", "EXECUTE"): "Classify",
            ("CLASSIFY", "OPTIMIZE"): "Classify",
            ("ANALYZE", "TRANSFORM"): "Analyze",
            ("GENERATE", "DEBUG"): "Construct",
            ("SUMMARIZE", "EXTRACT"): "Summarize",
        }

        req_tuple = tuple(reqs[:2])
        if req_tuple in patterns:
            return patterns[req_tuple]

        return self.req_to_action.get(reqs[0], reqs[0].lower())

    def decode(self, compressed: str) -> str:
        """
        Main decode function - converts CLLM tokens to natural language

        Args:
            compressed: Token string like "[REQ:GENERATE] [TARGET:ANSWER]"

        Returns:
            Natural language string
        """
        if not compressed or not compressed.strip():
            return ""

        token_strs = re.findall(r"\[([^\]]+)\]", compressed)
        if not token_strs:
            return compressed

        tokens = [self.parse_token(t) for t in token_strs]
        req_tokens = [t for t in tokens if t["type"] == "REQ"]
        target_tokens = [t for t in tokens if t["type"] == "TARGET"]
        extract_tokens = [t for t in tokens if t["type"] == "EXTRACT"]
        ctx_tokens = [t for t in tokens if t["type"] == "CTX"]
        out_tokens = [t for t in tokens if t["type"] == "OUT"]

        if not req_tokens and target_tokens:
            target = target_tokens[0]
            if "TYPE" in target["attributes"]:
                type_text = self.humanize_topic(target["attributes"]["TYPE"])
                return type_text.capitalize() + "."

            noun = self.target_to_noun.get(target["value"], target["value"].lower())
            return noun.capitalize() + "."

        if not req_tokens:
            return compressed

        action = self.combine_req_tokens(req_tokens)
        is_question = req_tokens[0]["value"] == "QUERY"

        if not target_tokens:
            return action + "."

        target = target_tokens[0]
        target_val = target["value"]

        if "TOPIC" in target["attributes"]:
            topic = target["attributes"]["TOPIC"]
            topic_text = self.humanize_topic(topic)

            if is_question:
                question = self.format_question(
                    topic_text, target["attributes"].get("TYPE")
                )
                return question + "?"
            else:
                sentence = f"{action} {topic_text}"

        elif "TYPE" in target["attributes"]:
            type_val = target["attributes"]["TYPE"]
            type_text = self.humanize_topic(type_val)

            if is_question:
                question = self.format_question(type_text)
                return question + "?"
            else:
                sentence = f"{action} {type_text}"

        elif "DOMAIN" in target["attributes"]:
            domain = target["attributes"]["DOMAIN"].lower()
            noun = self.target_to_noun.get(target_val, target_val.lower())
            noun = noun.replace("the ", "")
            sentence = f"{action} the {domain} {noun}"

        else:
            noun = self.target_to_noun.get(target_val, target_val.lower())

            if is_question:
                question = self.format_question(
                    noun.replace("the ", "").replace("a ", "").replace("an ", "")
                )
                return question + "?"
            else:
                sentence = f"{action} {noun}"

        if extract_tokens:
            fields = extract_tokens[0]["value"].split("+")
            field_text = ", ".join(f.replace("_", " ").lower() for f in fields)
            if len(fields) > 1:
                parts = field_text.rsplit(", ", 1)
                field_text = " and ".join(parts)
            sentence += f" and extract the {field_text}"

        for ctx in ctx_tokens:
            val = ctx["value"]
            if "=" in val:
                key, value = val.split("=", 1)
                if key in self.ctx_modifiers and value in self.ctx_modifiers[key]:
                    sentence += " " + self.ctx_modifiers[key][value]

        if out_tokens:
            fmt = out_tokens[0]["value"]
            if fmt in self.out_formats:
                sentence += " " + self.out_formats[fmt]

        if sentence and not sentence[0].isupper():
            sentence = sentence[0].upper() + sentence[1:]

        if not sentence.endswith((".", "?", "!")):
            sentence += "."

        return sentence

    def batch_decode(self, compressed_list: List[str]) -> List[str]:
        """Decode multiple prompts"""
        return [self.decode(c) for c in compressed_list]
