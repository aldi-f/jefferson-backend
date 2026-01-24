#!/usr/bin/env python3
"""
Simple test to verify msgspec approach with real data.
"""

import json
import msgspec
import requests

def test_msgspec_with_real_data():
    """Test msgspec with actual API data."""
    print("🔍 Testing msgspec with real API data...")
    
    try:
        # Get real data from API
        response = requests.get("https://api.warframe.com/cdn/worldState.php")
        if response.status_code != 200:
            print(f"✗ API request failed: {response.status_code}")
            return False
        
        data = response.json()
        print(f"✓ Got data with {len(data)} keys")
        
        # Create a minimal working model
        class MinimalWorldstate(msgspec.Struct):
            WorldSeed: str
            Version: int
            MobileVersion: str
            BuildLabel: str
            Time: int
        
        # Test msgspec.convert
        try:
            decoded = msgspec.convert(data, type=MinimalWorldstate, strict=True)
            print(f"✓ msgspec.convert() works!")
            print(f"  - Type: {type(decoded)}")
            print(f"  - Version: {decoded.Version} (type: {type(decoded.Version)})")
            print(f"  - WorldSeed: {decoded.WorldSeed[:20]}...")
            
            # Check if we're getting actual values or Field objects
            if hasattr(decoded.Version, 'name'):
                print("❌ Still getting Field object")
                return False
            else:
                print("✅ Getting actual values!")
                return True
                
        except Exception as e:
            print(f"✗ msgspec.convert() failed: {e}")
            
            # Try with json.decode
            try:
                json_str = json.dumps(data)
                decoded = msgspec.json.decode(json_str, type=MinimalWorldstate, strict=True)
                print(f"✓ msgspec.json.decode() works!")
                print(f"  - Version: {decoded.Version}")
                return True
            except Exception as e2:
                print(f"✗ json.decode() also failed: {e2}")
                return False
                
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_field_vs_attribute():
    """Test the difference between field and attribute access."""
    print("\n🔍 Testing field vs attribute access...")
    
    try:
        # Create a test model
        class TestModel(msgspec.Struct):
            test_field: int
        
        # Test data
        data = {"test_field": 42}
        
        # Decode
        decoded = msgspec.convert(data, type=TestModel, strict=True)
        
        print(f"Decoded object: {decoded}")
        print(f"Type: {type(decoded)}")
        print(f"test_field value: {decoded.test_field}")
        print(f"test_field type: {type(decoded.test_field)}")
        
        # Check if it's a Field object
        if hasattr(decoded.test_field, 'name'):
            print("❌ test_field is a Field object")
            print(f"Field name: {decoded.test_field.name}")
            print(f"Field type: {decoded.test_field.type}")
            return False
        else:
            print("✅ test_field is actual value")
            return True
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Testing msgspec approaches")
    print("=" * 50)
    
    # Test with real data
    real_data_success = test_msgspec_with_real_data()
    
    # Test field vs attribute
    field_test_success = test_field_vs_attribute()
    
    print(f"\n📊 Results:")
    print("=" * 30)
    print(f"Real data test: {'✓ PASS' if real_data_success else '✗ FAIL'}")
    print(f"Field vs attribute: {'✓ PASS' if field_test_success else '✗ FAIL'}")
    
    if real_data_success and field_test_success:
        print(f"\n🎉 Success! msgspec.convert() works with real data!")
        print(f"Solution: Use msgspec.convert() with exact field name matching.")
    else:
        print(f"\n❌ Issues still exist.")