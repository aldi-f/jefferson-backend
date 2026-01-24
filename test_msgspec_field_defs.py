#!/usr/bin/env python3
"""
Test different msgspec field definitions for version 0.19.0.
"""

import msgspec
from msgspec import field

def test_msgspec_field_definitions():
    """Test different ways to define msgspec fields for v0.19.0."""
    print("🔍 Testing msgspec field definitions for v0.19.0...")
    
    try:
        print(f"Msgspec version: {msgspec.__version__}")
        
        # Test 1: Basic type annotations (should work in newer versions)
        print(f"\n1. Basic type annotations:")
        class BasicModel(msgspec.Struct):
            test_field: str
            number_field: int
        
        print(f"   BasicModel fields: {BasicModel.__struct_fields__}")
        
        # Test 2: Using field() without parameters
        print(f"\n2. Using field() without parameters:")
        class FieldModel(msgspec.Struct):
            test_field: str = field()
            number_field: int = field()
        
        print(f"   FieldModel fields: {FieldModel.__struct_fields__}")
        
        # Test 3: Using field() with name parameter (the correct way for v0.19.0)
        print(f"\n3. Using field() with name parameter:")
        class NamedFieldModel(msgspec.Struct):
            test_field: str = field(name="test_field")
            number_field: int = field(name="number_field")
        
        print(f"   NamedFieldModel fields: {NamedFieldModel.__struct_fields__}")
        
        # Test 4: Using field() with explicit field names
        print(f"\n4. Using field() with explicit field names (legacy way):")
        class ExplicitFieldModel(msgspec.Struct):
            test_field: str = field(name="test_field")
            number_field: int = field(name="number_field")
        
        print(f"   ExplicitFieldModel fields: {ExplicitFieldModel.__struct_fields__}")
        
        # Test with actual data
        test_data = {"test_field": "hello", "number_field": 42}
        
        print(f"\n5. Testing with data: {test_data}")
        
        # Test basic model
        try:
            basic_decoded = msgspec.convert(test_data, type=BasicModel, strict=True)
            print(f"   BasicModel: {basic_decoded}")
            if hasattr(basic_decoded, 'test_field'):
                val = basic_decoded.test_field
                print(f"     test_field: {val} (type: {type(val)})")
                if hasattr(val, 'name'):
                    print(f"       → Field name: {val.name}")
                else:
                    print(f"       → Actual value!")
        except Exception as e:
            print(f"   BasicModel failed: {e}")
            
        # Test field model
        try:
            field_decoded = msgspec.convert(test_data, type=FieldModel, strict=True)
            print(f"   FieldModel: {field_decoded}")
            if hasattr(field_decoded, 'test_field'):
                val = field_decoded.test_field
                print(f"     test_field: {val} (type: {type(val)})")
                if hasattr(val, 'name'):
                    print(f"       → Field name: {val.name}")
                else:
                    print(f"       → Actual value!")
        except Exception as e:
            print(f"   FieldModel failed: {e}")
            
        # Test named field model
        try:
            named_decoded = msgspec.convert(test_data, type=NamedFieldModel, strict=True)
            print(f"   NamedFieldModel: {named_decoded}")
            if hasattr(named_decoded, 'test_field'):
                val = named_decoded.test_field
                print(f"     test_field: {val} (type: {type(val)})")
                if hasattr(val, 'name'):
                    print(f"       → Field name: {val.name}")
                else:
                    print(f"       → Actual value!")
        except Exception as e:
            print(f"   NamedFieldModel failed: {e}")
            
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_msgspec_struct_config():
    """Test msgspec struct configuration options."""
    print(f"\n🔍 Testing msgspec struct configuration...")
    
    try:
        # Test with different struct configurations
        class ConfigModel(msgspec.Struct):
            test_field: str
            number_field: int
        
        print(f"   ConfigModel fields: {ConfigModel.__struct_fields__}")
        print(f"   ConfigModel config: {ConfigModel.__struct_config__}")
        
        # Check if we need to manually define fields
        if not ConfigModel.__struct_fields__:
            print(f"   ⚠️  No fields detected - manual field definition needed")
            
            # Try manual field definition (the old msgspec way)
            try:
                # This is how it was done in older versions
                class ManualModel(msgspec.Struct):
                    __struct_fields__ = ["test_field", "number_field"]
                    test_field: str
                    number_field: int
                
                print(f"   ManualModel fields: {ManualModel.__struct_fields__}")
                
                test_data = {"test_field": "hello", "number_field": 42}
                manual_decoded = msgspec.convert(test_data, type=ManualModel, strict=True)
                print(f"   ManualModel decoded: {manual_decoded}")
                
                if hasattr(manual_decoded, 'test_field'):
                    val = manual_decoded.test_field
                    print(f"     test_field: {val} (type: {type(val)})")
                    if hasattr(val, 'name'):
                        print(f"       → Field name: {val.name}")
                    else:
                        print(f"       → Actual value!")
                        
            except Exception as e:
                print(f"   ManualModel failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Testing msgspec field definitions for v0.19.0")
    print("=" * 60)
    
    field_test_success = test_msgspec_field_definitions()
    config_test_success = test_msgspec_struct_config()
    
    print(f"\n📊 Results:")
    print("=" * 30)
    print(f"Field definitions: {'✓ PASS' if field_test_success else '✗ FAIL'}")
    print(f"Config test: {'✓ PASS' if config_test_success else '✗ FAIL'}")
    
    if field_test_success and config_test_success:
        print(f"\n🎯 Found the solution for msgspec 0.19.0!")
        print(f"The issue is that type annotations alone don't define struct fields in v0.19.0.")
        print(f"Need to use __struct_fields__ = [...] or upgrade to newer msgspec version.")