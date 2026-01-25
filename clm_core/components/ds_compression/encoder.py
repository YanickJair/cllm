from typing import Any

from clm_core.types import SDCompressionConfig, FieldImportance, CLMOutput


class SDEncoder:
    ROW_SEPARATOR = "|"
    NESTED_OPEN = "["
    NESTED_CLOSE = "]"
    SCHEMA_OPEN = "{"
    SCHEMA_CLOSE = "}"

    def __init__(
        self,
        *,
        config: SDCompressionConfig,
        catalog_name: str = "CATALOG",
        delimiter: str = ",",
    ):
        self._config = config
        self._catalog_name = catalog_name
        self._done: bool = False
        self._delimiter = delimiter

    @property
    def delimiter(self) -> str:
        return self._delimiter

    @delimiter.setter
    def delimiter(self, val: str) -> None:
        self._delimiter = val

    def encode(self, catalog: list[dict[str, Any]] | dict[str, Any]) -> CLMOutput:
        """
        Main entry point: compress entire catalog

        Args:
            catalog: List of catalog items (any schema)

        Returns:
            Compressed catalog in format:
            {field1,field2,field3}[value1,value2,value3][value1,value2,value3]
        """
        if isinstance(catalog, dict):
            compressed_item = self._format_item_token(self.encode_item(catalog))
            return CLMOutput(
                component="ds_compression",
                compressed=compressed_item,
                original=catalog,
                metadata={
                    "original_length": len(catalog),
                    "compressed_length": len(compressed_item),
                },
            )

        compressed_results = [
            self.encode_item(item) for item in catalog if isinstance(item, dict)
        ]

        if len(compressed_results) > 0:
            compressed_keys = self._format_header_keys(compressed_results[0])

            parts = [f"{{{compressed_keys}}}"]

            for compressed in compressed_results:
                item_token = self._format_item_token(compressed)
                parts.append(item_token)

            compressed_item = "".join(parts)
            return CLMOutput(
                component="ds_compression",
                compressed=compressed_item,
                original=catalog,
                metadata={
                    "original_length": len(catalog),
                    "compressed_length": len(compressed_item),
                },
            )
        return CLMOutput(
            component="ds_compression",
            compressed="",
            original=catalog,
            metadata={
                "original_length": len(catalog),
                "compressed_length": 0,
            },
        )

    def encode_item(self, item: dict[str, Any]) -> dict[str, Any]:
        """
        Compress a single catalog item

        This is where your diagram's logic happens
        """
        compressed: dict[str, Any] = {}

        if "id" in item:
            compressed["id"] = item["id"]

        for key, value in item.items():
            if not self._should_include_field(key, value):
                continue
            if isinstance(value, dict):
                compressed[key] = self.encode_item(value)
            elif isinstance(value, list):
                compressed[key] = [
                    self.encode_item(v) if isinstance(v, dict) else v
                    for v in value
                ]
            else:
                compressed[key] = value
        return compressed

    def _get_ordered_fields(self, compressed_item: dict[str, Any]) -> list[tuple[str, Any]]:
        """
        Get fields ordered consistently: simple fields (sorted by default_fields_order) first,
        then complex fields.

        Returns:
            List of (key, value) tuples in the correct order
        """
        simple_fields = []
        complex_fields = []

        for key, value in compressed_item.items():
            key_lower = key.lower()
            if key_lower in self._config.simple_fields:
                simple_fields.append((key_lower, value))
            else:
                complex_fields.append((key_lower, value))

        simple_fields.sort(
            key=lambda x: self._config.default_fields_order.index(x[0])
            if x[0] in self._config.default_fields_order
            else 999
        )

        return simple_fields + complex_fields

    def _format_item_token(self, compressed_item: dict[str, Any]) -> str:
        """
        Format single item as a bracketed token with delimiter-separated values.

        Args:
            compressed_item: Dict returned by encode_item()

        Returns:
            Token string like "[ID-001,Product Name,Category,199.99]"
        """
        ordered_fields = self._get_ordered_fields(compressed_item)
        parts = []

        for key, value in ordered_fields:
            # Apply max length for non-simple fields (complex/description fields)
            max_len = None
            if key.lower() not in self._config.simple_fields:
                max_len = self._config.max_description_length

            formatted_value = self._format_value(value, max_length=max_len)
            if formatted_value and formatted_value != "":
                parts.append(formatted_value)

        return f"[{f'{self.delimiter}'.join(parts)}]"

    def _format_header_keys(self, compressed_item: dict[str, Any]) -> str:
        """
        Format header keys in the same order as values are formatted.
        """
        ordered_fields = self._get_ordered_fields(compressed_item)
        return self.delimiter.join(key for key, _ in ordered_fields)

    def _format_value(self, value: Any, max_length: int | None = None) -> str:
        """
        Format a value for token output - minimal transformation for max compression.

        Args:
            value: Any value from compressed item
            max_length: Optional maximum length for the formatted value

        Returns:
             Formatted string
        """
        if isinstance(value, list):
            # list of dicts → multiple rows
            if value and isinstance(value[0], dict):
                rows = [self._format_inline_object(v) for v in value]
                return self.ROW_SEPARATOR.join(rows)
            return "+".join(str(v) for v in value)

        if isinstance(value, dict):
            return self._format_inline_object(value)

        if isinstance(value, str):
            result = value.replace(self._delimiter, ";")
        else:
            result = str(value)

        if max_length and len(result) > max_length:
            result = result[:max_length] + "..."
        return result

    def _format_inline_object(self, obj: dict[str, Any]) -> str:
        ordered = self._get_ordered_fields(obj)

        schema = self.delimiter.join(k for k, _ in ordered)
        values = self.delimiter.join(
            self._format_value(v) for _, v in ordered
        )

        return (
            f"{self.SCHEMA_OPEN}{schema}{self.SCHEMA_CLOSE}"
            f"{self.NESTED_OPEN}{values}{self.NESTED_CLOSE}"
        )

    def _should_include_field(self, key: str, value: Any) -> bool:
        """
        Decide if a field should be included (your diagram's decision logic)

        This implements both Blue and Orange approaches
        """
        if self._config.excluded_fields and key in self._config.excluded_fields:
            return False

        if self._config.required_fields and key in self._config.required_fields:
            return True

        if self._config.field_importance and key in self._config.field_importance:
            return (
                self._config.field_importance[key] >= self._config.importance_threshold
            )

        if self._config.auto_detect:
            importance = self._detect_field_importance(key, value)
            return importance.value >= self._config.importance_threshold
        return True

    def _detect_field_importance(self, key: str, value: Any) -> FieldImportance:
        """
        Automatically detect how important a field is (Orange approach)

        This is the "intelligent" system that learns what's important
        """
        key_lower = key.lower()

        for pattern, importance in self._config.default_fields_importance.items():
            if pattern in key_lower:
                return importance

        if key_lower.startswith("internal_") or key_lower.startswith("_"):
            return FieldImportance.LOW

        if key_lower.endswith("_at") or key_lower.endswith("_date"):
            return FieldImportance.NEVER

        if value is None or value == "":
            return FieldImportance.NEVER

        if isinstance(value, str):
            if len(value) > 500:
                return FieldImportance.MEDIUM
            if len(value) < 3:
                return FieldImportance.LOW
        return FieldImportance.MEDIUM
