#!/usr/bin/env python3
"""
Research the correct way to define msgspec structs for version 0.19.0.
"""

import msgspec
from msgspec import field

def test_msgspec_0190_approaches():
    """Test different approaches for msgspec 0.19.0."""
    print("🔍 Researching msgspec 0.19.0 struct definition approaches...")
    
    try:
        print(f"Msgspec version: {msgspec.__version__}")
        
        # Approach 1: Using field() with name parameter (the documented way)
        print(f"\n1. Using field() with name parameter:")
        try:
            class NamedFieldModel(msgspec.Struct):
                test_field: str = field(name="test_field")
                number_field: int = field(name="number_field")
            
            print(f"   NamedFieldModel fields: {NamedFieldModel.__struct_fields__}")
            
            test_data = {"test_field": "hello", "number_field": 42}
            decoded = msgspec.convert(test_data, type=NamedFieldModel, strict=True)
            print(f"   Decoded: {decoded}")
            
            if hasattr(decoded, 'test_field'):
                val = decoded.test_field
                print(f"   test_field: {val} (type: {type(val)})")
                if hasattr(val, 'name'):
                    print(f"     → Field name: {val.name}")
                else:
                    print(f"     → Actual value!")
            else:
                print(f"   ❌ No test_field attribute")
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        # Approach 2: Using field() without name but with default
        print(f"\n2. Using field() without name:")
        try:
            class DefaultFieldModel(msgspec.Struct):
                test_field: str = field()
                number_field: int = field()
            
            print(f"   DefaultFieldModel fields: {DefaultFieldModel.__struct_fields__}")
            
            test_data = {"test_field": "hello", "number_field": 42}
            decoded = msgspec.convert(test_data, type=DefaultFieldModel, strict=True)
            print(f"   Decoded: {decoded}")
            
            if hasattr(decoded, 'test_field'):
                val = decoded.test_field
                print(f"   test_field: {val} (type: {type(val)})")
                if hasattr(val, 'name'):
                    print(f"     → Field name: {val.name}")
                else:
                    print(f"     → Actual value!")
            else:
                print(f"   ❌ No test_field attribute")
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        # Approach 3: The old way - using field() as a decorator
        print(f"\n3. Using field() as decorator:")
        try:
            class DecoratorFieldModel(msgspec.Struct):
                test_field = field(name="test_field")
                number_field = field(name="number_field")
            
            print(f"   DecoratorFieldModel fields: {DecoratorFieldModel.__struct_fields__}")
            
            test_data = {"test_field": "hello", "number_field": 42}
            decoded = msgspec.convert(test_data, type=DecoratorFieldModel, strict=True)
            print(f"   Decoded: {decoded}")
            
            if hasattr(decoded, 'test_field'):
                val = decoded.test_field
                print(f"   test_field: {val} (type: {type(val)})")
                if hasattr(val, 'name'):
                    print(f"     → Field name: {val.name}")
                else:
                    print(f"     → Actual value!")
            else:
                print(f"   ❌ No test_field attribute")
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        # Approach 4: Check if we need to use msgspec.json.decode instead
        print(f"\n4. Using msgspec.json.decode:")
        try:
            import json
            
            class JsonDecodeModel(msgspec.Struct):
                test_field: str = field(name="test_field")
                number_field: int = field(name="number_field")
            
            test_data = {"test_field": "hello", "number_field": 42}
            json_str = json.dumps(test_data)
            decoded = msgspec.json.decode(json_str, type=JsonDecodeModel, strict=True)
            print(f"   Decoded: {decoded}")
            
            if hasattr(decoded, 'test_field'):
                val = decoded.test_field
                print(f"   test_field: {val} (type: {type(val)})")
                if hasattr(val, 'name'):
                    print(f"     → Field name: {val.name}")
                else:
                    print(f"     → Actual value!")
            else:
                print(f"   ❌ No test_field attribute")
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        # Approach 5: Check the msgspec documentation/examples
        print(f"\n5. Checking msgspec capabilities:")
        print(f"   Available attributes in msgspec: {[attr for attr in dir(msgspec) if not attr.startswith('_')]}")
        
        # Try to find examples in the msgspec module
        try:
            if hasattr(msgspec, 'examples'):
                print(f"   Examples available: {msgspec.examples}")
        except:
            pass
            
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_msgspec_field_inspection():
    """Inspect msgspec Field objects."""
    print(f"\n🔍 Inspecting msgspec Field objects...")
    
    try:
        class TestModel(msgspec.Struct):
            test_field: str = field(name="test_field")
        
        print(f"TestModel struct fields: {TestModel.__struct_fields__}")
        
        # Check the field objects
        test_field_obj = TestModel.__annotations__['test_field']
        print(f"test_field annotation: {test_field_obj}")
        
        # Try to create a field manually
        try:
            manual_field = msgspec.field(name="test_field")
            print(f"Manual field: {manual_field}")
            print(f"Manual field type: {type(manual_field)}")
            print(f"Manual field attributes: {[attr for attr in dir(manual_field) if not attr.startswith('_')]}")
        except Exception as e:
            print(f"Manual field creation failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Researching msgspec 0.19.0 struct definition")
    print("=" * 60)
    
    approaches_success = test_msgspec_0190_approaches()
    inspection_success = test_msgspec_field_inspection()
    
    print(f"\n📊 Results:")
    print("=" * 30)
    print(f"Approaches test: {'✓ PASS' if approaches_success else '✗ FAIL'}")
    print(f"Inspection test: {'✓ PASS' if inspection_success else '✗ FAIL'}")
    
    print(f"\n🎯 Conclusion:")
    print(f"Msgspec 0.19.0 appears to have a different API than expected.")
    print(f"The issue is likely that this version requires explicit field definition")
    print(f"or there may be a compatibility issue with the current approach.")