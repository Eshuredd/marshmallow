"""Example demonstrating JSON Pointer error format for validation errors.

This example shows how to use the error_format parameter to get validation
errors in JSON Pointer (RFC 6901) format instead of nested dictionaries.
"""

from marshmallow import Schema, fields, validate, ValidationError


class AddressSchema(Schema):
    street = fields.String(required=True)
    city = fields.String(required=True)
    zip_code = fields.String(validate=validate.Length(min=5, max=10))


class ItemSchema(Schema):
    name = fields.String(required=True)
    price = fields.Float(required=True, validate=validate.Range(min=0))
    quantity = fields.Integer(validate=validate.Range(min=1))


class OrderSchema(Schema):
    customer_name = fields.String(required=True, data_key="customerName")
    email = fields.Email(required=True)
    address = fields.Nested(AddressSchema, required=True)
    items = fields.List(fields.Nested(ItemSchema), required=True)


def example_nested_errors():
    """Example showing nested error format (default)."""
    print("=" * 70)
    print("EXAMPLE 1: Nested Error Format (Default)")
    print("=" * 70)
    
    schema = OrderSchema()
    invalid_data = {
        "customerName": "John Doe",
        "address": {
            "city": "New York"
        },
        "items": [
            {"name": "Widget", "price": -10.0},
            {"price": 25.0},
        ]
    }
    
    try:
        schema.load(invalid_data)
    except ValidationError as err:
        print("\nNested format errors:")
        import json
        print(json.dumps(err.messages, indent=2))
    
    print()


def example_json_pointer_errors():
    """Example showing JSON Pointer error format."""
    print("=" * 70)
    print("EXAMPLE 2: JSON Pointer Error Format")
    print("=" * 70)
    
    schema = OrderSchema()
    invalid_data = {
        "customerName": "John Doe",
        "address": {
            "city": "New York"
        },
        "items": [
            {"name": "Widget", "price": -10.0},
            {"price": 25.0},
        ]
    }
    
    try:
        schema.load(invalid_data, error_format="json-pointer")
    except ValidationError as err:
        print("\nJSON Pointer format errors:")
        import json
        print(json.dumps(err.messages, indent=2))
    
    print()


def example_validate_method():
    """Example using validate() method with JSON Pointer format."""
    print("=" * 70)
    print("EXAMPLE 3: Using validate() Method with JSON Pointer")
    print("=" * 70)
    
    schema = OrderSchema()
    invalid_data = {
        "customerName": "John Doe",
        "email": "not-an-email",
        "address": {
            "street": "123 Main St",
            "city": "New York"
        },
        "items": []
    }
    
    errors = schema.validate(invalid_data, error_format="json-pointer")
    
    print("\nValidation errors:")
    import json
    print(json.dumps(errors, indent=2))
    print()


def example_field_escaping():
    """Example showing field name escaping in JSON Pointer format."""
    print("=" * 70)
    print("EXAMPLE 4: Field Name Escaping (~ and /)")
    print("=" * 70)
    
    # Create a schema with field names containing special characters
    TestSchema = Schema.from_dict({
        "user/name": fields.String(required=True),
        "meta~data": fields.Integer(required=True),
    })
    
    schema = TestSchema()
    
    try:
        schema.load({}, error_format="json-pointer")
    except ValidationError as err:
        print("\nEscaped field names in JSON Pointer format:")
        import json
        print(json.dumps(err.messages, indent=2))
        print("\nNote:")
        print("  - 'user/name' becomes '/user~1name' (/ → ~1)")
        print("  - 'meta~data' becomes '/meta~0data' (~ → ~0)")
    
    print()


def example_many_true():
    """Example with many=True."""
    print("=" * 70)
    print("EXAMPLE 5: Collection Validation (many=True)")
    print("=" * 70)
    
    class UserSchema(Schema):
        name = fields.String(required=True)
        age = fields.Integer(validate=validate.Range(min=0, max=150))
    
    schema = UserSchema()
    users = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": -5},
        {"age": 25},
    ]
    
    try:
        schema.load(users, many=True, error_format="json-pointer")
    except ValidationError as err:
        print("\nCollection errors with JSON Pointer format:")
        import json
        print(json.dumps(err.messages, indent=2))
        print("\nNote: Array indices are 0-based")
    
    print()


if __name__ == "__main__":
    example_nested_errors()
    example_json_pointer_errors()
    example_validate_method()
    example_field_escaping()
    example_many_true()
    
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("""
The error_format parameter supports two values:
  - "nested" (default): Returns errors as nested dictionaries
  - "json-pointer": Returns errors as flat dictionaries with JSON Pointer paths

JSON Pointer format benefits:
  - Easy to map errors to specific form fields in UIs
  - Standardized path format (RFC 6901)
  - Flattened structure for simpler error handling
  - Works with all Marshmallow field types and validation scenarios

The feature is fully backward compatible - existing code continues
to work without any changes.
""")
