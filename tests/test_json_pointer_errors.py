import pytest

from marshmallow import Schema, fields, validate
from marshmallow.exceptions import ValidationError


class TestJSONPointerErrorFormat:
    def test_invalid_error_format_raises_value_error(self):
        class UserSchema(Schema):
            name = fields.String(required=True)

        schema = UserSchema()
        with pytest.raises(ValueError, match="Invalid error_format"):
            schema.load({}, error_format="invalid")

    def test_none_error_format_raises_value_error(self):
        class UserSchema(Schema):
            name = fields.String(required=True)

        schema = UserSchema()
        with pytest.raises(ValueError, match="Invalid error_format"):
            schema.load({}, error_format=None)

    def test_error_format_validates_even_with_valid_data(self):
        class UserSchema(Schema):
            name = fields.String(required=True)

        schema = UserSchema()
        with pytest.raises(ValueError, match="Invalid error_format"):
            schema.load({"name": "John"}, error_format="bad-format")

    def test_simple_field_error_json_pointer(self):
        class UserSchema(Schema):
            email = fields.Email(required=True)

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"email": "invalid"}, error_format="json-pointer")

        assert "/email" in exc_info.value.messages
        assert "valid email" in str(exc_info.value.messages["/email"][0]).lower()

    def test_missing_required_field_json_pointer(self):
        class UserSchema(Schema):
            name = fields.String(required=True)
            email = fields.Email(required=True)

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({}, error_format="json-pointer")

        assert "/name" in exc_info.value.messages
        assert "/email" in exc_info.value.messages

    def test_nested_schema_error_json_pointer(self):
        class AddressSchema(Schema):
            street = fields.String(required=True)
            city = fields.String(required=True)

        class UserSchema(Schema):
            name = fields.String(required=True)
            address = fields.Nested(AddressSchema)

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load(
                {"name": "John", "address": {"city": "NYC"}},
                error_format="json-pointer",
            )

        assert "/address/street" in exc_info.value.messages

    def test_list_field_error_json_pointer(self):
        class UserSchema(Schema):
            tags = fields.List(fields.Integer())

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"tags": [1, "invalid", 3]}, error_format="json-pointer")

        assert "/tags/1" in exc_info.value.messages

    def test_nested_list_error_json_pointer(self):
        class ItemSchema(Schema):
            name = fields.String(required=True)
            price = fields.Float(required=True)

        class OrderSchema(Schema):
            items = fields.List(fields.Nested(ItemSchema))

        schema = OrderSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load(
                {
                    "items": [
                        {"name": "Item 1", "price": 10.0},
                        {"name": "Item 2"},
                        {"price": 30.0},
                    ]
                },
                error_format="json-pointer",
            )

        assert "/items/1/price" in exc_info.value.messages
        assert "/items/2/name" in exc_info.value.messages

    def test_many_true_error_json_pointer(self):
        class UserSchema(Schema):
            name = fields.String(required=True)
            age = fields.Integer()

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load(
                [
                    {"name": "John", "age": 30},
                    {"name": "Jane", "age": "invalid"},
                    {"age": 25},
                ],
                many=True,
                error_format="json-pointer",
            )

        assert "/1/age" in exc_info.value.messages
        assert "/2/name" in exc_info.value.messages

    def test_field_with_tilde_escaping(self):
        DataSchema = Schema.from_dict({"a~b": fields.String(required=True)})

        schema = DataSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({}, error_format="json-pointer")

        assert "/a~0b" in exc_info.value.messages

    def test_field_with_slash_escaping(self):
        DataSchema = Schema.from_dict({"first/name": fields.String(required=True)})

        schema = DataSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({}, error_format="json-pointer")

        assert "/first~1name" in exc_info.value.messages

    def test_field_with_tilde_and_slash_escaping(self):
        DataSchema = Schema.from_dict({"a~/b": fields.String(required=True)})

        schema = DataSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({}, error_format="json-pointer")

        assert "/a~0~1b" in exc_info.value.messages

    def test_schema_level_error_json_pointer(self):
        from marshmallow import validates_schema

        class UserSchema(Schema):
            name = fields.String(required=True)

            @validates_schema
            def validate_schema(self, data, **kwargs):
                raise ValidationError("Schema level error")

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"name": "John"}, error_format="json-pointer")

        assert "/_schema" in exc_info.value.messages

    def test_nested_schema_level_error_json_pointer(self):
        from marshmallow import validates_schema

        class AddressSchema(Schema):
            street = fields.String()

            @validates_schema
            def validate_address(self, data, **kwargs):
                raise ValidationError("Invalid address")

        class UserSchema(Schema):
            address = fields.Nested(AddressSchema)

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"address": {"street": "Main St"}}, error_format="json-pointer")

        assert "/address/_schema" in exc_info.value.messages

    def test_data_key_uses_external_name(self):
        class UserSchema(Schema):
            user_name = fields.String(required=True, data_key="userName")

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({}, error_format="json-pointer")

        assert "/userName" in exc_info.value.messages

    def test_validate_method_with_json_pointer(self):
        class UserSchema(Schema):
            email = fields.Email(required=True)

        schema = UserSchema()
        errors = schema.validate({"email": "invalid"}, error_format="json-pointer")

        assert "/email" in errors

    def test_loads_method_with_json_pointer(self):
        class UserSchema(Schema):
            email = fields.Email(required=True)

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.loads('{"email": "invalid"}', error_format="json-pointer")

        assert "/email" in exc_info.value.messages

    def test_nested_default_behavior_unchanged(self):
        class UserSchema(Schema):
            email = fields.Email(required=True)

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"email": "invalid"})

        assert "email" in exc_info.value.messages
        assert "/email" not in exc_info.value.messages

    def test_nested_error_format_explicit(self):
        class UserSchema(Schema):
            email = fields.Email(required=True)

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"email": "invalid"}, error_format="nested")

        assert "email" in exc_info.value.messages
        assert "/email" not in exc_info.value.messages

    def test_multiple_errors_same_field(self):
        class UserSchema(Schema):
            age = fields.Integer(
                required=True, validate=[validate.Range(min=0, max=120)]
            )

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"age": "not_a_number"}, error_format="json-pointer")

        assert "/age" in exc_info.value.messages
        assert isinstance(exc_info.value.messages["/age"], list)

    def test_deeply_nested_structure(self):
        class ItemSchema(Schema):
            price = fields.Float(required=True)

        class OrderSchema(Schema):
            items = fields.List(fields.Nested(ItemSchema))

        class UserSchema(Schema):
            orders = fields.List(fields.Nested(OrderSchema))

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load(
                {"orders": [{"items": [{"price": 10.0}]}, {"items": [{}]}]},
                error_format="json-pointer",
            )

        assert "/orders/1/items/0/price" in exc_info.value.messages

    def test_tuple_field_error_json_pointer(self):
        class DataSchema(Schema):
            coordinates = fields.Tuple([fields.Float(), fields.Float()])

        schema = DataSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"coordinates": (1.0, "invalid")}, error_format="json-pointer")

        assert "/coordinates/1" in exc_info.value.messages

    def test_dict_field_error_json_pointer(self):
        class DataSchema(Schema):
            metadata = fields.Dict(keys=fields.String(), values=fields.Integer())

        schema = DataSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load(
                {"metadata": {"key1": 1, "key2": "invalid"}}, error_format="json-pointer"
            )

        assert "/metadata/key2/value" in exc_info.value.messages

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
            email = fields.Email(required=True)

        schema = UserSchema()
        input_data = {"email": "invalid"}
        with pytest.raises(ValidationError) as exc_info:
            schema.load(input_data, error_format="json-pointer")

        assert exc_info.value.data == input_data

    def test_error_format_with_partial(self):
        class UserSchema(Schema):
            name = fields.String(required=True)
            email = fields.Email(required=True)

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load(
                {"email": "invalid"}, partial=True, error_format="json-pointer"
            )

        assert "/email" in exc_info.value.messages
        assert "/name" not in exc_info.value.messages

    def test_error_format_with_unknown_exclude(self):
        from marshmallow import EXCLUDE

        class UserSchema(Schema):
            name = fields.String(required=True)

        schema = UserSchema()
        result = schema.load(
            {"name": "John", "extra": "field"}, unknown=EXCLUDE, error_format="json-pointer"
        )

        assert result == {"name": "John"}

    def test_multiple_validation_errors_preserved_order(self):
        class UserSchema(Schema):
            age = fields.Integer(
                validate=[
                    validate.Range(min=0, max=120, error="Age must be 0-120"),
                    validate.Range(min=18, max=100, error="Age must be 18-100"),
                ]
            )

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"age": -5}, error_format="json-pointer")

        assert "/age" in exc_info.value.messages
        errors = exc_info.value.messages["/age"]
        assert len(errors) == 2
        assert "0-120" in errors[0]
        assert "18-100" in errors[1]

    def test_combination_of_field_types(self):
        class AddressSchema(Schema):
            street = fields.String(required=True)

        class UserSchema(Schema):
            addresses = fields.List(fields.Nested(AddressSchema))
            metadata = fields.Dict(keys=fields.String(), values=fields.Integer())
            coordinates = fields.Tuple([fields.Float(), fields.Float()])

        schema = UserSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load(
                {
                    "addresses": [{}, {"street": "Main St"}],
                    "metadata": {"key1": "invalid"},
                    "coordinates": (1.0, "invalid"),
                },
                error_format="json-pointer",
            )

        assert "/addresses/0/street" in exc_info.value.messages
        assert "/metadata/key1/value" in exc_info.value.messages
        assert "/coordinates/1" in exc_info.value.messages
