# JSON Pointer Error Format - Quick Reference

## Basic Usage

```python
from marshmallow import Schema, fields, ValidationError

class UserSchema(Schema):
    email = fields.Email(required=True)

schema = UserSchema()

# Use error_format parameter
try:
    schema.load({"email": "invalid"}, error_format="json-pointer")
except ValidationError as err:
    print(err.messages)
    # Output: {"/email": ["Not a valid email address."]}
```

## Available Methods

All three deserialization/validation methods support `error_format`:

```python
# load()
schema.load(data, error_format="json-pointer")

# loads()
schema.loads(json_string, error_format="json-pointer")

# validate()
errors = schema.validate(data, error_format="json-pointer")
```

## Error Format Values

- `"nested"` (default) - Traditional nested dictionary format
- `"json-pointer"` - Flat dictionary with RFC 6901 JSON Pointer paths

Invalid values raise `ValueError`.

## Path Examples

| Validation Error | JSON Pointer Path |
|-----------------|-------------------|
| Root field | `/email` |
| Nested field | `/address/street` |
| List item | `/tags/1` |
| Nested list | `/orders/0/items/2/price` |
| Many=True | `/1/age` (second item) |
| Schema-level | `/_schema` |
| Nested schema-level | `/address/_schema` |

## Field Name Escaping

RFC 6901 requires escaping special characters:

```python
# Field name: "user/name"  → Path: "/user~1name"
# Field name: "meta~data"  → Path: "/meta~0data"
# Field name: "a~/b"       → Path: "/a~0~1b"
```

Escaping rules:
1. `~` becomes `~0`
2. `/` becomes `~1`

## data_key Handling

When a field uses `data_key`, the external name appears in the path:

```python
class UserSchema(Schema):
    user_name = fields.String(data_key="userName")

# Error path will be: "/userName" (not "/user_name")
```

## Complex Example

```python
from marshmallow import Schema, fields

class ItemSchema(Schema):
    name = fields.String(required=True)
    price = fields.Float(required=True)

class OrderSchema(Schema):
    items = fields.List(fields.Nested(ItemSchema))

schema = OrderSchema()
data = {
    "items": [
        {"name": "Widget", "price": 10.0},  # valid
        {"name": "Gadget"},                  # missing price
        {"price": 20.0}                      # missing name
    ]
}

try:
    schema.load(data, error_format="json-pointer")
except ValidationError as err:
    print(err.messages)
    # {
    #   "/items/1/price": ["Missing data for required field."],
    #   "/items/2/name": ["Missing data for required field."]
    # }
```

## Backward Compatibility

Existing code without `error_format` parameter continues to work unchanged:

```python
# This still works exactly as before
try:
    schema.load(invalid_data)
except ValidationError as err:
    # err.messages is in nested format (default)
    pass
```

## Common Use Cases

### 1. Frontend Form Validation
```python
# Map errors to form fields by ID
for path, messages in err.messages.items():
    field_id = path.replace("/", "_")  # "/user/email" → "user_email"
    display_error_on_field(field_id, messages[0])
```

### 2. API Error Responses
```python
@app.route("/api/users", methods=["POST"])
def create_user():
    try:
        user = UserSchema().load(request.json, error_format="json-pointer")
        return {"user": user}, 201
    except ValidationError as err:
        return {"errors": err.messages}, 400
```

### 3. Validation Only
```python
# Check for errors without raising exception
errors = schema.validate(data, error_format="json-pointer")
if errors:
    # Handle errors with JSON Pointer paths
    for path in errors:
        print(f"Error at {path}: {errors[path]}")
```

## Notes

- Error values are always lists (even with single error)
- Multiple errors at same location are preserved
- Works with all Marshmallow field types
- Compatible with partial=True, unknown=EXCLUDE, etc.
- Schema-level validators can still report field-specific errors
