from __future__ import annotations
import json
import re
from typing import Any, Union, Optional

from clm_core.components.sys_prompt._schemas import (
    OutputField,
    OutputSchema,
    SysPromptConfig,
)

BULLET_PATTERNS = [
    r"^\s*[-*]\s+",  # - item
    r"^\s*•\s+",  # • item
    r"^\s*\d+\.\s+",  # 1. item
    r"^\s*\(\w\)\s+",  # (a) item
]
FORMAT_HINTS = {
    "json": ["json", "json format", "json structure", "{", '"'],
    "list": [
        "list of dictionaries",
        "list of dicts",
        "list of objects",
        "list where each",
        "each item",
    ],
    "dict": ["dictionary", "dict", "object"],
    "yaml": ["yaml", "yml"],
}
NON_ENUM_KEYWORDS = {
    "output",
    "format",
    "instruction",
    "instructions",
    "requirement",
    "requirements",
    "responsibilities",
    "responsibility",
    "document",
    "documentation",
    "ensure",
    "provide",
}

ENUM_HINT_KEYWORDS = {
    "steps",
    "types",
    "values",
    "options",
    "levels",
    "statuses",
    "categories",
}
FIELD_LINE_PATTERNS = [
    # "key": description
    re.compile(
        r'["\'](?P<key>[\w\-\_ ]{1,80})["\']\s*[:\-–—]\s*(?P<desc>.+)', re.IGNORECASE
    ),
    # key -> description OR key -> description (unicode arrow normalized earlier)
    re.compile(r"(?P<key>[\w\-\_ ]{1,80})\s*->\s*(?P<desc>.+)", re.IGNORECASE),
    # key — description or - key - description (bulleted)
    re.compile(
        r"^\s*-\s*(?P<key>[\w\-\_ ]{1,80})\s*[-:–—]\s*(?P<desc>.+)", re.IGNORECASE
    ),
    # key: description (bare)
    re.compile(r"(?P<key>[\w\-\_ ]{1,80})\s*:\s*(?P<desc>.+)", re.IGNORECASE),
    # key (short description)
    re.compile(r"(?P<key>[\w\-\_ ]{1,80})\s*\((?P<desc>[^\)]+)\)", re.IGNORECASE),
]


def normalize_text(text: str) -> str:
    """
    Normalize incoming specification:
    - Convert common Unicode arrows to ASCII
    - Normalize bullets to one-per-line
    - Trim extra whitespace and unify newlines
    - Convert “–”/“—” to hyphen
    """
    if not text:
        return ""

    text = text.replace("→", "->").replace("→", "->")
    text = text.replace("–", "-").replace("—", "-")
    text = text.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Ensure bullets on their own lines (convert "• key — desc" style by splitting)
    for pat in BULLET_PATTERNS:
        text = re.sub(r"\n\s*" + pat, "\n- ", text)
        text = re.sub(r"^" + pat, "- ", text, flags=re.MULTILINE)

    # Make sure each bullet begins on new line
    text = re.sub(r"\s*\n\s*-\s*", "\n- ", text.strip())

    # Collapse multiple blank lines somewhat
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def contains_json_block(text: str) -> bool:
    """Look for an explicit JSON block inside the text and verify parseable"""
    # first look for codeblock-style or brace occurrences
    json_like = re.search(
        r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text, flags=re.IGNORECASE
    )
    if json_like:
        content = json_like.group(1)
    else:
        # fallback: look for first { ... } that is reasonably sized
        brace_match = re.search(r"(\{[\s\S]{10,2000}\})", text)
        content = brace_match.group(1) if brace_match else None

    if content:
        try:
            json.loads(content)
            return True
        except Exception:
            return False
    return False


def detect_format_from_text(text: str) -> str:
    tl = text.lower()
    # explicit JSON snippet
    if contains_json_block(text):
        return "JSON"
    # strong phrase matches
    for key, phrases in FORMAT_HINTS.items():
        for p in phrases:
            if p in tl:
                if key == "list":
                    return "LIST"
                if key == "json":
                    return "JSON"
                if key == "dict":
                    return "JSON"
                if key == "yaml":
                    return "YAML"
    # fallback: if text contains "keys:" or "fields:" then structured list-like
    if re.search(r"\bkeys?\b|\bfields?\b|\bcontains\b|\bshould include\b", tl):
        return "LIST"
    return "STRUCTURED"


def split_into_candidate_lines(text: str) -> list[str]:
    """
    Break normalized text into useful candidate lines/phrases to parse.
    Also attempt to expand enumerations like 'The fields are: a, b, c' into separate lines.
    """
    lines = []
    for raw in text.split("\n"):
        s = raw.strip()
        if not s:
            continue
        # if a line contains comma-separated field list after "fields are" -> expand
        m = re.search(r"(fields?|keys?)\s*(are|:)\s*(.+)", s, flags=re.IGNORECASE)
        if m:
            remainder = m.group(3)
            # split on commas but ignore commas inside quotes
            parts = re.split(r',\s*(?=(?:[^"]*"[^"]*")*[^"]*$)', remainder)
            for p in parts:
                p = p.strip()
                if p:
                    lines.append(p)
            continue
        # otherwise keep the line
        lines.append(s)
    return lines


def parse_fields_from_lines(lines: list[str]) -> list[OutputField]:
    """
    Apply micro-grammar patterns and heuristics to extract fields.
    Return list of OutputField (flat). Nested detection happens later.
    """
    extracted: dict[str, OutputField] = {}

    for line in lines:
        matched = False
        # try each grammar pattern
        for pat in FIELD_LINE_PATTERNS:
            m = pat.search(line)
            if m:
                key = m.group("key").strip().strip('"').strip("'")
                desc = m.groupdict().get("desc")
                if desc:
                    desc = desc.strip().strip('"').strip("'").rstrip(".;")
                # Normalize key to snake-like
                normalized_key = re.sub(r"\s+", "_", key.strip()).lower()
                if normalized_key not in extracted:
                    extracted[normalized_key] = OutputField(
                        name=normalized_key, type=None, description=desc or None
                    )
                matched = True
                break

        if not matched:
            # fallback: if the line itself is a single word/phrase probably meaning a key
            single = re.match(r'^\-?\s*["\']?(?P<w>[\w\-\_ ]{1,60})["\']?\s*$', line)
            if single:
                key = single.group("w").strip()
                normalized_key = re.sub(r"\s+", "_", key).lower()
                if normalized_key not in extracted:
                    extracted[normalized_key] = OutputField(name=normalized_key)
                continue

            # fallback: try splitting "name - description" with any hyphen
            m2 = re.match(r"(?P<key>[\w\-\_ ]{1,80})\s*[-–—]\s*(?P<desc>.+)", line)
            if m2:
                key = m2.group("key").strip()
                desc = m2.group("desc").strip().rstrip(".;")
                normalized_key = re.sub(r"\s+", "_", key).lower()
                if normalized_key not in extracted:
                    extracted[normalized_key] = OutputField(
                        name=normalized_key, description=desc
                    )
                continue

    return list(extracted.values())


def extract_fields_from_dict(
    schema: dict[str, Any], prefix: str = ""
) -> list[OutputField]:
    """
    Recursively extract fields from a dict (structured schema).
    """
    fields: list[OutputField] = []
    for key, val in schema.items():
        if isinstance(val, dict):
            nested = extract_fields_from_dict(val, prefix=f"{prefix}{key}.")
            fields.append(OutputField(name=key, type="object", nested=nested))
        elif isinstance(val, list):
            # if first element is dict, treat as array of objects
            if len(val) > 0 and isinstance(val[0], dict):
                nested = extract_fields_from_dict(val[0], prefix=f"{prefix}{key}.")
                fields.append(
                    OutputField(name=key, type="array<object>", nested=nested)
                )
            else:
                fields.append(OutputField(name=key, type="array", description=str(val)))
        else:
            fields.append(
                OutputField(name=key, type=type(val).__name__, description=str(val))
            )
    return fields


def detect_nested_from_text(text: str, fields: list[OutputField]) -> bool:
    """
    Decide whether schema is nested based on:
    - presence of JSON/dict structures
    - explicit occurrences of 'nested', 'hierarchical', 'each item contains', etc.
    - indentation-based bullets with colon followed by newline
    - presence of nested fields in structured extraction
    """
    tl = text.lower()
    if (
        "nested" in tl
        or "hierarch" in tl
        or "each item contains" in tl
        or "each object contains" in tl
    ):
        return True

    lines = text.split("\n")
    for i, line in enumerate(lines[:-1]):
        if re.match(r"^\s*[-*]?\s*[\w\-\_ ]+:\s*$", line):
            if re.match(r"^\s{2,}[-*]?\s*[\w\-\_ ]+", lines[i + 1]):
                return True

    if any(f.nested for f in fields):
        return True

    return False


class SchemaOutputCompressor:
    """
    Token-efficient, signature-preserving schema compressor.
    Produces:
    OutputSchema(format_type="JSON", attributes={"SCHEMA": "{...}", "SCORE_MAP": "{...}"})
    """

    def __init__(
        self, *, infer_types: bool, add_attributes: bool, add_examples: bool
    ) -> None:
        self._add_attributes: bool = add_attributes
        self._infer_types: bool = infer_types
        self._add_specs_attr = add_examples

    SCORE_PATTERN = re.compile(
        r"(\d+\.\d+)\s*[-–]\s*(\d+\.\d+)\s*:\s*([A-Za-z ]+)",
        flags=re.IGNORECASE,
    )

    def compress_schema(self, schema: dict, extra_text: str = "") -> OutputSchema:
        schema_encoded = self._encode_schema(schema)
        attributes = {"schema": schema_encoded}

        if self._add_attributes:
            enums_and_constraints = self._extract_enums(extra_text)
            if enums := enums_and_constraints.get("enums"):
                attributes["ENUMS"] = json.dumps(enums)
                specs_attr = self._extract_specs(extra_text)
                if specs_attr is not None:
                    attributes["SPECS"] = specs_attr
            if constraints := enums_and_constraints.get("constraints"):
                attributes["CONSTRAINTS"] = json.dumps(constraints)

        fields = self._extract_fields(schema)
        return OutputSchema(
            format_type="JSON", fields=fields, attributes=attributes, raw_schema=schema
        )

    def _encode_schema(self, obj) -> str:
        """
        Encode schema compactly.
        - When self._infer_types is False: omit primitive type labels BUT preserve nested object structure.
          e.g. {summary,qa_scores:{verification,policy_adherence},violations,recommendations}
        - When self._infer_types is True: emit types as before.
          e.g. {summary:STR,qa_scores:{verification:FLOAT,...},violations:[STR],...}
        """

        if isinstance(obj, dict):
            parts = []
            for k, v in obj.items():
                if isinstance(v, dict):
                    inner = self._encode_schema(v)
                    parts.append(f"{k}:{inner}")
                elif isinstance(v, list):
                    if not v:
                        parts.append(f"{k}:[]")
                    else:
                        first = v[0]
                        if isinstance(first, dict):
                            inner = self._encode_schema(first)
                            parts.append(f"{k}:[{inner}]")
                        else:
                            if self._infer_types:
                                t = self._infer_type(first)
                                parts.append(f"{k}:[{t}]")
                            else:
                                parts.append(f"{k}")
                else:
                    if self._infer_types:
                        parts.append(f"{k}:{self._infer_type(v)}")
                    else:
                        parts.append(f"{k}")
            return "{" + ",".join(parts) + "}"

        elif isinstance(obj, list):
            if not obj:
                return "[]"
            first = obj[0]
            if isinstance(first, dict):
                return "[" + self._encode_schema(first) + "]"
            else:
                if self._infer_types:
                    return f"[{self._infer_type(first)}]"
                return "[]"

        else:
            if self._infer_types:
                return self._infer_type(obj)
            return ""

    def _extract_enums(self, text: str) -> dict:
        """
        Extract:
          - ENUMS: selectable categorical values
          - CONSTRAINTS: imperative output / behavior requirements
        """
        if not text:
            return {}

        enums = {}
        constraints = {}

        range_matches = re.findall(
            r"(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)\s*(?:means|is|=|:)\s*([A-Za-z_ ]+)",
            text,
            flags=re.IGNORECASE,
        )

        if range_matches:
            enums["ranges"] = [
                {
                    "min": float(lo),
                    "max": float(hi),
                    "label": label.strip().upper().replace(" ", "_"),
                }
                for lo, hi, label in range_matches
            ]

        inline_enum_matches = re.findall(
            r"([\w\.]+)\s*\(([^)]+\|[^)]+)\)",
            text,
            flags=re.IGNORECASE,
        )

        for field, body in inline_enum_matches:
            values = [v.strip().upper() for v in body.split("|") if v.strip()]
            if len(values) >= 2:
                enums[field.lower()] = {
                    "kind": "categorical",
                    "values": values,
                }

        block_pattern = re.compile(
            r"([^\n:]{1,80}):\s*\n((?:\s*[-*]\s*[^\n]+\n?)+)",
            flags=re.IGNORECASE,
        )

        for header, block in block_pattern.findall(text):
            header_clean = re.sub(r"\s+", " ", header.strip().lower())

            items = [
                line.strip().lstrip("-* ")
                for line in block.splitlines()
                if line.strip()
            ]

            if len(items) < 2:
                continue

            if self._is_imperative_header(header_clean):
                constraints[header_clean.replace(" ", "_")] = {
                    "kind": "required",
                    "items": items,
                }
                continue

            if self._is_enum_candidate(header_clean):
                enums[header_clean.replace(" ", "_")] = {
                    "kind": "categorical",
                    "values": [i.upper() for i in items],
                }

        if not enums and not constraints:
            return {}

        return {
            "enums": enums or None,
            "constraints": constraints or None,
        }

    @staticmethod
    def _is_imperative_header(header: str) -> bool:
        header = header.lower().strip()

        if any(word in header for word in ("should", "must", "required")):
            return True

        if any(header.startswith(k) for k in NON_ENUM_KEYWORDS):
            return True

        return False

    @staticmethod
    def _is_enum_candidate(header: str) -> bool:
        header = header.lower()
        return any(k in header for k in ENUM_HINT_KEYWORDS)

    def _extract_specs(self, text: str) -> Optional[dict]:
        """
        Generic SPECS extractor.
        - Detects explicit SPECS={...} blocks and parses leniently.
        - Falls back to NL heuristics to infer range maps, types, and field lists.
        """
        if not text:
            return None

        m = re.search(r"specs\s*[:=]\s*\{([\s\S]+?)\}", text, flags=re.IGNORECASE)
        if m:
            raw = m.group(1).strip()
            parsed = self._parse_specs_block(raw)
            return parsed if parsed else None

        nl_parsed = self._extract_specs_from_nl(text)
        return nl_parsed if nl_parsed else None

    def _parse_specs_block(self, body: str) -> dict:
        """
        Parse the inside of SPECS={...} into a Python dict using lenient pseudo-JSON parsing.
        Supports nested {...}, arrays [...], key:value and key=value styles.
        """
        specs = {}
        parts = re.split(r",\s*(?=(?:[^{}]*\{[^}]*\})*[^}]*$)", body)

        for p in parts:
            if not p.strip():
                continue
            if ":" in p:
                key, val = p.split(":", 1)
            elif "=" in p:
                key, val = p.split("=", 1)
            else:
                k = p.strip()
                specs[k] = True
                continue

            key = key.strip().strip('"').strip("'")
            val = val.strip()
            parsed = self._try_parse_json_fragment(val)
            specs[key] = parsed if parsed is not None else self._clean_value_string(val)

        return specs

    def _try_parse_json_fragment(self, val: str):
        """
        Tries to parse pseudo-JSON fragments:
            {a:b,c:d}
            [x,y,z]
            {"key":"value"}
        Returns Python object or None.
        """
        v = val.strip()
        try:
            return json.loads(v)
        except Exception:
            pass

        heur = v
        heur = re.sub(
            r"([\{\[,]\s*)([A-Za-z0-9_]+\s*):",
            lambda m: m.group(1) + '"' + m.group(2).strip().rstrip(":") + '":',
            heur,
        )
        heur = re.sub(r":\s*([A-Za-z_][A-Za-z0-9_\-]*)", r':"\1"', heur)

        try:
            return json.loads(heur)
        except Exception:
            pass

        if heur.startswith("[") and heur.endswith("]"):
            inner = heur[1:-1].strip()
            parts = [
                x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()
            ]
            return parts

        return None

    def _clean_value_string(self, s: str) -> str:
        # strip surrounding braces/brackets/quotes
        s = s.strip()
        if s.startswith("{") and s.endswith("}"):
            s = s[1:-1].strip()
        if s.startswith("[") and s.endswith("]"):
            s = s[1:-1].strip()
        return s.strip().strip('"').strip("'")

    def _extract_specs_from_nl(self, text: str) -> Optional[dict]:
        """
        Extract rule-like structures from natural language instructions.
        Uses regex heuristics and (optionally) spaCy if available as self.nlp.
        """
        inferred = {}
        type_rule = re.findall(
            r"([\w\.]+)\s+(?:is|are)\s+(?:a|an)?\s*(float|int|boolean|bool|string|str|array|list|object)",
            text,
            flags=re.IGNORECASE,
        )
        if type_rule:
            types = {field: t.upper() for field, t in type_rule}
            inferred.setdefault("types", {}).update(types)

        contains = re.search(
            r"(contain|contains|include|includes|have the following keys)\s*[:\-]\s*(.+)",
            text,
            flags=re.IGNORECASE,
        )
        if contains:
            fields = [
                f.strip().strip(".,")
                for f in re.split(r",\s*|\n", contains.group(2))
                if f.strip()
            ]
            inferred["fields"] = fields

        reqs = re.findall(
            r"([\w\.]+)\s+(required|required:|optional|optional:|must be present|must be absent)",
            text,
            flags=re.IGNORECASE,
        )
        if reqs:
            requirements = {}
            for f, rule in reqs:
                rule_clean = rule.lower().replace(":", "").strip()
                if "optional" in rule_clean:
                    requirements[f] = "OPTIONAL"
                else:
                    requirements[f] = "REQUIRED"
            inferred.setdefault("requirements", {}).update(requirements)

        try:
            if hasattr(self, "nlp") and self.nlp is not None:
                doc = self.nlp(text)
                ents = [ent.text for ent in doc.ents if ent.text]
                if ents:
                    inferred["entities"] = ents
        except Exception:
            pass

        return inferred if inferred else None

    def _extract_fields(self, schema: dict) -> list[OutputField]:
        fields = []
        if isinstance(schema, str):
            return fields
        for k, v in schema.items():
            if isinstance(v, dict):
                nested = self._extract_fields(v)
                fields.append(OutputField(name=k, type="object", nested=nested))
            elif isinstance(v, list):
                fields.append(OutputField(name=k, type="array", description=str(v)))
            else:
                fields.append(
                    OutputField(
                        name=k, type=self._infer_type(v) if self._infer_types else None
                    )
                )
        return fields

    def _infer_type(self, v) -> str:
        if isinstance(v, float):
            return "FLOAT"
        if isinstance(v, int):
            return "INT"
        if isinstance(v, bool):
            return "BOOL"
        if isinstance(v, str):
            return "STR"
        return "ANY"


class SysPromptOutputFormat:
    def __init__(self, config: SysPromptConfig):
        self.struct_compressor = SchemaOutputCompressor(
            infer_types=config.infer_types,
            add_attributes=config.add_attrs,
            add_examples=config.add_examples,
        )

    def compress(self, output_spec, is_structured=None):
        if is_structured is None:
            is_structured = isinstance(output_spec, dict)

        if is_structured:
            return self.struct_compressor.compress_schema(
                output_spec, extra_text=str(output_spec)
            )

        schema_obj = self._process_nl_schema(output_spec)
        return self.struct_compressor.compress_schema(
            schema_obj.raw_schema or {}, extra_text=output_spec
        )

    def compress_with_schema(
        self, output_spec: Union[str, dict], return_schema: bool = False
    ):
        is_structured = isinstance(output_spec, dict)
        if is_structured:
            schema = self.struct_compressor.compress_schema(output_spec)
        else:
            schema = self._process_nl_schema(str(output_spec))

        token = schema.build_token()
        if return_schema:
            return token, schema
        return token

    def _process_nl_schema(self, text: str) -> OutputSchema:
        norm = normalize_text(text)

        if contains_json_block(norm):
            m = re.search(
                r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", norm, flags=re.IGNORECASE
            )
            json_str = (
                m.group(1) if m else re.search(r"(\{[\s\S]{10,2000}\})", norm).group(1)
            )  # type: ignore
            try:
                parsed = json.loads(json_str)
                return self.struct_compressor.compress_schema(parsed)
            except Exception:
                pass

        format_hint = detect_format_from_text(norm)
        lines = split_into_candidate_lines(norm)

        phrase_field_matches = []
        phrase_match = re.search(
            r"(contain|contains|include|includes|have the following keys|fields are)\s*[:\-]?\s*(.+)$",
            norm,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if phrase_match:
            remainder = phrase_match.group(2)
            remainder = remainder.split("\\n\\n")[0]
            candidates = re.split(r",\\s*|\\n", remainder)
            for c in candidates:
                c = c.strip().strip("-").strip()
                if c:
                    phrase_field_matches.append(c)

        for p in phrase_field_matches:
            lines.insert(0, p)

        fields = parse_fields_from_lines(lines)
        nested = detect_nested_from_text(norm, fields)

        attributes = {}
        if fields:
            attributes["KEYS"] = "+".join([f.name for f in fields])
        if nested:
            attributes["NESTED"] = "true"

        canonical_format = (
            "LIST"
            if format_hint == "LIST"
            else ("JSON" if format_hint == "JSON" else "STRUCTURED")
        )

        return OutputSchema(
            format_type=canonical_format,
            fields=fields,
            attributes=attributes,
            raw_schema=text,
            format_hint=canonical_format,
        )

    @staticmethod
    def _parse_simple_schema_string(schema_str: str) -> dict:
        # very simple key: value line parsing fallback
        out = {}
        for line in schema_str.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                out[k.strip()] = v.strip()
        return out
