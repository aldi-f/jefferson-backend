#!/usr/bin/env python3
"""
Test the completely fixed WorldstateModel with real data.
"""

import msgspec
import requests
import json
import sys
import importlib

def test_fresh_worldstate_model():
    """Test the fresh WorldstateModel with real data."""
    print("🔍 Testing fresh WorldstateModel...")
    
    try:
        # Force reload the module to get the fresh version
        if 'app.clients.warframe.worldstate.parsers.worldstate' in sys.modules:
            importlib.reload(sys.modules['app.clients.warframe.worldstate.parsers.worldstate'])
        
        from app.clients.warframe.worldstate.parsers.worldstate import WorldstateModel
        
        print(f"Model struct fields: {WorldstateModel.__struct_fields__}")
        print(f"Model type: {type(WorldstateModel)}")
        
        # Check if __struct_fields__ is properly defined
        if not WorldstateModel.__struct_fields__:
            print(f"❌ __struct_fields__ is still empty!")
            return False
        else:
            print(f"✅ __struct_fields__ has {len(WorldstateModel.__struct_fields__)} fields")
            print(f"First 10 fields: {list(WorldstateModel.__struct_fields__)[:10]}")
        
        # Get real data
        response = requests.get("https://api.warframe.com/cdn/worldState.php")
        data = response.json()
        print(f"✓ Got API data with {len(data)} keys")
        
        # Test msgspec.convert with the fixed model
        try:
            decoded = msgspec.convert(data, type=WorldstateModel, strict=True)
            print(f"✓ msgspec.convert() succeeded!")
            print(f"  Type: {type(decoded)}")
            
            # Test accessing some fields
            try:
                version = decoded.Version
                if hasattr(version, 'name'):
                    print(f"  ⚠️  Version is still a Field object: {version}")
                    print(f"     Field name: {version.name}")
                    print(f"     Field type: {version.type}")
                else:
                    print(f"  ✅ Version: {version} (type: {type(version)})")
            except AttributeError as e:
                print(f"  ✗ AttributeError accessing Version: {e}")
                
            try:
                worldseed = decoded.WorldSeed
                if hasattr(worldseed, 'name'):
                    print(f"  ⚠️  WorldSeed is still a Field object: {worldseed}")
                    print(f"     Field name: {worldseed.name}")
                else:
                    print(f"  ✅ WorldSeed: {worldseed[:50]}... (type: {type(worldseed)})")
            except AttributeError as e:
                print(f"  ✗ AttributeError accessing WorldSeed: {e}")
                
            try:
                events = decoded.Events
                if hasattr(events, 'name'):
                    print(f"  ⚠️  Events is still a Field object: {events}")
                    print(f"     Field name: {events.name}")
                else:
                    print(f"  ✅ Events: {len(events)} events (type: {type(events)})")
            except AttributeError as e:
                print(f"  ✗ AttributeError accessing Events: {e}")
                
            # Check if we're getting actual values
            has_actual_values = False
            for field_name in ["Version", "WorldSeed", "Events"]:
                try:
                    val = getattr(decoded, field_name)
                    if not hasattr(val, 'name'):
                        has_actual_values = True
                        print(f"  ✅ {field_name} is an actual value!")
                        break
                except AttributeError:
                    continue
                    
            if has_actual_values:
                print(f"🎉 SUCCESS! The fix worked - we're getting actual values!")
                return True
            else:
                print(f"❌ Still getting Field objects - need to investigate further")
                return False
                
        except Exception as e:
            print(f"✗ msgspec.convert() failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_struct_with_fields():
    """Test a simple struct with explicit __struct_fields__."""
    print(f"\n🔍 Testing simple struct with explicit fields...")
    
    try:
        # Create a simple struct with explicit fields
        class SimpleTestStruct(msgspec.Struct):
            __struct_fields__ = ("test_field", "number_field")
            test_field: str
            number_field: int
        
        print(f"SimpleTestStruct fields: {SimpleTestStruct.__struct_fields__}")
        
        # Test conversion
        test_data = {"test_field": "hello", "number_field": 42}
        decoded = msgspec.convert(test_data, type=SimpleTestStruct, strict=True)
        
        print(f"Decoded: {decoded}")
        
        # Check if we get actual values
        test_val = decoded.test_field
        if hasattr(test_val, 'name'):
            print(f"⚠️  test_field is Field object: {test_val}")
            print(f"   Field name: {test_val.name}")
        else:
            print(f"✅ test_field is actual value: {test_val}")
            return True
            
        return False
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Testing completely fixed WorldstateModel")
    print("=" * 60)
    
    fresh_test_success = test_fresh_worldstate_model()
    simple_test_success = test_simple_struct_with_fields()
    
    print(f"\n📊 Results:")
    print("=" * 30)
    print(f"Fresh model test: {'✓ PASS' if fresh_test_success else '✗ FAIL'}")
    print(f"Simple struct test: {'✓ PASS' if simple_test_success else '✗ FAIL'}")
    
    if fresh_test_success and simple_test_success:
        print(f"\n🎉 SUCCESS! The fix worked completely!")
    elif simple_test_success:
        print(f"\n🎯 The simple struct works, but there might be an import issue with the complex model.")
    else:
        print(f"\n❌ Still issues - msgspec 0.19.0 may need a different approach.")