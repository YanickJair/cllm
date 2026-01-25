import pytest

from clm_core.types import CLMOutput, FieldImportance, SDCompressionConfig


class TestFieldImportance:
    def test_enum_values(self):
        assert FieldImportance.CRITICAL.value == 1.0
        assert FieldImportance.HIGH.value == 0.8
        assert FieldImportance.MEDIUM.value == 0.5
        assert FieldImportance.LOW.value == 0.2
        assert FieldImportance.NEVER.value == 0.0

    def test_enum_members_count(self):
        assert len(FieldImportance) == 5

    def test_enum_comparison(self):
        assert FieldImportance.CRITICAL.value > FieldImportance.HIGH.value
        assert FieldImportance.HIGH.value > FieldImportance.MEDIUM.value
        assert FieldImportance.MEDIUM.value > FieldImportance.LOW.value
        assert FieldImportance.LOW.value > FieldImportance.NEVER.value


class TestCLMOutput:
    def test_create_with_string_original(self):
        output = CLMOutput(
            original="Hello world",
            component="test",
            compressed="Hlo wld",
            metadata={}
        )
        assert output.original == "Hello world"
        assert output.component == "test"
        assert output.compressed == "Hlo wld"
        assert output.metadata == {}

    def test_create_with_dict_original(self):
        output = CLMOutput(
            original={"id": "1", "name": "test"},
            component="ds_compression",
            compressed="[ID:1|N:test]",
            metadata={"field_count": 2}
        )
        assert output.original == {"id": "1", "name": "test"}

    def test_create_with_list_original(self):
        output = CLMOutput(
            original=[{"id": "1"}, {"id": "2"}],
            component="ds_compression",
            compressed="[1,2]",
            metadata={}
        )
        assert output.original == [{"id": "1"}, {"id": "2"}]

    def test_compression_ratio_positive(self):
        # Token estimation: ~4 chars per token
        output = CLMOutput(
            original="Hello world! This is a test.",  # 28 chars = ~7 tokens
            component="test",
            compressed="Hlo",  # 3 chars = ~1 token
            metadata={}
        )
        # n_tokens = 28//4 = 7, c_tokens = 3//4 = 1 (min 1)
        # (1 - 1/7) * 100 = 85.7
        assert output.n_tokens == 7
        assert output.c_tokens == 1
        assert output.compression_ratio == 85.7

    def test_compression_ratio_zero(self):
        output = CLMOutput(
            original="Hello",
            component="test",
            compressed="Hello",
            metadata={}
        )
        # Both have same token count, so 0% compression
        assert output.compression_ratio == 0.0

    def test_compression_ratio_negative_fallback(self):
        # When compressed would be larger than original, validator falls back to original
        output = CLMOutput(
            original="Hi",  # 2 chars = ~1 token (min 1)
            component="test",
            compressed="Hello world and more",  # 20 chars = ~5 tokens, but will be replaced
            metadata={}
        )
        # Validator replaces compressed with original when c_tokens > n_tokens
        assert output.n_tokens == 1
        assert output.c_tokens == 1  # Now same as original
        assert output.compressed == "Hi"  # Replaced with original
        assert output.compression_ratio == 0.0  # No compression, not negative

    def test_n_tokens_and_c_tokens_computed(self):
        output = CLMOutput(
            original="This is a sample text for testing tokens",  # 41 chars
            component="test",
            compressed="[TEST]",  # 6 chars
            metadata={}
        )
        assert output.n_tokens == 10  # 41 // 4
        assert output.c_tokens == 1   # 6 // 4 = 1 (min 1)


class TestSDCompressionConfig:
    def test_default_values(self):
        config = SDCompressionConfig()
        assert config.required_fields is None
        assert config.auto_detect is True
        assert config.importance_threshold == 0.5
        assert config.field_importance is None
        assert config.excluded_fields is None
        assert config.max_description_length == 200
        assert config.preserve_structure is True

    def test_default_simple_fields(self):
        config = SDCompressionConfig()
        assert "id" in config.simple_fields
        assert "title" in config.simple_fields
        assert "name" in config.simple_fields
        assert "type" in config.simple_fields
        assert "article_id" in config.simple_fields
        assert "product_id" in config.simple_fields

    def test_default_fields_order(self):
        config = SDCompressionConfig()
        expected_order = ["id", "uuid", "priority", "article_id", "product_id", "title", "name", "type"]
        assert config.default_fields_order == expected_order

    def test_default_fields_importance_contains_expected_keys(self):
        config = SDCompressionConfig()
        expected_keys = [
            "id", "external_id", "name", "title", "type", "category",
            "subcategory", "tags", "description", "details", "notes",
            "status", "priority", "severity", "resolution", "owner",
            "assignee", "department", "channel", "language", "source",
            "metadata", "created_at", "updated_at", "version"
        ]
        for key in expected_keys:
            assert key in config.default_fields_importance

    def test_default_fields_importance_critical_fields(self):
        config = SDCompressionConfig()
        assert config.default_fields_importance["id"] == FieldImportance.CRITICAL
        assert config.default_fields_importance["external_id"] == FieldImportance.CRITICAL
        assert config.default_fields_importance["status"] == FieldImportance.CRITICAL

    def test_default_fields_importance_high_fields(self):
        config = SDCompressionConfig()
        assert config.default_fields_importance["name"] == FieldImportance.HIGH
        assert config.default_fields_importance["title"] == FieldImportance.HIGH
        assert config.default_fields_importance["description"] == FieldImportance.HIGH

    def test_default_fields_importance_low_fields(self):
        config = SDCompressionConfig()
        assert config.default_fields_importance["notes"] == FieldImportance.LOW
        assert config.default_fields_importance["source"] == FieldImportance.LOW
        assert config.default_fields_importance["created_at"] == FieldImportance.LOW

    def test_custom_required_fields(self):
        config = SDCompressionConfig(required_fields=["id", "name", "custom_field"])
        assert config.required_fields == ["id", "name", "custom_field"]

    def test_custom_importance_threshold(self):
        config = SDCompressionConfig(importance_threshold=0.8)
        assert config.importance_threshold == 0.8

    def test_custom_excluded_fields(self):
        config = SDCompressionConfig(excluded_fields=["password", "secret"])
        assert config.excluded_fields == ["password", "secret"]

    def test_custom_max_description_length(self):
        config = SDCompressionConfig(max_description_length=500)
        assert config.max_description_length == 500


class TestSDCompressionConfigFieldImportanceValidator:
    def test_accepts_field_importance_enum_values(self):
        config = SDCompressionConfig(
            default_fields_importance={
                "id": FieldImportance.CRITICAL,
                "name": FieldImportance.HIGH,
            }
        )
        assert config.default_fields_importance["id"] == FieldImportance.CRITICAL
        assert config.default_fields_importance["name"] == FieldImportance.HIGH

    def test_converts_float_to_field_importance(self):
        config = SDCompressionConfig(
            default_fields_importance={
                "id": 1.0,
                "name": 0.8,
                "tags": 0.5,
                "notes": 0.2,
                "secret": 0.0,
            }
        )
        assert config.default_fields_importance["id"] == FieldImportance.CRITICAL
        assert config.default_fields_importance["name"] == FieldImportance.HIGH
        assert config.default_fields_importance["tags"] == FieldImportance.MEDIUM
        assert config.default_fields_importance["notes"] == FieldImportance.LOW
        assert config.default_fields_importance["secret"] == FieldImportance.NEVER

    def test_converts_int_to_field_importance(self):
        config = SDCompressionConfig(
            default_fields_importance={
                "id": 1,  # int instead of float
                "secret": 0,
            }
        )
        assert config.default_fields_importance["id"] == FieldImportance.CRITICAL
        assert config.default_fields_importance["secret"] == FieldImportance.NEVER

    def test_mixed_enum_and_float_values(self):
        config = SDCompressionConfig(
            default_fields_importance={
                "id": FieldImportance.CRITICAL,
                "name": 0.8,
                "tags": FieldImportance.MEDIUM,
                "notes": 0.2,
            }
        )
        assert config.default_fields_importance["id"] == FieldImportance.CRITICAL
        assert config.default_fields_importance["name"] == FieldImportance.HIGH
        assert config.default_fields_importance["tags"] == FieldImportance.MEDIUM
        assert config.default_fields_importance["notes"] == FieldImportance.LOW

    def test_invalid_float_value_raises_error(self):
        with pytest.raises(ValueError, match="No FieldImportance enum matches value"):
            SDCompressionConfig(
                default_fields_importance={
                    "id": 0.99,  # Not a valid FieldImportance value
                }
            )

    def test_invalid_float_value_negative_raises_error(self):
        with pytest.raises(ValueError, match="No FieldImportance enum matches value"):
            SDCompressionConfig(
                default_fields_importance={
                    "id": -0.5,
                }
            )

    def test_all_valid_float_values(self):
        valid_values = [1.0, 0.8, 0.5, 0.2, 0.0]
        expected_enums = [
            FieldImportance.CRITICAL,
            FieldImportance.HIGH,
            FieldImportance.MEDIUM,
            FieldImportance.LOW,
            FieldImportance.NEVER,
        ]
        fields = {f"field_{i}": v for i, v in enumerate(valid_values)}
        config = SDCompressionConfig(default_fields_importance=fields)
        for i, expected in enumerate(expected_enums):
            assert config.default_fields_importance[f"field_{i}"] == expected

    def test_empty_dict_accepted(self):
        config = SDCompressionConfig(default_fields_importance={})
        assert config.default_fields_importance == {}

    def test_enum_value_attribute_accessible(self):
        """Ensure .value can be accessed on stored enum values"""
        config = SDCompressionConfig(
            default_fields_importance={"id": 1.0, "name": 0.8}
        )
        assert config.default_fields_importance["id"].value == 1.0
        assert config.default_fields_importance["name"].value == 0.8


class TestSDCompressionConfigFieldImportanceSerializer:
    def test_model_dump_serializes_enums_to_floats(self):
        config = SDCompressionConfig(
            default_fields_importance={
                "id": FieldImportance.CRITICAL,
                "name": FieldImportance.HIGH,
            }
        )
        dump = config.model_dump()
        assert dump["default_fields_importance"]["id"] == 1.0
        assert dump["default_fields_importance"]["name"] == 0.8

    def test_model_dump_serializes_converted_floats(self):
        config = SDCompressionConfig(
            default_fields_importance={
                "id": 1.0,
                "tags": 0.5,
                "secret": 0.0,
            }
        )
        dump = config.model_dump()
        assert dump["default_fields_importance"]["id"] == 1.0
        assert dump["default_fields_importance"]["tags"] == 0.5
        assert dump["default_fields_importance"]["secret"] == 0.0

    def test_model_dump_default_fields_importance(self):
        config = SDCompressionConfig()
        dump = config.model_dump()
        # Check a few default values are serialized as floats
        assert dump["default_fields_importance"]["id"] == 1.0
        assert dump["default_fields_importance"]["name"] == 0.8
        assert dump["default_fields_importance"]["notes"] == 0.2

    def test_model_dump_empty_dict(self):
        config = SDCompressionConfig(default_fields_importance={})
        dump = config.model_dump()
        assert dump["default_fields_importance"] == {}
