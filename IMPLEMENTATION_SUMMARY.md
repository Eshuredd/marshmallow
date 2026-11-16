# JSON Pointer Error Format Implementation Summary

## Overview

Successfully implemented JSON Pointer (RFC 6901) support for validation errors in Marshmallow as specified in `problem.txt`. The implementation adds an optional `error_format` parameter to `Schema.load()`, `Schema.loads()`, and `Schema.validate()` methods while maintaining full backward compatibility.

## Changes Made

### 1. Core Implementation Files

#### `src/marshmallow/utils.py`
- Added `escape_json_pointer_segment()` function to escape field names according to RFC 6901 rules
- Added `errors_to_json_pointer()` function to recursively convert nested error dictionaries to flat JSON Pointer format
- Both functions handle the escaping rules: `~` → `~0`, `/` → `~1` (in that order)

#### `src/marshmallow/schema.py`
- Added `error_format` parameter (default: `"nested"`) to:
  - `Schema.load()`
  - `Schema.loads()`
  - `Schema.validate()`
  - `Schema._do_load()` (internal method)
- Added validation to ensure `error_format` is either `"nested"` or `"json-pointer"`, raising `ValueError` for invalid values
- Modified error handling in `_do_load()` to convert errors to JSON Pointer format when requested
- Imported `errors_to_json_pointer` utility function

### 2. Test Files

#### `tests/test_json_pointer_errors.py` (29 tests)
Comprehensive test coverage for the JSON Pointer feature:
- Invalid error format validation
- Simple field errors
- Nested schema errors
- List and collection errors
- Field name escaping (tilde and slash)
- Schema-level errors
- Data key handling
- Backward compatibility
- Multiple field types (Tuple, Dict, List, Nested)

#### `tests/test_json_pointer_requirements.py` (38 tests)
Tests organized by requirements from the problem statement:
- Requirement 1: API changes (12 tests)
- Requirement 2: Error paths (9 tests)
- Requirement 3: Escaping field names (4 tests)
- Requirement 4: Schema-level errors (4 tests)
- Requirement 5: Backward compatibility (9 tests)

### 3. Example Code

#### `examples/json_pointer_errors_example.py`
Demonstrates the feature with 5 practical examples:
1. Nested error format (default behavior)
2. JSON Pointer error format
3. Using validate() method with JSON Pointer
4. Field name escaping
5. Collection validation with many=True

## Features Implemented

### 1. API Changes ✓
- Added `error_format` keyword-only argument to `load()`, `loads()`, and `validate()`
- Supports `"nested"` (default) and `"json-pointer"` values
- Raises `ValueError` for invalid values, even with valid input data
- Formatted errors available through `ValidationError.messages`

### 2. Error Paths ✓
- All paths start with `/`
- Full path representation (e.g., `/users/1/age`)
- Each path maps to a list of error messages
- Supports:
  - `fields.Nested` (multiple levels)
  - `fields.List` (with primitives and nested schemas)
  - `fields.Tuple` (zero-based indexes)
  - `fields.Dict` (with key/value validation)
  - Schemas with `many=True`
  - All combinations of field types

### 3. Escaping Field Names ✓
- Implements RFC 6901 escaping rules:
  - `~` becomes `~0`
  - `/` becomes `~1`
  - Replacements happen in correct order
- Uses `data_key` in error paths when defined

### 4. Schema-Level Errors ✓
- Root schema errors: `/_schema`
- Nested schema errors: `/address/_schema`
- Collection item errors: `/users/1/_schema`
- Field-specific errors from schema validators point to their fields

### 5. Backward Compatibility ✓
- Existing behavior unchanged when `error_format` is omitted or set to `"nested"`
- No impact on:
  - Existing validation messages and ordering
  - Error aggregation
  - `ValidationError.valid_data` and `ValidationError.data`
  - `partial`, `unknown`, and `many` parameters
  - Field aliases via `data_key`
  - Schema inheritance
  - Validation hooks and `handle_error`
  - Serialization through `dump()` and `dumps()`

### 6. Implementation Quality ✓
- Uses existing validation and error-handling flow
- Works with custom fields and validators
- Original nested error data not modified
- 67 new tests covering all requirements
- All 1259 total tests passing

## Usage Examples

### Basic Usage

```python
from marshmallow import Schema, fields, ValidationError

class UserSchema(Schema):
    name = fields.String(required=True)
    email = fields.Email(required=True)

schema = UserSchema()

# Default nested format
try:
    schema.load({"name": "John"})
except ValidationError as err:
    print(err.messages)  # {"email": ["Missing data for required field."]}

# JSON Pointer format
try:
    schema.load({"name": "John"}, error_format="json-pointer")
except ValidationError as err:
    print(err.messages)  # {"/email": ["Missing data for required field."]}
```

### Nested Structures

```python
class AddressSchema(Schema):
    street = fields.String(required=True)
    city = fields.String(required=True)

class OrderSchema(Schema):
    items = fields.List(fields.Nested(ItemSchema))

# Errors like: "/orders/2/items/0/price" for deeply nested validation
```

### With validate() Method

```python
errors = schema.validate(data, error_format="json-pointer")
# Returns flat dictionary with JSON Pointer paths as keys
```

## Testing

All tests pass:
- 1259 total tests (1192 existing + 67 new)
- 29 tests in `test_json_pointer_errors.py`
- 38 tests in `test_json_pointer_requirements.py`
- Complete coverage of all requirements
- Backward compatibility verified

## Benefits

1. **API Compatibility**: Easy to map errors to form fields in web frameworks
2. **Standardized**: Uses RFC 6901 JSON Pointer specification
3. **Flexible**: Opt-in feature with sensible defaults
4. **Complete**: Works with all Marshmallow field types and patterns
5. **Safe**: Full backward compatibility, no breaking changes

## Files Modified

- `src/marshmallow/utils.py` - Added JSON Pointer utilities
- `src/marshmallow/schema.py` - Added error_format parameter and conversion logic

## Files Added

- `tests/test_json_pointer_errors.py` - Comprehensive feature tests
- `tests/test_json_pointer_requirements.py` - Requirements-based tests
- `examples/json_pointer_errors_example.py` - Usage examples
- `IMPLEMENTATION_SUMMARY.md` - This document
