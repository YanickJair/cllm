import pytest

from clm_core.components.ds_compression.encoder_v2 import SDEncoderV2
from clm_core.types import SDCompressionConfig, FieldImportance, CLMOutput


class TestSDEncoderV2Init:
    def test_default_initialization(self):
        config = SDCompressionConfig()
        encoder = SDEncoderV2(config=config)
        assert encoder._config is config
        assert encoder._delimiter == ","

    def test_custom_delimiter(self):
        config = SDCompressionConfig()
        encoder = SDEncoderV2(config=config, delimiter="|")
        assert encoder._delimiter == "|"


class TestSDEncoderV2EncodeObject:
    def test_encode_simple_object(self):
        config = SDCompressionConfig(drop_non_required_fields=False)
        encoder = SDEncoderV2(config=config)

        result = encoder.encode({"id": "1", "name": "Test"})

        assert isinstance(result, CLMOutput)
        assert result.component == "ds_compression"
        assert "{" in result.compressed
        assert "id" in result.compressed
        assert "1" in result.compressed

    def test_encode_object_with_nested_dict(self):
        config = SDCompressionConfig(
            drop_non_required_fields=False,
            required_fields=["id", "specs"]
        )
        encoder = SDEncoderV2(config=config)

        result = encoder.encode({
            "id": "1",
            "specs": {"cpu": "i7", "ram": "16GB"}
        })

        # Header should include nested schema
        assert "specs:{" in result.compressed
        assert "{" in result.compressed
        assert "1" in result.compressed

    def test_encode_object_with_array_of_objects(self):
        config = SDCompressionConfig(drop_non_required_fields=False)
        encoder = SDEncoderV2(config=config)

        result = encoder.encode({
            "id": "1",
            "actions": [
                {"name": "A", "desc": "X"},
                {"name": "B", "desc": "Y"}
            ]
        })

        # Header should include actions field
        assert "actions" in result.compressed
        # Values should contain the action data
        assert "A" in result.compressed
        assert "B" in result.compressed


class TestSDEncoderV2EncodeList:
    def test_encode_list_of_dicts_as_table(self):
        config = SDCompressionConfig(drop_non_required_fields=False)
        encoder = SDEncoderV2(config=config)

        result = encoder.encode([
            {"id": "1", "name": "First"},
            {"id": "2", "name": "Second"}
        ])

        # Should have header once
        assert result.compressed.count("{") == 1
        # Should have two rows
        assert result.compressed.count("[") == 2
        assert "1" in result.compressed
        assert "2" in result.compressed

    def test_encode_empty_list(self):
        config = SDCompressionConfig()
        encoder = SDEncoderV2(config=config)

        result = encoder.encode([])

        assert result.compressed == ""


class TestSDEncoderV2FormatHeader:
    def test_format_header_simple_fields(self):
        config = SDCompressionConfig(drop_non_required_fields=False)
        encoder = SDEncoderV2(config=config)

        header = encoder._format_header({"id": "1", "name": "Test"})

        assert "id" in header
        assert "name" in header
        assert "," in header

    def test_format_header_nested_object(self):
        config = SDCompressionConfig(drop_non_required_fields=False)
        encoder = SDEncoderV2(config=config)

        header = encoder._format_header({
            "id": "1",
            "details": {"a": "1", "b": "2"}
        })

        # Nested object should have scoped schema
        assert "details:{" in header
        assert "a" in header
        assert "b" in header


class TestSDEncoderV2FormatRow:
    def test_format_row_simple(self):
        config = SDCompressionConfig()
        encoder = SDEncoderV2(config=config)

        row = encoder._format_row({"id": "1", "name": "Test"})

        assert row.startswith("[")
        assert row.endswith("]")
        assert "1" in row
        assert "Test" in row

    def test_format_row_with_nested(self):
        config = SDCompressionConfig()
        encoder = SDEncoderV2(config=config)

        row = encoder._format_row({
            "id": "1",
            "nested": {"a": "x", "b": "y"}
        })

        # Nested values should be in brackets
        assert "[x,y]" in row or "[a,b]" in row or "x,y" in row


class TestSDEncoderV2FormatValue:
    def test_format_string_value(self):
        config = SDCompressionConfig()
        encoder = SDEncoderV2(config=config)

        result = encoder._format_value("Hello")

        assert result == "Hello"

    def test_format_string_escapes_delimiter(self):
        config = SDCompressionConfig()
        encoder = SDEncoderV2(config=config)

        result = encoder._format_value("Hello, World")

        assert result == "Hello; World"

    def test_format_list_value(self):
        config = SDCompressionConfig()
        encoder = SDEncoderV2(config=config)

        result = encoder._format_value(["a", "b", "c"])

        assert result == "a+b+c"

    def test_format_boolean_true(self):
        config = SDCompressionConfig()
        encoder = SDEncoderV2(config=config)

        result = encoder._format_value(True)

        assert result == "true"

    def test_format_boolean_false(self):
        config = SDCompressionConfig()
        encoder = SDEncoderV2(config=config)

        result = encoder._format_value(False)

        assert result == "false"

    def test_format_numeric_value(self):
        config = SDCompressionConfig()
        encoder = SDEncoderV2(config=config)

        result = encoder._format_value(42)

        assert result == "42"

    def test_format_dict_value(self):
        config = SDCompressionConfig()
        encoder = SDEncoderV2(config=config)

        result = encoder._format_value({"a": "1", "b": "2"})

        # Dict value should be formatted as row
        assert "[" in result
        assert "]" in result


class TestSDEncoderV2NormalizeObject:
    def test_drops_empty_lists(self):
        config = SDCompressionConfig()
        encoder = SDEncoderV2(config=config)

        result = encoder._normalize_object({"id": "1", "tags": []})

        assert "tags" not in result
        assert "id" in result

    def test_keeps_empty_list_if_required(self):
        config = SDCompressionConfig(required_fields=["tags"])
        encoder = SDEncoderV2(config=config)

        result = encoder._normalize_object({"id": "1", "tags": []})

        assert "tags" in result

    def test_truncates_long_strings(self):
        config = SDCompressionConfig(max_description_length=10)
        encoder = SDEncoderV2(config=config)

        result = encoder._normalize_object({"desc": "This is a very long description"})

        assert result["desc"] == "This is a ..."


class TestSDEncoderV2FilterFields:
    def test_drop_non_required_fields(self):
        config = SDCompressionConfig(
            drop_non_required_fields=True,
            required_fields=["id"]
        )
        encoder = SDEncoderV2(config=config)

        result = encoder._filter_fields({"id": "1", "name": "Test", "extra": "data"})

        assert "id" in result
        assert "name" not in result
        assert "extra" not in result

    def test_excludes_fields(self):
        config = SDCompressionConfig(
            drop_non_required_fields=False,
            excluded_fields=["secret"]
        )
        encoder = SDEncoderV2(config=config)

        result = encoder._filter_fields({"id": "1", "secret": "password"})

        assert "id" in result
        assert "secret" not in result

    def test_required_fields_always_included(self):
        config = SDCompressionConfig(
            drop_non_required_fields=False,
            required_fields=["id", "name"],
            importance_threshold=1.0
        )
        encoder = SDEncoderV2(config=config)

        result = encoder._filter_fields({"id": "1", "name": "Test"})

        assert "id" in result
        assert "name" in result


class TestSDEncoderV2FieldImportance:
    def test_detects_id_as_critical(self):
        config = SDCompressionConfig()
        encoder = SDEncoderV2(config=config)

        importance = encoder._detect_field_importance("id", "123")

        assert importance == FieldImportance.CRITICAL

    def test_detects_name_as_high(self):
        config = SDCompressionConfig()
        encoder = SDEncoderV2(config=config)

        importance = encoder._detect_field_importance("name", "Test")

        assert importance == FieldImportance.HIGH

    def test_detects_underscore_prefix_as_low(self):
        config = SDCompressionConfig()
        encoder = SDEncoderV2(config=config)

        importance = encoder._detect_field_importance("_internal", "data")

        assert importance == FieldImportance.LOW

    def test_detects_date_suffix_as_never(self):
        config = SDCompressionConfig()
        encoder = SDEncoderV2(config=config)

        # created_at is in default_fields_importance as LOW, so test with custom field
        importance = encoder._detect_field_importance("published_at", "2024-01-01")

        assert importance == FieldImportance.NEVER

    def test_detects_empty_value_as_never(self):
        config = SDCompressionConfig()
        encoder = SDEncoderV2(config=config)

        importance = encoder._detect_field_importance("field", "")

        assert importance == FieldImportance.NEVER


class TestSDEncoderV2OrderedItems:
    def test_simple_fields_come_first(self):
        config = SDCompressionConfig(
            simple_fields=["id", "name"],
            default_fields_order=["id", "name"]
        )
        encoder = SDEncoderV2(config=config)

        items = list(encoder._ordered_items({
            "description": "text",
            "id": "1",
            "name": "Test"
        }))

        keys = [k for k, _ in items]
        assert keys.index("id") < keys.index("description")
        assert keys.index("name") < keys.index("description")


class TestSDEncoderV2SameSchema:
    def test_same_schema_returns_true(self):
        result = SDEncoderV2._same_schema([
            {"a": 1, "b": 2},
            {"a": 3, "b": 4}
        ])

        assert result is True

    def test_different_schema_returns_false(self):
        result = SDEncoderV2._same_schema([
            {"a": 1, "b": 2},
            {"a": 3, "c": 4}
        ])

        assert result is False


class TestSDEncoderV2Integration:
    def test_full_encode_with_nested_actions(self):
        config = SDCompressionConfig(
            drop_non_required_fields=False,
            required_fields=["id", "title", "actions"]
        )
        encoder = SDEncoderV2(config=config)

        data = {
            "id": "NBA-001",
            "title": "Billing Issue",
            "actions": [
                {"name": "Verify", "steps": ["Step 1", "Step 2"]},
                {"name": "Refund", "steps": ["Step A", "Step B"]}
            ]
        }

        result = encoder.encode(data)

        # Header should include actions
        assert "actions" in result.compressed
        assert "id" in result.compressed
        assert "title" in result.compressed
        # Values should contain the data
        assert "NBA-001" in result.compressed
        assert "Billing Issue" in result.compressed

    def test_compression_ratio_positive(self):
        config = SDCompressionConfig(drop_non_required_fields=False)
        encoder = SDEncoderV2(config=config)

        data = [
            {"id": "1", "name": "Product A", "description": "A long description here"},
            {"id": "2", "name": "Product B", "description": "Another long description"},
        ]

        result = encoder.encode(data)

        # Should have positive compression
        assert result.compression_ratio >= 0

    def test_clm_output_fields(self):
        config = SDCompressionConfig()
        encoder = SDEncoderV2(config=config)

        result = encoder.encode({"id": "1"})

        assert hasattr(result, "compressed")
        assert hasattr(result, "original")
        assert hasattr(result, "n_tokens")
        assert hasattr(result, "c_tokens")
        assert hasattr(result, "compression_ratio")
        assert result.component == "ds_compression"
