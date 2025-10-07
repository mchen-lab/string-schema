# String-Schema Enhancement: Defaults and Descriptions

## Summary

Successfully enhanced string-schema to support default values and field descriptions using intuitive syntax:

- **Default values**: `field:type=value`
- **Descriptions**: `field:type | description`
- **Combined**: `field:type(constraints)?=default | description`

## New Syntax

### Default Values

```python
# Boolean defaults
active:bool=true
deleted:bool=false

# Numeric defaults
count:int=0
price:number=9.99

# String defaults
status:string=pending
name:string="John Doe"

# Null defaults
email:string?=null

# With constraints
age:int(0,120)=18
limit:int(1,1000)=100
```

### Descriptions

```python
# Simple descriptions
name:string | User's full name
age:int | User's age in years
email:email | Contact email address

# With constraints
age:int(0,120) | User's age in years
name:string(min=1,max=100) | User's full name
```

### Combined Syntax

```python
# All features together
name:string(min=1,max=100) | User's full name
age:int(0,120)=18 | User's age in years
active:bool=true | Whether the account is active
email:string? | Optional email address
count:int(1,1000)=1 | Number of items to process
```

## Implementation Details

### Changes Made

1. **Helper Functions** (`string_parser.py`):
   - `_split_on_equals_outside_parens()` - Splits on first `=` outside parentheses
   - `_parse_default_value()` - Parses default values (bool, int, float, string, null)

2. **Field Parsing** (`string_parser.py`):
   - Modified `_parse_single_field_with_nesting()` to extract:
     1. Description (after ` |`)
     2. Optional marker (`?`)
     3. Default value (after `=`)
   - Proper handling of `string?=null` syntax

3. **Sentinel Value** (`fields.py`):
   - Added `_NO_DEFAULT` sentinel to distinguish "no default" from "default is None"
   - Added `has_default` flag to `SimpleField`

4. **JSON Schema Generation** (`builders.py`, `string_parser.py`):
   - Updated to use `field.has_default` instead of `field.default is not None`
   - Ensures `null` defaults are properly included in JSON Schema

5. **Pydantic Integration** (`pydantic.py`):
   - Updated to use `field.has_default` for proper default handling

## Test Results

### New Tests
- **27 new tests** in `tests/test_defaults_descriptions.py`
- All tests passing ✅

### Backward Compatibility
- **171 existing tests** in string-schema - All passing ✅
- **35 tests** in simple-sqlalchemy - All passing ✅
- **Zero breaking changes** ✅

## Examples

### Worker Parameters (Real-World Use Case)

```python
from string_schema import parse_string_schema, validate_to_dict

# Define worker parameters
schema_str = """
    enable_cleanup:bool=true | Enable article cleanup step,
    enable_cat_tag:bool=true | Enable category and tag assignment,
    enable_create_summary:bool=true | Enable summary generation,
    max_articles_per_iteration:int(1,1000)=1 | Maximum articles to process,
    model_name:string? | LLM model to use (optional)
"""

# Use defaults
params = {}
result = validate_to_dict(params, schema_str)
# Result: {
#   "enable_cleanup": true,
#   "enable_cat_tag": true,
#   "enable_create_summary": true,
#   "max_articles_per_iteration": 1,
#   "model_name": null
# }

# Override some defaults
params = {
    "enable_cleanup": False,
    "max_articles_per_iteration": 10,
    "model_name": "openrouter:google/gemini-2.5-flash-lite"
}
result = validate_to_dict(params, schema_str)
# Result: {
#   "enable_cleanup": false,
#   "enable_cat_tag": true,
#   "enable_create_summary": true,
#   "max_articles_per_iteration": 10,
#   "model_name": "openrouter:google/gemini-2.5-flash-lite"
# }
```

### Generated JSON Schema

The enhanced syntax generates standard JSON Schema with `default` and `description` fields:

```json
{
  "type": "object",
  "properties": {
    "enable_cleanup": {
      "type": "boolean",
      "default": true,
      "description": "Enable article cleanup step"
    },
    "max_articles_per_iteration": {
      "type": "integer",
      "default": 1,
      "minimum": 1,
      "maximum": 1000,
      "description": "Maximum articles to process"
    }
  }
}
```

## Benefits

1. **Concise Syntax**: Much shorter than Pydantic or full JSON Schema
2. **Self-Documenting**: Descriptions inline with field definitions
3. **Type-Safe**: Validation and type conversion built-in
4. **Standard Output**: Generates standard JSON Schema
5. **Backward Compatible**: All existing code continues to work
6. **Perfect for Configuration**: Ideal for worker parameters, API schemas, etc.

## Comparison

### Before (Pydantic)
```python
class Params(BaseModel):
    enable_cleanup: bool = Field(
        default=True,
        description="Enable article cleanup step"
    )
    max_articles: int = Field(
        default=1,
        ge=1,
        le=1000,
        description="Max articles to process"
    )
```

### After (Enhanced String-Schema)
```python
PARAMS = """
enable_cleanup:bool=true | Enable article cleanup step,
max_articles:int(1,1000)=1 | Max articles to process
"""
```

**Result**: ~70% less code, same functionality!

## Next Steps

This enhancement enables:

1. **Service Parameter Definitions**: Define worker/service parameters concisely
2. **Frontend Schema Generation**: Auto-generate UI forms from schemas
3. **API Documentation**: Self-documenting API parameters
4. **Configuration Management**: Type-safe configuration with defaults

## Files Modified

- `string_schema/core/fields.py` - Added sentinel value and `has_default` flag
- `string_schema/core/builders.py` - Updated JSON schema generation
- `string_schema/parsing/string_parser.py` - Added parsing for defaults/descriptions
- `string_schema/integrations/pydantic.py` - Updated Pydantic integration
- `docs/string-syntax.md` - Added documentation
- `tests/test_defaults_descriptions.py` - Added comprehensive tests
- `examples/defaults_descriptions_demo.py` - Added demo

## Conclusion

The enhancement is **complete**, **tested**, and **backward compatible**. It provides a powerful, concise syntax for defining schemas with defaults and descriptions, making string-schema even more suitable for configuration management and API schema definitions.

**Status**: ✅ Ready for use in news project worker parameters!

