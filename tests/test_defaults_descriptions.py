"""
Tests for enhanced string-schema syntax with defaults and descriptions.

Tests the new syntax:
    - field:type=default
    - field:type | description
    - field:type=default | description
"""

import pytest
from string_schema import parse_string_schema, validate_to_dict
from string_schema.parsing.string_parser import _parse_default_value, _split_on_equals_outside_parens


class TestHelperFunctions:
    """Test helper functions for parsing defaults"""
    
    def test_split_on_equals_outside_parens(self):
        """Test splitting on = outside parentheses"""
        # Simple case
        assert _split_on_equals_outside_parens("string=hello") == ["string", "hello"]
        
        # With constraints
        assert _split_on_equals_outside_parens("int(1,100)=5") == ["int(1,100)", "5"]
        
        # Multiple equals (only split on first)
        assert _split_on_equals_outside_parens("string=a=b") == ["string", "a=b"]
        
        # No equals
        assert _split_on_equals_outside_parens("string") == ["string"]
    
    def test_parse_default_value(self):
        """Test parsing default values from strings"""
        # Booleans
        assert _parse_default_value("true") == True
        assert _parse_default_value("false") == False
        assert _parse_default_value("True") == True
        assert _parse_default_value("FALSE") == False
        
        # Null
        assert _parse_default_value("null") is None
        assert _parse_default_value("none") is None
        assert _parse_default_value("None") is None
        
        # Numbers
        assert _parse_default_value("123") == 123
        assert _parse_default_value("45.67") == 45.67
        assert _parse_default_value("0") == 0
        
        # Strings with quotes
        assert _parse_default_value('"hello"') == "hello"
        assert _parse_default_value("'world'") == "world"
        
        # Strings without quotes
        assert _parse_default_value("hello") == "hello"


class TestBackwardCompatibility:
    """Ensure existing syntax still works"""
    
    def test_basic_types(self):
        """Test basic type definitions"""
        schema = parse_string_schema("id:int, name:string, active:bool")
        
        assert schema['type'] == 'object'
        assert 'id' in schema['properties']
        assert 'name' in schema['properties']
        assert 'active' in schema['properties']
        assert schema['properties']['id']['type'] == 'integer'
        assert schema['properties']['name']['type'] == 'string'
        assert schema['properties']['active']['type'] == 'boolean'
    
    def test_constraints(self):
        """Test type constraints"""
        schema = parse_string_schema("age:int(0,120), name:string(min=1,max=100)")
        
        assert schema['properties']['age']['minimum'] == 0
        assert schema['properties']['age']['maximum'] == 120
        assert schema['properties']['name']['minLength'] == 1
        assert schema['properties']['name']['maxLength'] == 100
    
    def test_optional_fields(self):
        """Test optional field marker"""
        schema = parse_string_schema("name:string, email:string?")
        
        assert 'name' in schema['required']
        assert 'email' not in schema['required']
    
    def test_special_types(self):
        """Test special types"""
        schema = parse_string_schema("email:email, website:url, created:datetime")
        
        assert schema['properties']['email']['format'] == 'email'
        assert schema['properties']['website']['format'] == 'uri'
        assert schema['properties']['created']['format'] == 'date-time'
    
    def test_enum_types(self):
        """Test enum types"""
        schema = parse_string_schema("status:enum(active,inactive,pending)")
        
        assert schema['properties']['status']['enum'] == ['active', 'inactive', 'pending']
    
    def test_union_types(self):
        """Test union types"""
        schema = parse_string_schema("value:string|int|null")
        
        assert 'anyOf' in schema['properties']['value']
        types = [t['type'] for t in schema['properties']['value']['anyOf']]
        assert 'string' in types
        assert 'integer' in types
        assert 'null' in types
    
    def test_arrays(self):
        """Test array types"""
        schema = parse_string_schema("tags:[string], items:[int]")
        
        assert schema['properties']['tags']['type'] == 'array'
        assert schema['properties']['tags']['items']['type'] == 'string'
        assert schema['properties']['items']['type'] == 'array'
        assert schema['properties']['items']['items']['type'] == 'integer'
    
    def test_nested_objects(self):
        """Test nested object types"""
        schema = parse_string_schema("user:{id:int, name:string}")
        
        assert schema['properties']['user']['type'] == 'object'
        assert 'id' in schema['properties']['user']['properties']
        assert 'name' in schema['properties']['user']['properties']


class TestDefaultValues:
    """Test new default value syntax"""
    
    def test_boolean_defaults(self):
        """Test boolean default values"""
        schema = parse_string_schema("active:bool=true, deleted:bool=false")
        
        assert schema['properties']['active']['default'] == True
        assert schema['properties']['deleted']['default'] == False
    
    def test_integer_defaults(self):
        """Test integer default values"""
        schema = parse_string_schema("count:int=0, limit:int=100")
        
        assert schema['properties']['count']['default'] == 0
        assert schema['properties']['limit']['default'] == 100
    
    def test_float_defaults(self):
        """Test float default values"""
        schema = parse_string_schema("price:number=9.99, rate:number=0.5")
        
        assert schema['properties']['price']['default'] == 9.99
        assert schema['properties']['rate']['default'] == 0.5
    
    def test_string_defaults(self):
        """Test string default values"""
        schema = parse_string_schema('status:string=active, name:string="John"')
        
        assert schema['properties']['status']['default'] == 'active'
        assert schema['properties']['name']['default'] == 'John'
    
    def test_null_defaults(self):
        """Test null default values"""
        schema = parse_string_schema("value:string?=null")
        
        assert schema['properties']['value']['default'] is None
    
    def test_defaults_with_constraints(self):
        """Test defaults combined with constraints"""
        schema = parse_string_schema("age:int(0,120)=18, count:int(1,1000)=1")
        
        assert schema['properties']['age']['default'] == 18
        assert schema['properties']['age']['minimum'] == 0
        assert schema['properties']['age']['maximum'] == 120
        assert schema['properties']['count']['default'] == 1
        assert schema['properties']['count']['minimum'] == 1
        assert schema['properties']['count']['maximum'] == 1000
    
    def test_enum_with_default(self):
        """Test enum with default value"""
        schema = parse_string_schema("status:enum(draft,published,archived)=draft")
        
        assert schema['properties']['status']['enum'] == ['draft', 'published', 'archived']
        assert schema['properties']['status']['default'] == 'draft'


class TestDescriptions:
    """Test new description syntax"""
    
    def test_simple_descriptions(self):
        """Test simple field descriptions"""
        schema = parse_string_schema("name:string | User name, age:int | User age")
        
        assert schema['properties']['name']['description'] == 'User name'
        assert schema['properties']['age']['description'] == 'User age'
    
    def test_descriptions_with_constraints(self):
        """Test descriptions with constraints"""
        schema = parse_string_schema("age:int(0,120) | User age in years")
        
        assert schema['properties']['age']['description'] == 'User age in years'
        assert schema['properties']['age']['minimum'] == 0
        assert schema['properties']['age']['maximum'] == 120
    
    def test_descriptions_with_optional(self):
        """Test descriptions with optional fields"""
        schema = parse_string_schema("email:string? | Optional email address")

        assert schema['properties']['email']['description'] == 'Optional email address'
        assert 'email' not in schema.get('required', [])
    
    def test_descriptions_with_special_types(self):
        """Test descriptions with special types"""
        schema = parse_string_schema("email:email | User email address")
        
        assert schema['properties']['email']['description'] == 'User email address'
        assert schema['properties']['email']['format'] == 'email'


class TestCombinedSyntax:
    """Test combined defaults and descriptions"""
    
    def test_default_and_description(self):
        """Test field with both default and description"""
        schema = parse_string_schema("active:bool=true | Whether user is active")
        
        assert schema['properties']['active']['default'] == True
        assert schema['properties']['active']['description'] == 'Whether user is active'
    
    def test_constraints_default_description(self):
        """Test field with constraints, default, and description"""
        schema = parse_string_schema("count:int(1,100)=1 | Number of items")
        
        assert schema['properties']['count']['minimum'] == 1
        assert schema['properties']['count']['maximum'] == 100
        assert schema['properties']['count']['default'] == 1
        assert schema['properties']['count']['description'] == 'Number of items'
    
    def test_optional_default_description(self):
        """Test optional field with default and description"""
        schema = parse_string_schema("email:string?=null | Optional email address")

        assert schema['properties']['email']['default'] is None
        assert schema['properties']['email']['description'] == 'Optional email address'
        assert 'email' not in schema.get('required', [])
    
    def test_multiple_fields_combined(self):
        """Test multiple fields with various combinations"""
        schema = parse_string_schema("""
            id:int | Unique identifier,
            name:string | User name,
            age:int(0,120)=18 | User age,
            active:bool=true | Account status,
            email:string? | Optional email
        """)
        
        # Check all fields exist
        assert 'id' in schema['properties']
        assert 'name' in schema['properties']
        assert 'age' in schema['properties']
        assert 'active' in schema['properties']
        assert 'email' in schema['properties']
        
        # Check descriptions
        assert schema['properties']['id']['description'] == 'Unique identifier'
        assert schema['properties']['name']['description'] == 'User name'
        assert schema['properties']['age']['description'] == 'User age'
        assert schema['properties']['active']['description'] == 'Account status'
        assert schema['properties']['email']['description'] == 'Optional email'
        
        # Check defaults
        assert schema['properties']['age']['default'] == 18
        assert schema['properties']['active']['default'] == True
        
        # Check constraints
        assert schema['properties']['age']['minimum'] == 0
        assert schema['properties']['age']['maximum'] == 120
        
        # Check required
        assert 'id' in schema['required']
        assert 'name' in schema['required']
        assert 'age' in schema['required']
        assert 'active' in schema['required']
        assert 'email' not in schema['required']


class TestValidation:
    """Test validation with defaults"""
    
    def test_validation_uses_defaults(self):
        """Test that validation applies default values"""
        schema_str = "name:string, active:bool=true, count:int=0"
        
        # Provide only name
        data = {"name": "John"}
        result = validate_to_dict(data, schema_str)
        
        assert result['name'] == 'John'
        assert result['active'] == True
        assert result['count'] == 0
    
    def test_validation_overrides_defaults(self):
        """Test that provided values override defaults"""
        schema_str = "name:string, active:bool=true, count:int=0"
        
        # Provide all values
        data = {"name": "John", "active": False, "count": 5}
        result = validate_to_dict(data, schema_str)
        
        assert result['name'] == 'John'
        assert result['active'] == False
        assert result['count'] == 5

