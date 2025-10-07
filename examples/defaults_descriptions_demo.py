"""
Demo: Enhanced String Schema with Defaults and Descriptions

This example demonstrates the new syntax for defining default values
and descriptions in string-schema.

New syntax:
    - field:type=default
    - field:type | description
    - field:type=default | description
"""

from string_schema import parse_string_schema, validate_to_dict
import json


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def demo_default_values():
    """Demonstrate default value syntax"""
    print_section("Default Values")
    
    # Define schema with defaults
    schema_str = """
        active:bool=true,
        count:int=0,
        status:string=pending,
        price:number=9.99
    """
    
    print("\nSchema definition:")
    print(schema_str)
    
    # Parse schema
    schema = parse_string_schema(schema_str)
    print("\nGenerated JSON Schema:")
    print(json.dumps(schema, indent=2))
    
    # Validate data with defaults
    print("\n--- Test 1: Empty data (uses all defaults) ---")
    data = {}
    result = validate_to_dict(data, schema_str)
    print(f"Input:  {data}")
    print(f"Output: {result}")
    
    print("\n--- Test 2: Partial data (some defaults) ---")
    data = {"count": 5}
    result = validate_to_dict(data, schema_str)
    print(f"Input:  {data}")
    print(f"Output: {result}")
    
    print("\n--- Test 3: Override defaults ---")
    data = {"active": False, "count": 10, "status": "completed", "price": 19.99}
    result = validate_to_dict(data, schema_str)
    print(f"Input:  {data}")
    print(f"Output: {result}")


def demo_descriptions():
    """Demonstrate description syntax"""
    print_section("Field Descriptions")
    
    # Define schema with descriptions
    schema_str = """
        name:string | User's full name,
        age:int | User's age in years,
        email:email | Contact email address,
        created:datetime | Account creation timestamp
    """
    
    print("\nSchema definition:")
    print(schema_str)
    
    # Parse schema
    schema = parse_string_schema(schema_str)
    print("\nGenerated JSON Schema (with descriptions):")
    print(json.dumps(schema, indent=2))


def demo_combined_syntax():
    """Demonstrate combined defaults and descriptions"""
    print_section("Combined: Defaults + Descriptions")
    
    # Define schema with both defaults and descriptions
    schema_str = """
        name:string | User's full name,
        age:int(0,120)=18 | User's age in years,
        active:bool=true | Whether the account is active,
        email:string? | Optional email address,
        count:int(1,1000)=1 | Number of items to process
    """
    
    print("\nSchema definition:")
    print(schema_str)
    
    # Parse schema
    schema = parse_string_schema(schema_str)
    print("\nGenerated JSON Schema:")
    print(json.dumps(schema, indent=2))
    
    # Validate data
    print("\n--- Test: Minimal data (uses defaults) ---")
    data = {"name": "John Doe"}
    result = validate_to_dict(data, schema_str)
    print(f"Input:  {data}")
    print(f"Output: {result}")


def demo_worker_parameters():
    """Demonstrate using enhanced syntax for worker parameters"""
    print_section("Real-World Example: Worker Parameters")
    
    # Define worker parameters schema
    schema_str = """
        enable_cleanup:bool=true | Enable article cleanup step,
        enable_cat_tag:bool=true | Enable category and tag assignment,
        enable_create_summary:bool=true | Enable summary generation,
        enable_embedding_generation:bool=true | Enable embedding generation,
        max_articles_per_iteration:int(1,1000)=1 | Maximum articles to process per run,
        processing_days_limit:int(1,365)=7 | Number of days to look back for articles,
        model_name:string? | LLM model to use (leave empty for default)
    """
    
    print("\nWorker Parameters Schema:")
    print(schema_str)
    
    # Parse schema
    schema = parse_string_schema(schema_str)
    print("\nGenerated JSON Schema:")
    print(json.dumps(schema, indent=2))
    
    # Example 1: Default configuration
    print("\n--- Example 1: Default configuration ---")
    params = {}
    result = validate_to_dict(params, schema_str)
    print(f"Input:  {params}")
    print(f"Output: {json.dumps(result, indent=2)}")
    
    # Example 2: Custom configuration
    print("\n--- Example 2: Custom configuration ---")
    params = {
        "enable_cleanup": False,
        "max_articles_per_iteration": 10,
        "model_name": "openrouter:google/gemini-2.5-flash-lite"
    }
    result = validate_to_dict(params, schema_str)
    print(f"Input:  {json.dumps(params, indent=2)}")
    print(f"Output: {json.dumps(result, indent=2)}")


def demo_null_defaults():
    """Demonstrate null default values"""
    print_section("Null Default Values")
    
    # Define schema with null defaults
    schema_str = """
        name:string,
        email:string?=null | Optional email (defaults to null),
        phone:string?=null | Optional phone (defaults to null),
        notes:string? | Optional notes (no default)
    """
    
    print("\nSchema definition:")
    print(schema_str)
    
    # Parse schema
    schema = parse_string_schema(schema_str)
    print("\nGenerated JSON Schema:")
    print(json.dumps(schema, indent=2))
    
    # Validate data
    print("\n--- Test: Minimal data ---")
    data = {"name": "John Doe"}
    result = validate_to_dict(data, schema_str)
    print(f"Input:  {data}")
    print(f"Output: {result}")


def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("  String Schema: Defaults and Descriptions Demo")
    print("="*60)
    
    demo_default_values()
    demo_descriptions()
    demo_combined_syntax()
    demo_worker_parameters()
    demo_null_defaults()
    
    print("\n" + "="*60)
    print("  Demo Complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

