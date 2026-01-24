#!/usr/bin/env python3
"""
Test msgspec 0.19.0 alternative approaches including defstruct.
"""

import msgspec
from msgspec import field
import json

def test_defstruct_approach():
    """Test using msgspec.defstruct for version 0.19.0."""
    print("🔍 Testing msgspec.defstruct approach...")
    
    try:
        # Use defstruct which is available in msgspec 0.19.0
        TestModel = msgspec.defstruct(
            "TestModel",
            ["test_field", "number_field"],
            {"test_field": str, "number_field": int}
        )
        
        print(f"TestModel type: {type(TestModel)}")
        print(f"TestModel fields: {TestModel.__struct_fields__}")
        
        # Test conversion
        test_data = {"test_field": "hello", "number_field": 42}
        decoded = msgspec.convert(test_data, type=TestModel, strict=True)
        
        print(f"Decoded: {decoded}")
        
        if hasattr(decoded, 'test_field'):
            val = decoded.test_field
            print(f"test_field: {val} (type: {type(val)})")
            if hasattr(val, 'name'):
                print(f"  → Field name: {val.name}")
            else:
                print(f"  → Actual value!")
                return True
        else:
            print(f"❌ No test_field attribute")
            
        return False
        
    except Exception as e:
        print(f"❌ defstruct approach failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_manual_struct_creation():
    """Test manually creating and populating a struct."""
    print(f"\n🔍 Testing manual struct creation...")
    
    try:
        # Create a basic struct
        class ManualModel(msgspec.Struct):
            pass
        
        print(f"ManualModel fields: {ManualModel.__struct_fields__}")
        
        # Try to manually set attributes
        test_data = {"test_field": "hello", "number_field": 42}
        
        # Create instance and set attributes manually
        instance = ManualModel()
        for key, value in test_data.items():
            setattr(instance, key, value)
        
        print(f"Manual instance: {instance}")
        print(f"Instance dir: {[attr for attr in dir(instance) if not attr.startswith('_')]}")
        
        if hasattr(instance, 'test_field'):
            val = instance.test_field
            print(f"test_field: {val} (type: {type(val)})")
            return True
        else:
            print(f"❌ No test_field attribute")
            
        return False
        
    except Exception as e:
        print(f"❌ Manual struct creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_attribute_access():
    """Test accessing attributes directly without conversion."""
    print(f"\n🔍 Testing direct attribute access...")
    
    try:
        # Create a model
        class DirectModel(msgspec.Struct):
            test_field: str = field(name="test_field")
            number_field: int = field(name="number_field")
        
        print(f"DirectModel fields: {DirectModel.__struct_fields__}")
        
        # Create instance directly with data
        instance = DirectModel()
        instance.test_field = "hello"
        instance.number_field = 42
        
        print(f"Direct instance: {instance}")
        print(f"test_field: {instance.test_field}")
        print(f"number_field: {instance.number_field}")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct attribute access failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_msgspec_inspect():
    """Use msgspec.inspect to understand the struct."""
    print(f"\n🔍 Using msgspec.inspect...")
    
    try:
        # Create a model
        class InspectModel(msgspec.Struct):
            test_field: str = field(name="test_field")
            number_field: int = field(name="number_field")
        
        # Use inspect to understand the struct
        inspection = msgspec.inspect(InspectModel)
        print(f"Inspection: {inspection}")
        print(f"Inspection type: {type(inspection)}")
        print(f"Inspection attributes: {[attr for attr in dir(inspection) if not attr.startswith('_')]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Inspection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_msgspec_struct_module():
    """Test the msgspec.structs module."""
    print(f"\n🔍 Testing msgspec.structs module...")
    
    try:
        import msgspec.structs
        
        print(f"Structs module: {msgspec.structs}")
        print(f"Structs attributes: {[attr for attr in dir(msgspec.structs) if not attr.startswith('_')]}")
        
        # Try to use struct creation functions
        if hasattr(msgspec.structs, 'make_struct'):
            print(f"Found make_struct function")
            
        if hasattr(msgspec.structs, 'create_struct'):
            print(f"Found create_struct function")
            
        return True
        
    except Exception as e:
        print(f"❌ Structs module test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Testing msgspec 0.19.0 alternative approaches")
    print("=" * 60)
    
    defstruct_success = test_defstruct_approach()
    manual_success = test_manual_struct_creation()
    direct_success = test_direct_attribute_access()
    inspect_success = test_msgspec_inspect()
    structs_success = test_msgspec_struct_module()
    
    print(f"\n📊 Results:")
    print("=" * 30)
    print(f"defstruct: {'✓ PASS' if defstruct_success else '✗ FAIL'}")
    print(f"Manual creation: {'✓ PASS' if manual_success else '✗ FAIL'}")
    print(f"Direct access: {'✓ PASS' if direct_success else '✗ FAIL'}")
    print(f"Inspect: {'✓ PASS' if inspect_success else '✗ FAIL'}")
    print(f"Structs module: {'✓ PASS' if structs_success else '✗ FAIL'}")
    
    if defstruct_success:
        print(f"\n🎉 SUCCESS! defstruct approach works!")
        print(f"This is the solution for msgspec 0.19.0!")
    elif manual_success or direct_success:
        print(f"\n🎯 Alternative approaches work - defstruct may not be the right solution.")
    else:
        print(f"\n❌ All approaches failed - need to find another solution.")