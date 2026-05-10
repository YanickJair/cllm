from typing import Any, Iterable, Annotated

from annotated_doc import Doc
from thread_encoder.types import SDCompressionConfig, FieldImportance, CLMOutput


class SDEncoderV2:
    """
    Canonical CLM structured-data encoder (V2)

    Features:
    - Header-first, row-based encoding
    - Explicit nested schema scoping: key:{nested}
    - Path-aware required field projection (e.g. users.name)
    - Strict projection via drop_non_required_fields
    - Early string truncation
    """

    ROW_OPEN = "["
    ROW_CLOSE = "]"

    def __init__(
        self,
        *,
        config: Annotated[
            SDCompressionConfig,
            Doc(
                "Configuration controlling field selection, truncation, structure preservation, and required-field projection."
            ),
        ],
        delimiter: Annotated[
            str, Doc("Character used to separate field values inside bracket tokens.")
        ] = ",",
    ):
        self._config = config
        self._delimiter = delimiter
        self._required_paths = set(config.required_fields or [])

    def encode(
        self,
        data: Annotated[
            Any,
            Doc("The input to compress. May be a dict, list of dicts, or a scalar."),
        ],
    ) -> CLMOutput:
        if isinstance(data, dict):
            compressed = self._encode_object(data)
        elif isinstance(data, list):
            compressed = self._encode_list(data)
        else:
            compressed = str(data)

        return CLMOutput(
            component="ds_compression",
            compressed=compressed,
            original=data,
            metadata={},
        )

    def _encode_object(
        self,
        obj: Annotated[
            dict[str, Any],
            Doc(
                "A dict to encode, potentially containing nested objects or table-valued keys."
            ),
        ],
    ) -> str:
        normalized = self._normalize_object(obj)

        table_fields = self._find_table_fields(normalized)
        if (
            self._config.preserve_structure
            and len(table_fields) == 1
            and len(normalized) == 1
            and not self._has_identity_fields(normalized)
        ):
            _, table = table_fields[0]
            return self._encode_table(table)

        row = self._filter_fields(normalized, path="")
        if not row:
            return ""

        header = self._format_header(row)
        body = self._format_row(row)
        return f"{{{header}}}{body}"

    def _encode_list(
        self,
        items: Annotated[
            list[Any],
            Doc(
                "A list of items to encode. Homogeneous list-of-dicts are encoded as a table; mixed lists are encoded item-by-item."
            ),
        ],
    ) -> str:
        dict_items = [x for x in items if isinstance(x, dict)]

        if (
            dict_items
            and len(dict_items) == len(items)
            and self._same_schema(dict_items)
        ):
            return self._encode_table(dict_items)

        parts = []
        for item in items:
            if isinstance(item, dict):
                encoded = self._encode_object(item)
                if encoded:
                    parts.append(encoded)
            else:
                parts.append(str(item))
        return "".join(parts)

    def _encode_table(
        self,
        rows: Annotated[
            list[dict[str, Any]],
            Doc("A list of same-schema dicts to encode as a header+rows table."),
        ],
    ) -> str:
        filtered_rows = [
            self._filter_fields(self._normalize_object(r), path="") for r in rows
        ]
        filtered_rows = [r for r in filtered_rows if r]

        if not filtered_rows:
            return ""

        header = self._format_header(filtered_rows[0])
        body = "".join(self._format_row(r) for r in filtered_rows)
        return f"{{{header}}}{body}"

    def _format_header(
        self,
        row: Annotated[
            dict[str, Any],
            Doc("A representative row dict whose keys define the header schema."),
        ],
    ) -> str:
        parts = []
        for key, value in self._ordered_items(row):
            if isinstance(value, dict):
                nested = self._format_header(value)
                parts.append(f"{key}:{{{nested}}}")
            elif self._is_nested_table(value):
                nested = self._format_header(value[0])
                parts.append(f"{key}:{{{nested}}}")
            else:
                parts.append(key)
        return self._delimiter.join(parts)

    def _format_row(
        self,
        row: Annotated[
            dict[str, Any],
            Doc("A single normalized row dict to format as a bracketed token."),
        ],
    ) -> str:
        values = [self._format_value(v) for _, v in self._ordered_items(row)]
        return f"{self.ROW_OPEN}{self._delimiter.join(values)}{self.ROW_CLOSE}"

    def _format_value(
        self,
        value: Annotated[
            Any,
            Doc(
                "A value from a normalized row (may be str, int, bool, list, or nested dict)."
            ),
        ],
    ) -> str:
        if isinstance(value, dict):
            if len(value) == 1:
                return self._format_value(next(iter(value.values())))
            return self._format_row(value)
        if self._is_nested_table(value):
            return "".join(self._format_row(item) for item in value)
        if isinstance(value, list):
            return "+".join(str(v) for v in value)
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, str):
            return value.replace(self._delimiter, ";")
        return str(value)

    def _normalize_object(
        self,
        obj: Annotated[
            dict[str, Any],
            Doc(
                "A raw dict to normalize: recursively normalize values and drop empty non-required list fields."
            ),
        ],
    ) -> dict[str, Any]:
        out = {}
        for key, value in obj.items():
            value = self._normalize_value(value, key)
            if value == [] and not self._is_required_path(key):
                continue
            out[key] = value
        return out

    def _normalize_value(
        self,
        value: Annotated[
            Any,
            Doc(
                "The raw value to normalize; strings may be truncated according to config."
            ),
        ],
        key: Annotated[
            str, Doc("The field name; used for per-field truncation mapping lookups.")
        ],
    ) -> Any:
        if isinstance(value, dict):
            return self._normalize_object(value)
        if (
            isinstance(value, list)
            and value
            and all(isinstance(x, dict) for x in value)
        ):
            return [self._normalize_object(x) for x in value]
        if (
            isinstance(value, str)
            and self._config.max_truncation_mapping
            and key in self._config.max_truncation_mapping
            and len(value) > self._config.max_truncation_mapping[key]
        ):
            value = value[: self._config.max_truncation_mapping[key]] + "..."
        elif (
            isinstance(value, str)
            and self._config.max_truncation_length
            and len(value) > self._config.max_truncation_length
        ):
            return value[: self._config.max_truncation_length] + "..."
        return value

    def _filter_fields(
        self,
        obj: Annotated[
            dict[str, Any],
            Doc(
                "A normalized dict to filter according to path-based projection rules."
            ),
        ],
        *,
        path: Annotated[
            str,
            Doc(
                "Dot-separated path prefix for the current recursion level, e.g. 'users' or 'users.address'."
            ),
        ],
    ) -> dict[str, Any]:
        out = {}

        for key, value in obj.items():
            full_path = f"{path}.{key}" if path else key

            if not self._should_include_path(full_path, value):
                continue

            if isinstance(value, dict) and self._config.preserve_structure:
                nested = self._filter_fields(value, path=full_path)
                if nested:
                    out[key] = nested
            elif self._is_nested_table(value) and self._config.preserve_structure:
                # Filter first item to determine schema, then apply
                # the same keys to all items for consistent schema.
                first = self._filter_fields(value[0], path=full_path)
                if first:
                    kept = set(first.keys())
                    filtered = [first] + [
                        {k: item[k] for k in item if k in kept} for item in value[1:]
                    ]
                    out[key] = filtered
            else:
                out[key] = value

        return out

    def _should_include_path(self, path: str, value: Any) -> bool:
        """
        Strict path-based projection.
        """
        if self._config.drop_non_required_fields and self._required_paths:
            # exact match
            if path in self._required_paths:
                return True

            # prefix match (parent of required path)
            for req in self._required_paths:
                if req.startswith(path + "."):
                    return True

            return False

        key = path.split(".")[-1]
        if self._config.excluded_fields and key in self._config.excluded_fields:
            return False

        if self._config.required_fields and key in self._config.required_fields:
            return True

        if self._config.field_importance and key in self._config.field_importance:
            return (
                self._config.field_importance[key] >= self._config.importance_threshold
            )

        if self._config.auto_detect:
            return (
                self._detect_field_importance(key, value).value
                >= self._config.importance_threshold
            )

        return True

    def _is_required_path(self, key: str) -> bool:
        return any(rp == key or rp.startswith(key + ".") for rp in self._required_paths)

    @staticmethod
    def _find_table_fields(
        obj: dict[str, Any],
    ) -> list[tuple[str, list[dict[str, Any]]]]:
        return [
            (k, v)
            for k, v in obj.items()
            if isinstance(v, list) and v and all(isinstance(x, dict) for x in v)
        ]

    def _has_identity_fields(self, obj: dict[str, Any]) -> bool:
        identity = set(f.lower() for f in self._config.simple_fields)
        return any(k.lower() in identity for k in obj.keys())

    @staticmethod
    def _is_nested_table(value: Any) -> bool:
        return (
            isinstance(value, list)
            and len(value) > 0
            and all(isinstance(x, dict) for x in value)
            and SDEncoderV2._same_schema(value)
        )

    @staticmethod
    def _same_schema(rows: list[dict[str, Any]]) -> bool:
        keys = set(rows[0].keys())
        return all(set(r.keys()) == keys for r in rows)

    def _ordered_items(self, obj: dict[str, Any]) -> Iterable[tuple[str, Any]]:
        simple, complex_ = [], []

        for key, val in obj.items():
            if key.lower() in self._config.simple_fields:
                simple.append((key, val))
            else:
                complex_.append((key, val))

        simple.sort(
            key=lambda x: self._config.default_fields_order.index(x[0])
            if x[0] in self._config.default_fields_order
            else 999
        )
        return simple + complex_

    def _detect_field_importance(self, key: str, value: Any) -> FieldImportance:
        key_lower = key.lower()

        for pattern, importance in self._config.default_fields_importance.items():
            if pattern in key_lower:
                return importance

        if key_lower.startswith("_"):
            return FieldImportance.LOW

        if key_lower.endswith("_at") or key_lower.endswith("_date"):
            return FieldImportance.NEVER

        if not value:
            return FieldImportance.NEVER

        if isinstance(value, str):
            if len(value) > 500:
                return FieldImportance.MEDIUM
            if len(value) < 3:
                return FieldImportance.LOW

        return FieldImportance.MEDIUM
