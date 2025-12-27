from typing import Any

from clm_core.types import SDCompressionConfig, FieldImportance, CLMOutput


class DSEncoder:
    def __init__(
        self,
        *,
        config: SDCompressionConfig,
        catalog_name: str = "CATALOG",
        delimiter: str = ",",
    ) -> None:
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
            [NBA_CATALOG:
             [NBA:id:title:KEY=VALUE:KEY=VALUE]
             [NBA:id:title:KEY=VALUE:KEY=VALUE]
            ]
        """
        if isinstance(catalog, dict):
            compressed_item = self._format_item_token(self.encode_item(catalog))
            return CLMOutput(
                compressed=compressed_item,
                original=catalog,
                metadata={
                    "original_length": len(catalog),
                    "compressed_length": len(compressed_item),
                    "output_tokens": len(compressed_item.split()),
                },
            )

        count_catalogs = len(catalog)
        compressed_results = [
            self.encode_item(item) for item in catalog if isinstance(item, dict)
        ]

        if len(compressed_results) > 0:
            compressed_keys = f"{self.delimiter}".join(
                k.upper() for k in self._formated_keys(compressed_results[0])
            )

            lines = [
                f"[{self._catalog_name.upper()}_CATALOG:{count_catalogs}]{{{compressed_keys}}}"
            ]

            for compressed in compressed_results:
                item_token = self._format_item_token(compressed)
                lines.append(f" {item_token}")

            compressed_item = ("\n".join(lines),)
            return CLMOutput(
                compressed=compressed_item,
                original=catalog,
                metadata={
                    "original_length": len(catalog),
                    "compressed_length": len(compressed_item),
                    "output_tokens": len(compressed_item.split()),
                },
            )
        return CLMOutput(
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
            # Always include the ID
            compressed["id"] = item["id"]

        compressed_keys: list[str] = []
        for key, value in item.items():
            if self._should_include_field(key, value):
                if isinstance(value, dict):
                    self.encode_item(value)
                elif isinstance(value, list):
                    self.encode(value)
                else:
                    compressed[key] = value
                compressed_keys.append(key)
        return compressed

    def _format_item_token(self, compressed_item: dict[str, Any]) -> str:
        """
        Format single item as [NBA:id:title:KEY=VALUE:KEY=VALUE]

        Args:
            compressed_item: Dict returned by encode_item()

        Returns:
            Token string like "[NBA:NBA-001:BILLING_ISSUE_RESOLUTION:CATEGORY=BILLING:PRIORITY=HIGH]"
        """
        parts = []

        simple_fields = []
        complex_fields = []

        for key, value in compressed_item.items():
            key_lower = key.lower()
            formatted_value = self._format_value(value)

            if key_lower in self._config.simple_fields:
                simple_fields.append((key_lower, formatted_value))
            else:
                complex_fields.append((key.upper(), formatted_value))

        simple_fields.sort(
            key=lambda x: self._config.default_fields_order.index(x[0])
            if x[0] in self._config.default_fields_order
            else 999
        )

        for _, value in simple_fields:
            parts.append(value)

        for key, value in complex_fields:
            if value and value != "":
                parts.append(f"{value}")

        return f"[{f'{self.delimiter}'.join(parts)}]"

    @staticmethod
    def _formated_keys(compressed_item: dict[str, Any]):
        return compressed_item.keys()

    @staticmethod
    def _format_value(value: Any) -> str:
        """
        Format a value for token output

        Args:
            value: Any value from compressed item

        Returns:
             Formatted string
        """
        if isinstance(value, list):
            return "+".join([str(v).replace(" ", "_") for v in value])

        if isinstance(value, dict):
            return "+".join([f"{v}" for k, v in value.items()])

        if isinstance(value, str):
            cleaned = value.replace(" ", "_").replace(":", "").replace("=", "")
            return cleaned.upper()

        return str(value)

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
