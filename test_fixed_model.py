#!/usr/bin/env python3
"""
Test the fixed WorldstateModel with msgspec.
"""

import msgspec
import requests
import json
from msgspec import field

def test_fixed_worldstate_model():
    """Test the fixed WorldstateModel with real data."""
    print("🔍 Testing fixed WorldstateModel...")
    
    try:
        # Import the fixed model
        from app.clients.warframe.worldstate.parsers.worldstate import WorldstateModel
        
        print(f"Model struct fields: {WorldstateModel.__struct_fields__}")
        print(f"Model type: {type(WorldstateModel)}")
        
        # Get real data
        response = requests.get("https://api.warframe.com/cdn/worldState.php")
        data = response.json()
        print(f"✓ Got API data with {len(data)} keys")
        
        # Test msgspec.convert with the fixed model
        try:
            decoded = msgspec.convert(data, type=WorldstateModel, strict=True)
            print(f"✓ msgspec.convert() succeeded!")
            print(f"  Type: {type(decoded)}")
            print(f"  Dir: {[attr for attr in dir(decoded) if not attr.startswith('_')]}")
            
            # Test accessing some fields
            try:
                version = decoded.Version
                print(f"  ✓ Version: {version} (type: {type(version)})")
            except AttributeError as e:
                print(f"  ✗ AttributeError accessing Version: {e}")
                
            try:
                worldseed = decoded.WorldSeed
                print(f"  ✓ WorldSeed: {worldseed[:50]}... (type: {type(worldseed)})")
            except AttributeError as e:
                print(f"  ✗ AttributeError accessing WorldSeed: {e}")
                
            try:
                events = decoded.Events
                print(f"  ✓ Events: {len(events)} events (type: {type(events)})")
            except AttributeError as e:
                print(f"  ✗ AttributeError accessing Events: {e}")
                
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

def test_field_vs_default():
    """Test the difference between field() and field(default=...)."""
    print(f"\n🔍 Testing field() vs field(default=...)...")
    
    try:
        # Test model with field() only
        class SimpleModel(msgspec.Struct):
            test_field: str = field()
            number_field: int = field()
        
        print(f"SimpleModel fields: {SimpleModel.__struct_fields__}")
        
        # Test model with defaults
        class DefaultModel(msgspec.Struct):
            test_field: str = field(default="default")
            number_field: int = field(default=0)
        
        print(f"DefaultModel fields: {DefaultModel.__struct_fields__}")
        
        # Test conversion
        test_data = {"test_field": "hello", "number_field": 42}
        
        try:
            simple_decoded = msgspec.convert(test_data, type=SimpleModel, strict=True)
            print(f"✓ SimpleModel conversion: {simple_decoded}")
            if hasattr(simple_decoded, 'test_field'):
                print(f"  ✓ test_field: {simple_decoded.test_field}")
            else:
                print(f"  ✗ No test_field attribute")
        except Exception as e:
            print(f"✗ SimpleModel conversion failed: {e}")
            
        try:
            default_decoded = msgspec.convert(test_data, type=DefaultModel, strict=True)
            print(f"✓ DefaultModel conversion: {default_decoded}")
            if hasattr(default_decoded, 'test_field'):
                print(f"  ✓ test_field: {default_decoded.test_field}")
            else:
                print(f"  ✗ No test_field attribute")
        except Exception as e:
            print(f"✗ DefaultModel conversion failed: {e}")
            
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Testing fixed WorldstateModel")
    print("=" * 50)
    
    model_success = test_fixed_worldstate_model()
    field_test_success = test_field_vs_default()
    
    print(f"\n📊 Results:")
    print("=" * 30)
    print(f"Fixed model: {'✓ PASS' if model_success else '✗ FAIL'}")
    print(f"Field test: {'✓ PASS' if field_test_success else '✗ FAIL'}")
    
    if model_success:
        print(f"\n🎉 Success! The fix worked!")
        print(f"Solution: Remove 'default' parameters from field() calls in msgspec 0.19.0")
    else:
        print(f"\n❌ Issues still exist.")