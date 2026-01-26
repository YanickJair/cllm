from typing import Any, Iterable

from clm_core.types import SDCompressionConfig, FieldImportance, CLMOutput


class SDEncoderV2:
    """
    Canonical CLM encoder

    - Header-first, row-based
    - Explicit nested schema scoping: key:{nested}
    - Tables only at root or via semantic wrapper
    - No nested tables
    - Config-driven
    """

    ROW_OPEN = "["
    ROW_CLOSE = "]"

    def __init__(
        self,
        *,
        config: SDCompressionConfig,
        delimiter: str = ",",
    ):
        self._config = config
        self._delimiter = delimiter

    def encode(self, data: Any) -> CLMOutput:
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

    def _encode_object(self, obj: dict[str, Any]) -> str:
        normalized = self._normalize_object(obj)

        table_fields = self._find_table_fields(normalized)
        if (
            self._config.preserve_structure
            and len(table_fields) == 1
            and not self._has_identity_fields(normalized)
        ):
            _, table = table_fields[0]
            return self._encode_table(table)

        row = self._filter_fields(normalized)
        header = self._format_header(row)
        body = self._format_row(row)
        return f"{{{header}}}{body}"

    def _encode_list(self, items: list[Any]) -> str:
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
                parts.append(self._encode_object(item))
            else:
                parts.append(str(item))
        return "".join(parts)

    def _encode_table(self, rows: list[dict[str, Any]]) -> str:
        normalized_rows = [self._filter_fields(self._normalize_object(r)) for r in rows]

        header = self._format_header(normalized_rows[0])
        body = "".join(self._format_row(r) for r in normalized_rows)

        return f"{{{header}}}{body}"

    def _format_header(self, row: dict[str, Any]) -> str:
        parts = []
        for key, value in self._ordered_items(row):
            if isinstance(value, dict):
                nested = self._format_header(value)
                parts.append(f"{key}:{{{nested}}}")
            else:
                parts.append(key)
        return self._delimiter.join(parts)

    def _format_row(self, row: dict[str, Any]) -> str:
        values = [self._format_value(v) for _, v in self._ordered_items(row)]
        return f"{self.ROW_OPEN}{self._delimiter.join(values)}{self.ROW_CLOSE}"

    def _format_value(self, value: Any) -> str:
        if isinstance(value, dict):
            return self._format_row(value)
        if isinstance(value, list):
            return "+".join(str(v) for v in value)
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, str):
            return value.replace(self._delimiter, ";")
        return str(value)

    def _normalize_object(self, obj: dict[str, Any]) -> dict[str, Any]:
        """
        Early normalization:
        - truncate strings
        - drop empty lists unless required
        """
        out = {}
        for key, value in obj.items():
            value = self._normalize_value(value)

            if value == [] and (
                not self._config.required_fields
                or key not in self._config.required_fields
            ):
                continue

            out[key] = value
        return out

    def _normalize_value(self, value: Any) -> Any:
        if (
            isinstance(value, str)
            and self._config.max_description_length
            and len(value) > self._config.max_description_length
        ):
            return value[: self._config.max_description_length] + "..."
        return value

    def _filter_fields(self, obj: dict[str, Any]) -> dict[str, Any]:
        """
        Importance filtering with recursive dict preservation.
        """
        out = {}
        for key, value in obj.items():
            if not self._should_include_field(key, value):
                continue

            if isinstance(value, dict) and self._config.preserve_structure:
                out[key] = self._filter_fields(value)
            else:
                out[key] = value

        return out

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

    def _should_include_field(self, key: str, value: Any) -> bool:
        if self._config.drop_non_required_fields:
            return self._config.required_fields and key in self._config.required_fields

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
