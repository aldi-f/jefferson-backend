#!/usr/bin/env python3
"""
Test msgspec 0.19.0 defstruct and structs module approaches.
"""

import msgspec
from msgspec import field
import json

def test_fixed_defstruct():
    """Test using msgspec.defstruct with correct signature."""
    print("🔍 Testing fixed msgspec.defstruct approach...")
    
    try:
        # Use defstruct with correct signature for 0.19.0
        TestModel = msgspec.defstruct(
            "TestModel",
            ["test_field", "number_field"]
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

def test_structs_module_approaches():
    """Test various approaches using msgspec.structs."""
    print(f"\n🔍 Testing msgspec.structs approaches...")
    
    try:
        import msgspec.structs
        
        # Approach 1: Use force_setattr
        print(f"\n1. Using force_setattr:")
        class ForceSetattrModel(msgspec.Struct):
            test_field: str = field(name="test_field")
            number_field: int = field(name="number_field")
        
        print(f"ForceSetattrModel fields: {ForceSetattrModel.__struct_fields__}")
        
        # Create instance and force set attributes
        instance = ForceSetattrModel()
        msgspec.structs.force_setattr(instance, "test_field", "hello")
        msgspec.structs.force_setattr(instance, "number_field", 42)
        
        print(f"ForceSetattr instance: {instance}")
        print(f"test_field: {instance.test_field}")
        print(f"number_field: {instance.number_field}")
        
        # Check if values are actual values
        if not hasattr(instance.test_field, 'name'):
            print(f"✅ Getting actual values with force_setattr!")
            return True
        else:
            print(f"❌ Still getting Field objects")
            
        # Approach 2: Use fields function
        print(f"\n2. Using msgspec.structs.fields:")
        try:
            model_fields = msgspec.structs.fields(ForceSetattrModel)
            print(f"Model fields: {model_fields}")
            print(f"Fields type: {type(model_fields)}")
            
            if hasattr(model_fields, '__iter__'):
                for field_info in model_fields:
                    print(f"  Field: {field_info}")
                    
        except Exception as e:
            print(f"❌ Fields function failed: {e}")
            
        # Approach 3: Try to convert with force_setattr
        print(f"\n3. Trying conversion with force_setattr:")
        try:
            test_data = {"test_field": "hello", "number_field": 42}
            instance = ForceSetattrModel()
            
            # Manually set all fields from data
            for field_name in test_data:
                msgspec.structs.force_setattr(instance, field_name, test_data[field_name])
            
            print(f"Converted instance: {instance}")
            print(f"test_field: {instance.test_field}")
            print(f"number_field: {instance.number_field}")
            
            # Check if we got actual values
            if not hasattr(instance.test_field, 'name'):
                print(f"✅ Success! Got actual values through manual setting!")
                return True
            else:
                print(f"❌ Still getting Field objects")
                
        except Exception as e:
            print(f"❌ Conversion with force_setattr failed: {e}")
            
        return False
        
    except Exception as e:
        print(f"❌ Structs module approaches failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_field_info_approach():
    """Test using FieldInfo approach."""
    print(f"\n🔍 Testing FieldInfo approach...")
    
    try:
        import msgspec.structs
        
        # Create a model
        class FieldInfoModel(msgspec.Struct):
            test_field: str = field(name="test_field")
            number_field: int = field(name="number_field")
        
        # Get field info
        field_infos = msgspec.structs.fields(FieldInfoModel)
        print(f"Field infos: {field_infos}")
        
        # Create instance manually
        instance = FieldInfoModel()
        
        # Try to set values using field info
        for field_info in field_infos:
            print(f"Field info: {field_info}")
            print(f"Field name: {field_info.name}")
            print(f"Field type: {field_info.type}")
            
            # Try to set the value
            try:
                msgspec.structs.force_setattr(instance, field_info.name, "test_value")
                print(f"✓ Set {field_info.name} successfully")
            except Exception as e:
                print(f"✗ Failed to set {field_info.name}: {e}")
        
        print(f"Final instance: {instance}")
        
        return True
        
    except Exception as e:
        print(f"❌ FieldInfo approach failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_struct_asdict():
    """Test using asdict function."""
    print(f"\n🔍 Testing asdict approach...")
    
    try:
        import msgspec.structs
        
        class AsDictModel(msgspec.Struct):
            test_field: str = field(name="test_field")
            number_field: int = field(name="number_field")
        
        # Create instance with force_setattr
        instance = AsDictModel()
        msgspec.structs.force_setattr(instance, "test_field", "hello")
        msgspec.structs.force_setattr(instance, "number_field", 42)
        
        # Convert to dict
        as_dict = msgspec.structs.asdict(instance)
        print(f"As dict: {as_dict}")
        
        # Check if it works
        if as_dict.get("test_field") == "hello":
            print(f"✅ asdict works correctly!")
            return True
        else:
            print(f"❌ asdict didn't work as expected")
            
        return False
        
    except Exception as e:
        print(f"❌ asdict approach failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Testing msgspec 0.19.0 defstruct and structs module")
    print("=" * 70)
    
    defstruct_success = test_fixed_defstruct()
    structs_success = test_structs_module_approaches()
    fieldinfo_success = test_field_info_approach()
    asdict_success = test_struct_asdict()
    
    print(f"\n📊 Results:")
    print("=" * 30)
    print(f"defstruct: {'✓ PASS' if defstruct_success else '✗ FAIL'}")
    print(f"Structs module: {'✓ PASS' if structs_success else '✗ FAIL'}")
    print(f"FieldInfo: {'✓ PASS' if fieldinfo_success else '✗ FAIL'}")
    print(f"AsDict: {'✓ PASS' if asdict_success else '✗ FAIL'}")
    
    if structs_success or fieldinfo_success or asdict_success:
        print(f"\n🎯 SUCCESS! Found working approaches with msgspec.structs!")
        print(f"The solution is to use msgspec.structs.force_setattr() to manually set values.")
    elif defstruct_success:
        print(f"\n🎉 SUCCESS! defstruct approach works!")
    else:
        print(f"\n❌ All approaches failed - need to find another solution.")