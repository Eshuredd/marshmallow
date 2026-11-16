"""Tests for JSON Pointer error format requirements from problem statement."""

import pytest

from marshmallow import Schema, fields, validate, validates_schema
from marshmallow.exceptions import ValidationError


class TestRequirement1APIChanges:
    """Tests for requirement 1: API changes."""

    def test_load_accepts_error_format_nested(self):
        class UserSchema(Schema):
            name = fields.String(required=True)

        schema = UserSchema()
        result = schema.load({"name": "John"}, error_format="nested")
        assert result == {"name": "John"}

    def test_load_accepts_error_format_json_pointer(self):
        class UserSchema(Schema):
            name = fields.String(required=True)

        schema = UserSchema()
        result = schema.load({"name": "John"}, error_format="json-pointer")
        assert result == {"name": "John"}

    def test_loads_accepts_error_format_nested(self):
        class UserSchema(Schema):
            name = fields.String(required=True)

        schema = UserSchema()
        result = schema.loads('{"name": "John"}', error_format="nested")
        assert result == {"name": "John"}

    def test_loads_accepts_error_format_json_pointer(self):
        class UserSchema(Schema):
            name = fields.String(required=True)

        schema = UserSchema()
        result = schema.loads('{"name": "John"}', error_format="json-pointer")
        assert result == {"name": "John"}

    def test_validate_accepts_error_format_nested(self):
        class UserSchema(Schema):
            name = fields.String(required=True)

        schema = UserSchema()
        errors = schema.validate({"name": "John"}, error_format="nested")
        assert errors == {}

    def test_validate_accepts_error_format_json_pointer(self):
        class UserSchema(Schema):
            name = fields.String(required=True)

        schema = UserSchema()
        errors = schema.validate({"name": "John"}, error_format="json-pointer")
        assert errors == {}

    def test_nested_is_default_for_load(self):
        class UserSchema(Schema):
            email = fields.Email(required=True)

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"email": "invalid"})
        
        assert "email" in exc_info.value.messages
        assert "/email" not in exc_info.value.messages

    def test_nested_is_default_for_loads(self):
        class UserSchema(Schema):
            email = fields.Email(required=True)

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.loads('{"email": "invalid"}')
        
        assert "email" in exc_info.value.messages
        assert "/email" not in exc_info.value.messages

    def test_nested_is_default_for_validate(self):
        class UserSchema(Schema):
            email = fields.Email(required=True)

        schema = UserSchema()
        errors = schema.validate({"email": "invalid"})
        assert "email" in errors
        assert "/email" not in errors

    def test_invalid_error_format_raises_value_error_on_valid_data(self):
        class UserSchema(Schema):
            name = fields.String()

        schema = UserSchema()
        with pytest.raises(ValueError, match="Invalid error_format"):
            schema.load({"name": "valid"}, error_format="invalid-format")

    def test_none_error_format_raises_value_error_on_valid_data(self):
        class UserSchema(Schema):
            name = fields.String()

        schema = UserSchema()
        with pytest.raises(ValueError, match="Invalid error_format"):
            schema.load({"name": "valid"}, error_format=None)

    def test_formatted_errors_in_validation_error_messages(self):
        class UserSchema(Schema):
            email = fields.Email(required=True)

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"email": "invalid"}, error_format="json-pointer")

        assert "/email" in exc_info.value.messages


class TestRequirement2ErrorPaths:
    """Tests for requirement 2: Error paths."""

    def test_paths_start_with_slash(self):
        class UserSchema(Schema):
            name = fields.String(required=True)

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({}, error_format="json-pointer")

        for key in exc_info.value.messages.keys():
            assert key.startswith("/")

    def test_nested_field_path(self):
        class AddressSchema(Schema):
            street = fields.String(required=True)

        class UserSchema(Schema):
            address = fields.Nested(AddressSchema)

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"address": {}}, error_format="json-pointer")

        assert "/address/street" in exc_info.value.messages

    def test_list_index_path(self):
        class UserSchema(Schema):
            tags = fields.List(fields.Integer())

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"tags": [1, "invalid"]}, error_format="json-pointer")

        assert "/tags/1" in exc_info.value.messages

    def test_tuple_index_path(self):
        class DataSchema(Schema):
            coords = fields.Tuple([fields.Float(), fields.Float()])

        schema = DataSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"coords": [1.0, "invalid"]}, error_format="json-pointer")

        assert "/coords/1" in exc_info.value.messages

    def test_many_true_uses_zero_based_index(self):
        class UserSchema(Schema):
            age = fields.Integer(required=True)

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load([{"age": 25}, {}], many=True, error_format="json-pointer")

        assert "/1/age" in exc_info.value.messages

    def test_deeply_nested_path(self):
        class ItemSchema(Schema):
            price = fields.Float(required=True)

        class OrderSchema(Schema):
            items = fields.List(fields.Nested(ItemSchema))

        class UserSchema(Schema):
            orders = fields.List(fields.Nested(OrderSchema))

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load(
                {"orders": [{"items": [{}]}]},
                error_format="json-pointer",
            )

        assert "/orders/0/items/0/price" in exc_info.value.messages

    def test_error_values_are_lists(self):
        class UserSchema(Schema):
            email = fields.Email(required=True)

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"email": "invalid"}, error_format="json-pointer")

        for value in exc_info.value.messages.values():
            assert isinstance(value, list)

    def test_multiple_errors_at_same_location_preserved(self):
        class UserSchema(Schema):
            name = fields.String(required=True)
            age = fields.Integer(required=True)

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({}, error_format="json-pointer")

        assert "/name" in exc_info.value.messages
        assert "/age" in exc_info.value.messages
        assert isinstance(exc_info.value.messages["/name"], list)
        assert isinstance(exc_info.value.messages["/age"], list)

    def test_multiple_errors_original_order_preserved(self):
        class ItemSchema(Schema):
            name = fields.String(required=True)
            price = fields.Float(required=True)

        class OrderSchema(Schema):
            items = fields.List(fields.Nested(ItemSchema))

        schema = OrderSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load(
                {"items": [{}, {"name": "X"}]},
                error_format="json-pointer",
            )

        assert "/items/0/name" in exc_info.value.messages
        assert "/items/0/price" in exc_info.value.messages
        assert "/items/1/price" in exc_info.value.messages


class TestRequirement3EscapingFieldNames:
    """Tests for requirement 3: Escaping field names."""

    def test_tilde_becomes_tilde_zero(self):
        TestSchema = Schema.from_dict({"field~name": fields.String(required=True)})
        schema = TestSchema()
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load({}, error_format="json-pointer")

        assert "/field~0name" in exc_info.value.messages

    def test_slash_becomes_tilde_one(self):
        TestSchema = Schema.from_dict({"field/name": fields.String(required=True)})
        schema = TestSchema()
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load({}, error_format="json-pointer")

        assert "/field~1name" in exc_info.value.messages

    def test_tilde_then_slash_escaping_order(self):
        TestSchema = Schema.from_dict({"a~/b": fields.String(required=True)})
        schema = TestSchema()
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load({}, error_format="json-pointer")

        assert "/a~0~1b" in exc_info.value.messages

    def test_data_key_used_in_path(self):
        class UserSchema(Schema):
            user_name = fields.String(required=True, data_key="userName")

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({}, error_format="json-pointer")

        assert "/userName" in exc_info.value.messages
        assert "/user_name" not in exc_info.value.messages


class TestRequirement4SchemaLevelErrors:
    """Tests for requirement 4: Schema-level errors."""

    def test_root_schema_error_uses_schema_key(self):
        class UserSchema(Schema):
            name = fields.String()

            @validates_schema
            def validate_schema(self, data, **kwargs):
                raise ValidationError("Schema level error")

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"name": "John"}, error_format="json-pointer")

        assert "/_schema" in exc_info.value.messages

    def test_nested_schema_error(self):
        class AddressSchema(Schema):
            street = fields.String()

            @validates_schema
            def validate_address(self, data, **kwargs):
                raise ValidationError("Invalid address")

        class UserSchema(Schema):
            address = fields.Nested(AddressSchema)

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load(
                {"address": {"street": "Main"}}, error_format="json-pointer"
            )

        assert "/address/_schema" in exc_info.value.messages

    def test_schema_error_in_collection_item(self):
        class ItemSchema(Schema):
            name = fields.String()

            @validates_schema
            def validate_item(self, data, **kwargs):
                raise ValidationError("Invalid item")

        class OrderSchema(Schema):
            items = fields.List(fields.Nested(ItemSchema))

        schema = OrderSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load(
                {"items": [{"name": "A"}, {"name": "B"}]},
                error_format="json-pointer",
            )

        assert "/items/0/_schema" in exc_info.value.messages
        assert "/items/1/_schema" in exc_info.value.messages

    def test_schema_validator_reporting_field_errors(self):
        class UserSchema(Schema):
            name = fields.String()
            age = fields.Integer()

            @validates_schema
            def validate_schema(self, data, **kwargs):
                raise ValidationError({"name": ["Custom name error"]})

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"name": "John", "age": 25}, error_format="json-pointer")

        assert "/name" in exc_info.value.messages
        assert "Custom name error" in exc_info.value.messages["/name"]


class TestRequirement5BackwardCompatibility:
    """Tests for requirement 5: Keep existing behavior unchanged."""

    def test_validation_error_valid_data_preserved(self):
        class UserSchema(Schema):
            name = fields.String()
            email = fields.Email(required=True)

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load(
                {"name": "John", "email": "invalid"}, error_format="json-pointer"
            )

        assert exc_info.value.valid_data == {"name": "John"}

    def test_validation_error_data_preserved(self):
        class UserSchema(Schema):
            email = fields.Email()

        schema = UserSchema()
        input_data = {"email": "invalid"}
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(input_data, error_format="json-pointer")

        assert exc_info.value.data == input_data

    def test_partial_works_with_json_pointer(self):
        class UserSchema(Schema):
            name = fields.String(required=True)
            email = fields.Email(required=True)

        schema = UserSchema()
        result = schema.load(
            {"name": "John"}, partial=True, error_format="json-pointer"
        )
        assert result == {"name": "John"}

    def test_unknown_exclude_works_with_json_pointer(self):
        from marshmallow import EXCLUDE

        class UserSchema(Schema):
            name = fields.String()

        schema = UserSchema()
        result = schema.load(
            {"name": "John", "extra": "field"},
            unknown=EXCLUDE,
            error_format="json-pointer",
        )
        assert result == {"name": "John"}
        assert "extra" not in result

    def test_many_works_with_json_pointer(self):
        class UserSchema(Schema):
            name = fields.String(required=True)

        schema = UserSchema()
        result = schema.load(
            [{"name": "John"}, {"name": "Jane"}],
            many=True,
            error_format="json-pointer",
        )
        assert len(result) == 2

    def test_data_key_works_with_json_pointer(self):
        class UserSchema(Schema):
            user_name = fields.String(required=True, data_key="userName")

        schema = UserSchema()
        result = schema.load({"userName": "john"}, error_format="json-pointer")
        assert result == {"user_name": "john"}

    def test_nested_default_unchanged(self):
        class UserSchema(Schema):
            email = fields.Email()

        schema = UserSchema()
        
        with pytest.raises(ValidationError) as exc_nested:
            schema.load({"email": "invalid"})
        
        with pytest.raises(ValidationError) as exc_explicit:
            schema.load({"email": "invalid"}, error_format="nested")

        assert exc_nested.value.messages == exc_explicit.value.messages

    def test_dump_not_affected(self):
        class UserSchema(Schema):
            name = fields.String()

        schema = UserSchema()
        result = schema.dump({"name": "John"})
        assert result == {"name": "John"}

    def test_dumps_not_affected(self):
        class UserSchema(Schema):
            name = fields.String()

        schema = UserSchema()
        result = schema.dumps({"name": "John"})
        assert '"name": "John"' in result
