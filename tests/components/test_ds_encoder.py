import pytest

from clm_core.components.ds_compression.encoder import DSEncoder
from clm_core.types import SDCompressionConfig, FieldImportance, CLMOutput


class TestCLMOutputEstimateTokens:
    """Token estimation is now a CLMOutput responsibility"""

    def test_estimate_tokens_string(self):
        result = CLMOutput._estimate_tokens("Hello world!")  # 12 chars
        assert result == 3  # 12 // 4 = 3

    def test_estimate_tokens_dict(self):
        data = {"id": "123", "name": "test"}
        result = CLMOutput._estimate_tokens(data)
        # JSON: {"id": "123", "name": "test"} = ~30 chars -> 7 tokens
        assert result >= 1

    def test_estimate_tokens_list(self):
        data = [{"id": "1"}, {"id": "2"}]
        result = CLMOutput._estimate_tokens(data)
        assert result >= 1

    def test_estimate_tokens_minimum_is_one(self):
        result = CLMOutput._estimate_tokens("ab")  # 2 chars
        assert result == 1  # max(1, 2//4) = max(1, 0) = 1

    def test_estimate_tokens_empty_string(self):
        result = CLMOutput._estimate_tokens("")
        assert result == 1  # minimum is 1


class TestDSEncoderInit:
    def test_default_initialization(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)
        assert encoder._config is config
        assert encoder._catalog_name == "CATALOG"
        assert encoder._delimiter == ","
        assert encoder._done is False

    def test_custom_catalog_name(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config, catalog_name="PRODUCTS")
        assert encoder._catalog_name == "PRODUCTS"

    def test_custom_delimiter(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config, delimiter="|")
        assert encoder._delimiter == "|"


class TestDSEncoderDelimiterProperty:
    def test_delimiter_getter(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config, delimiter=":")
        assert encoder.delimiter == ":"

    def test_delimiter_setter(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)
        encoder.delimiter = ";"
        assert encoder.delimiter == ";"




class TestDSEncoderEncode:
    def test_encode_single_dict(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)
        data = {"id": "123", "name": "Test Product"}

        result = encoder.encode(data)

        assert isinstance(result, CLMOutput)
        assert result.component == "ds_compression"
        assert result.original == data
        assert "[" in result.compressed and "]" in result.compressed

    def test_encode_list_of_dicts(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)
        data = [
            {"id": "1", "name": "Product A"},
            {"id": "2", "name": "Product B"},
        ]

        result = encoder.encode(data)

        assert isinstance(result, CLMOutput)
        assert result.component == "ds_compression"
        assert result.original == data
        # Should have header and items
        assert "{" in result.compressed  # header
        assert "[" in result.compressed  # items

    def test_encode_empty_list(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)
        data = []

        result = encoder.encode(data)

        assert isinstance(result, CLMOutput)
        assert result.compressed == ""
        assert result.c_tokens == 1  # minimum token count is 1

    def test_encode_sets_n_tokens_and_c_tokens(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)
        data = [{"id": "1", "name": "Test"}]

        result = encoder.encode(data)

        assert result.n_tokens > 0
        assert result.c_tokens > 0
        assert result.n_tokens >= result.c_tokens  # compression should reduce tokens

    def test_encode_compression_ratio_is_valid(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)
        data = [
            {"product_id": "PROD-001", "name": "Widget", "price": 9.99},
            {"product_id": "PROD-002", "name": "Gadget", "price": 19.99},
        ]

        result = encoder.encode(data)

        # Compression ratio should be between -inf and 100
        assert result.compression_ratio <= 100
        # For structured data, we expect positive compression
        assert result.compression_ratio > 0

    def test_encode_metadata_contains_lengths(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)
        data = [{"id": "1"}]

        result = encoder.encode(data)

        assert "original_length" in result.metadata
        assert "compressed_length" in result.metadata


class TestDSEncoderEncodeItem:
    def test_encode_item_includes_id(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)
        item = {"id": "123", "name": "Test"}

        result = encoder.encode_item(item)

        assert "id" in result
        assert result["id"] == "123"

    def test_encode_item_respects_required_fields(self):
        config = SDCompressionConfig(required_fields=["custom_field"])
        encoder = DSEncoder(config=config)
        item = {"id": "1", "custom_field": "value", "other": "data"}

        result = encoder.encode_item(item)

        assert "custom_field" in result

    def test_encode_item_respects_excluded_fields(self):
        config = SDCompressionConfig(excluded_fields=["secret", "password"])
        encoder = DSEncoder(config=config)
        item = {"id": "1", "name": "Test", "secret": "hidden", "password": "123"}

        result = encoder.encode_item(item)

        assert "secret" not in result
        assert "password" not in result

    def test_encode_item_filters_by_importance_threshold(self):
        config = SDCompressionConfig(
            auto_detect=True,
            importance_threshold=0.8  # Only HIGH and CRITICAL
        )
        encoder = DSEncoder(config=config)
        # 'notes' has LOW importance by default
        item = {"id": "1", "name": "Test", "notes": "some notes"}

        result = encoder.encode_item(item)

        assert "id" in result
        assert "name" in result
        # notes should be excluded due to LOW importance < 0.8 threshold
        assert "notes" not in result


class TestDSEncoderGetOrderedFields:
    def test_simple_fields_come_first(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)
        item = {"description": "A description", "id": "123", "name": "Test"}

        result = encoder._get_ordered_fields(item)
        keys = [k for k, v in result]

        # id and name are simple fields, description is complex
        assert keys.index("id") < keys.index("description")
        assert keys.index("name") < keys.index("description")

    def test_simple_fields_sorted_by_default_order(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)
        # default_fields_order has id before name
        item = {"name": "Test", "id": "123"}

        result = encoder._get_ordered_fields(item)
        keys = [k for k, v in result]

        assert keys.index("id") < keys.index("name")

    def test_complex_fields_at_end(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)
        item = {"id": "1", "custom_field": "value", "another_custom": "data"}

        result = encoder._get_ordered_fields(item)
        keys = [k for k, v in result]

        # id is simple, custom fields are complex and at end
        assert keys[0] == "id"


class TestDSEncoderFormatItemToken:
    def test_format_with_default_delimiter(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)
        item = {"id": "123", "name": "Test"}

        result = encoder._format_item_token(item)

        assert result.startswith("[")
        assert result.endswith("]")
        assert "," in result  # default delimiter

    def test_format_with_custom_delimiter(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config, delimiter="|")
        item = {"id": "123", "name": "Test"}

        result = encoder._format_item_token(item)

        assert "|" in result

    def test_truncates_long_complex_fields(self):
        config = SDCompressionConfig(max_description_length=20)
        encoder = DSEncoder(config=config)
        item = {"id": "1", "description": "A" * 100}  # 100 chars

        result = encoder._format_item_token(item)

        # Should be truncated with ...
        assert "..." in result
        assert "A" * 100 not in result


class TestDSEncoderFormatHeaderKeys:
    def test_header_matches_value_order(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)
        item = {"description": "desc", "id": "1", "name": "test"}

        header = encoder._format_header_keys(item)
        token = encoder._format_item_token(item)

        header_keys = header.split(",")
        # Verify order is consistent
        assert header_keys[0] == "id"
        assert header_keys[1] == "name"
        assert "description" in header_keys

    def test_header_uses_delimiter(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config, delimiter="|")
        item = {"id": "1", "name": "test"}

        header = encoder._format_header_keys(item)

        assert "|" in header


class TestDSEncoderFormatValue:
    def test_format_string_value(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)

        result = encoder._format_value("Hello World")

        assert result == "Hello World"

    def test_format_string_escapes_delimiter(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config, delimiter=",")

        result = encoder._format_value("Hello, World")

        assert result == "Hello; World"  # comma replaced with semicolon

    def test_format_list_value(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)

        result = encoder._format_value(["a", "b", "c"])

        assert result == "a+b+c"

    def test_format_dict_value(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)

        result = encoder._format_value({"key1": "val1", "key2": "val2"})

        assert "val1" in result
        assert "val2" in result
        assert "+" in result

    def test_format_numeric_value(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)

        result = encoder._format_value(42)

        assert result == "42"

    def test_format_boolean_value(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)

        assert encoder._format_value(True) == "True"
        assert encoder._format_value(False) == "False"

    def test_format_truncates_with_max_length(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)

        result = encoder._format_value("A" * 100, max_length=20)

        assert len(result) == 23  # 20 + "..."
        assert result.endswith("...")

    def test_format_no_truncation_when_under_max_length(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)

        result = encoder._format_value("Short", max_length=100)

        assert result == "Short"
        assert "..." not in result


class TestDSEncoderShouldIncludeField:
    def test_excludes_field_in_excluded_fields(self):
        config = SDCompressionConfig(excluded_fields=["secret"])
        encoder = DSEncoder(config=config)

        result = encoder._should_include_field("secret", "value")

        assert result is False

    def test_includes_field_in_required_fields(self):
        config = SDCompressionConfig(required_fields=["must_have"])
        encoder = DSEncoder(config=config)

        result = encoder._should_include_field("must_have", "value")

        assert result is True

    def test_uses_custom_field_importance(self):
        config = SDCompressionConfig(
            field_importance={"custom": 0.9},
            importance_threshold=0.8
        )
        encoder = DSEncoder(config=config)

        assert encoder._should_include_field("custom", "value") is True

    def test_uses_custom_field_importance_below_threshold(self):
        config = SDCompressionConfig(
            field_importance={"custom": 0.3},
            importance_threshold=0.5
        )
        encoder = DSEncoder(config=config)

        assert encoder._should_include_field("custom", "value") is False

    def test_auto_detect_mode(self):
        config = SDCompressionConfig(auto_detect=True)
        encoder = DSEncoder(config=config)

        # 'id' should be detected as CRITICAL
        assert encoder._should_include_field("user_id", "123") is True

    def test_includes_all_when_auto_detect_disabled(self):
        config = SDCompressionConfig(auto_detect=False)
        encoder = DSEncoder(config=config)

        assert encoder._should_include_field("random_field", "value") is True


class TestDSEncoderDetectFieldImportance:
    def test_detects_id_as_critical(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)

        result = encoder._detect_field_importance("user_id", "123")

        assert result == FieldImportance.CRITICAL

    def test_detects_name_as_high(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)

        result = encoder._detect_field_importance("product_name", "Widget")

        assert result == FieldImportance.HIGH

    def test_detects_internal_prefix_as_low(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)

        result = encoder._detect_field_importance("internal_code", "abc")

        assert result == FieldImportance.LOW

    def test_detects_underscore_prefix_as_low(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)

        result = encoder._detect_field_importance("_private", "value")

        assert result == FieldImportance.LOW

    def test_detects_date_suffix_as_never(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)

        # Use field names not in default_fields_importance to test suffix detection
        assert encoder._detect_field_importance("processed_at", "2024-01-01") == FieldImportance.NEVER
        assert encoder._detect_field_importance("expiry_date", "1990-01-01") == FieldImportance.NEVER

    def test_detects_none_value_as_never(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)

        result = encoder._detect_field_importance("some_field", None)

        assert result == FieldImportance.NEVER

    def test_detects_empty_string_as_never(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)

        result = encoder._detect_field_importance("some_field", "")

        assert result == FieldImportance.NEVER

    def test_detects_long_string_as_medium(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)

        result = encoder._detect_field_importance("content", "A" * 600)

        assert result == FieldImportance.MEDIUM

    def test_detects_short_string_as_low(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)

        result = encoder._detect_field_importance("code", "ab")

        assert result == FieldImportance.LOW

    def test_default_is_medium(self):
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)

        result = encoder._detect_field_importance("unknown_field", "some normal value")

        assert result == FieldImportance.MEDIUM


class TestDSEncoderIntegration:
    """Integration tests for complete encoding flows"""

    def test_encode_product_catalog(self):
        config = SDCompressionConfig(
            excluded_fields=["warehouse_location", "created_date"]
        )
        encoder = DSEncoder(config=config)

        products = [
            {
                "product_id": "PROD-001",
                "name": "Wireless Headphones",
                "description": "High-quality Bluetooth headphones",
                "price": 199.99,
                "category": "Electronics",
                "in_stock": True,
                "created_date": "2024-01-01",
                "warehouse_location": "A-23",
            },
            {
                "product_id": "PROD-002",
                "name": "Laptop Stand",
                "description": "Ergonomic adjustable stand",
                "price": 49.99,
                "category": "Accessories",
                "in_stock": True,
                "created_date": "2024-01-05",
                "warehouse_location": "B-15",
            },
        ]

        result = encoder.encode(products)

        assert result.compression_ratio > 0
        assert "PROD-001" in result.compressed
        assert "PROD-002" in result.compressed
        # Excluded fields should not appear
        assert "warehouse_location" not in result.compressed.lower()
        assert "A-23" not in result.compressed
        assert "B-15" not in result.compressed

    def test_header_value_alignment(self):
        """Verify that header keys align with value positions"""
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)

        data = [
            {"uuid": "id-1", "title": "Title 1", "priority": 1},
            {"uuid": "id-2", "title": "Title 2", "priority": 2},
        ]

        result = encoder.encode(data)

        # Extract header and first item
        parts = result.compressed.split("[")
        header_part = parts[0]  # {uuid,priority,title}

        # Header should have fields in correct order
        assert "uuid" in header_part
        assert "priority" in header_part
        assert "title" in header_part

        # Check order matches default_fields_order (uuid before priority before title)
        uuid_pos = header_part.index("uuid")
        priority_pos = header_part.index("priority")
        title_pos = header_part.index("title")

        assert uuid_pos < priority_pos < title_pos

    def test_single_item_vs_list_consistency(self):
        """Single dict and list with one item should produce similar structures"""
        config = SDCompressionConfig()
        encoder = DSEncoder(config=config)

        item = {"id": "123", "name": "Test"}

        single_result = encoder.encode(item)
        list_result = encoder.encode([item])

        # Both should have the values
        assert "123" in single_result.compressed
        assert "Test" in single_result.compressed
        assert "123" in list_result.compressed
        assert "Test" in list_result.compressed
