#!/usr/bin/env python3
"""
Debug the msgspec attribute access issue.
"""

import json
import msgspec
import requests

def debug_msgspec_issue():
    """Debug the specific msgspec attribute access problem."""
    print("🔍 Debugging msgspec attribute access issue...")
    
    try:
        # Get real data
        response = requests.get("https://api.warframe.com/cdn/worldState.php")
        data = response.json()
        print(f"✓ Got API data with {len(data)} keys")
        
        # Check actual field names in data
        print(f"📋 Sample keys in data: {list(data.keys())[:10]}")
        
        # Test with minimal data
        minimal_data = {
            "WorldSeed": data.get("WorldSeed", "test"),
            "Version": data.get("Version", 10),
            "MobileVersion": data.get("MobileVersion", "5.3.0.0"),
            "BuildLabel": data.get("BuildLabel", "test"),
            "Time": data.get("Time", 1234567890)
        }
        
        print(f"📋 Minimal test data: {minimal_data}")
        
        # Create model
        class TestModel(msgspec.Struct):
            WorldSeed: str
            Version: int
            MobileVersion: str
            BuildLabel: str
            Time: int
        
        # Test conversion
        try:
            decoded = msgspec.convert(minimal_data, type=TestModel, strict=True)
            print(f"✓ msgspec.convert() succeeded")
            print(f"  Decoded object: {decoded}")
            print(f"  Object type: {type(decoded)}")
            print(f"  Object dir: {[attr for attr in dir(decoded) if not attr.startswith('_')]}")
            
            # Try to access attributes
            try:
                version_val = decoded.Version
                print(f"✓ decoded.Version = {version_val} (type: {type(version_val)})")
            except AttributeError as e:
                print(f"✗ AttributeError accessing Version: {e}")
                
            try:
                worldseed_val = decoded.WorldSeed
                print(f"✓ decoded.WorldSeed = {worldseed_val} (type: {type(worldseed_val)})")
            except AttributeError as e:
                print(f"✗ AttributeError accessing WorldSeed: {e}")
                
            # Try all attributes
            for field_name in ["WorldSeed", "Version", "MobileVersion", "BuildLabel", "Time"]:
                try:
                    val = getattr(decoded, field_name)
                    print(f"✓ getattr(decoded, '{field_name}') = {val} (type: {type(val)})")
                except AttributeError as e:
                    print(f"✗ getattr failed for '{field_name}': {e}")
                    
            return True
            
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

def test_msgspec_inspection():
    """Inspect msgspec behavior more closely."""
    print(f"\n🔍 Inspecting msgspec behavior...")
    
    try:
        # Simple test
        test_data = {"test_field": 42}
        
        class TestModel(msgspec.Struct):
            test_field: int
        
        decoded = msgspec.convert(test_data, type=TestModel, strict=True)
        
        print(f"Test data: {test_data}")
        print(f"Decoded: {decoded}")
        print(f"Type: {type(decoded)}")
        
        # Check if it's actually working
        if hasattr(decoded, 'test_field'):
            print(f"✓ Has test_field attribute")
            print(f"  Value: {decoded.test_field}")
            print(f"  Type: {type(decoded.test_field)}")
        else:
            print(f"✗ No test_field attribute")
            
        # Check all attributes
        print(f"All attributes: {dir(decoded)}")
        
        # Check if it's a Field object
        if hasattr(decoded.test_field, 'name'):
            print(f"✗ test_field is a Field object")
            print(f"  Field name: {decoded.test_field.name}")
            print(f"  Field type: {decoded.test_field.type}")
        else:
            print(f"✓ test_field is a regular value")
            
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Debugging msgspec attribute access")
    print("=" * 50)
    
    debug_success = debug_msgspec_issue()
    inspect_success = test_msgspec_inspection()
    
    print(f"\n📊 Results:")
    print("=" * 30)
    print(f"Debug test: {'✓ PASS' if debug_success else '✗ FAIL'}")
    print(f"Inspect test: {'✓ PASS' if inspect_success else '✗ FAIL'}")