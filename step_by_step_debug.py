#!/usr/bin/env python3
"""
Step by step debugging of the msgspec issue.
"""

import json
import msgspec
from msgspec import Struct, field
import asyncio

def test_basic_msgspec():
    """Test basic msgspec functionality."""
    print("🔍 Testing basic msgspec functionality...")
    
    # Create a simple model
    class TestModel(Struct):
        version: int
        world_seed: str
    
    test_data = {
        "version": 10,
        "world_seed": "test_seed"
    }
    
    try:
        decoded = msgspec.json.decode(json.dumps(test_data), type=TestModel, strict=True)
        print(f"✓ Basic model works")
        print(f"  - Version: {decoded.version}")
        print(f"  - WorldSeed: {decoded.world_seed}")
        return True
    except Exception as e:
        print(f"✗ Basic model failed: {e}")
        return False

def test_field_mapping():
    """Test field mapping with msgspec.field."""
    print(f"\n🔍 Testing field mapping...")
    
    # Create a model with field mapping
    class TestModel(Struct):
        version: int = field(name="Version")
        world_seed: str = field(name="WorldSeed")
    
    test_data = {
        "Version": 10,
        "WorldSeed": "test_seed"
    }
    
    try:
        decoded = msgspec.json.decode(json.dumps(test_data), type=TestModel, strict=True)
        print(f"✓ Field mapping works")
        print(f"  - Version: {decoded.version}")
        print(f"  - WorldSeed: {decoded.world_seed}")
        return True
    except Exception as e:
        print(f"✗ Field mapping failed: {e}")
        return False

def test_nested_models():
    """Test nested models."""
    print(f"\n🔍 Testing nested models...")
    
    # Create a nested message model
    class Message(Struct):
        language_code: str
        message: str
    
    # Create an event model
    class Event(Struct):
        messages: list[Message]
        prop: str
    
    test_data = {
        "Messages": [
            {"LanguageCode": "en", "Message": "Test message"}
        ],
        "Prop": "https://example.com"
    }
    
    try:
        decoded = msgspec.json.decode(json.dumps(test_data), type=Event, strict=True)
        print(f"✓ Nested model works")
        print(f"  - Prop: {decoded.prop}")
        print(f"  - Messages: {len(decoded.messages)}")
        print(f"  - First message: {decoded.messages[0].message}")
        return True
    except Exception as e:
        print(f"✗ Nested model failed: {e}")
        return False

def test_worldstate_import():
    """Test importing the actual WorldstateModel."""
    print(f"\n🔍 Testing WorldstateModel import...")
    
    try:
        from app.clients.warframe.worldstate.parsers.worldstate import WorldstateModel
        print(f"✓ Import successful")
        print(f"  - Model: {WorldstateModel}")
        print(f"  - Type: {type(WorldstateModel)}")
        
        # Check annotations
        annotations = WorldstateModel.__annotations__
        print(f"  - Annotations: {list(annotations.keys())}")
        
        # Try to create an instance
        instance = WorldstateModel()
        print(f"  - Instance created: {instance}")
        
        # Check if it's a proper Struct
        if isinstance(instance, Struct):
            print(f"  - Is Struct: True")
        else:
            print(f"  - Is Struct: False")
        
        # Check field values
        version = getattr(instance, 'version', None)
        if version is not None:
            print(f"  - Version field: {version} (type: {type(version)})")
            if hasattr(version, '__class__') and 'Field' in str(version.__class__):
                print(f"  ⚠ Version is Field object")
            else:
                print(f"  ✓ Version is actual value")
        else:
            print(f"  ✗ Version field not found")
        
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_with_real_data():
    """Test with actual API data."""
    print(f"\n🔍 Testing with real API data...")
    
    try:
        import aiohttp
        
        async def get_data():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get("https://api.warframe.com/cdn/worldState.php") as response:
                        if response.status == 200:
                            text = await response.text()
                            return json.loads(text)
                        else:
                            return None
            except:
                return None
        
        data = await get_data()
        if not data:
            print("✗ Could not fetch data")
            return False
            
        print(f"✓ Got data with {len(data)} keys")
        print(f"Version: {data.get('Version')}")
        
        # Test with a simple model
        class SimpleWorldstate(Struct):
            version: int = field(name="Version")
            world_seed: str = field(name="WorldSeed")
            mobile_version: str = field(name="MobileVersion")
            build_label: str = field(name="BuildLabel")
            time: int = field(name="Time")
        
        try:
            decoded = msgspec.json.decode(json.dumps(data), type=SimpleWorldstate, strict=True)
            print(f"✓ Simple model with real data works")
            print(f"  - Version: {decoded.version}")
            print(f"  - WorldSeed: {decoded.world_seed[:20]}...")
            print(f"  - MobileVersion: {decoded.mobile_version}")
            print(f"  - BuildLabel: {decoded.build_label}")
            print(f"  - Time: {decoded.time}")
            return True
        except Exception as e:
            print(f"✗ Simple model with real data failed: {e}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

async def main():
    """Main test function."""
    print("🔧 Step by step msgspec debugging")
    print("=" * 60)
    
    # Test basic functionality
    basic_success = test_basic_msgspec()
    
    # Test field mapping
    mapping_success = test_field_mapping()
    
    # Test nested models
    nested_success = test_nested_models()
    
    # Test import
    import_success = test_worldstate_import()
    
    # Test with real data
    real_data_success = await test_with_real_data()
    
    # Summary
    print(f"\n📊 Test Results:")
    print("=" * 40)
    print(f"Basic msgspec: {'✓ PASS' if basic_success else '✗ FAIL'}")
    print(f"Field mapping: {'✓ PASS' if mapping_success else '✗ FAIL'}")
    print(f"Nested models: {'✓ PASS' if nested_success else '✗ FAIL'}")
    print(f"Worldstate import: {'✓ PASS' if import_success else '✗ FAIL'}")
    print(f"Real data test: {'✓ PASS' if real_data_success else '✗ FAIL'}")
    
    if all([basic_success, mapping_success, nested_success, import_success, real_data_success]):
        print(f"\n🎉 All tests passed!")
        print(f"The issue is likely in the complex WorldstateModel structure.")
    else:
        print(f"\n❌ Some basic functionality is failing.")

if __name__ == "__main__":
    asyncio.run(main())