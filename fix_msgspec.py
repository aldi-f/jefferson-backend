#!/usr/bin/env python3
"""
Fix the msgspec issue by checking the exact problem.
"""

import json
import msgspec
from app.config.settings import settings

# Define a simple test model outside the function
class SimpleWorldstate(msgspec.Struct):
    world_seed: str
    version: int
    mobile_version: str
    build_label: str
    time: int

def test_simple_model():
    """Test the simple model."""
    print("🔍 Testing simple model...")
    
    try:
        import aiohttp
        import asyncio
        
        async def get_data():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(settings.WORLDSTATE_URL) as response:
                        if response.status == 200:
                            text = await response.text()
                            return json.loads(text)
                        else:
                            return None
            except:
                return None
        
        data = asyncio.run(get_data())
        if not data:
            print("✗ Could not fetch data")
            return False
            
    except Exception as e:
        print(f"✗ Error fetching data: {e}")
        return False
    
    print(f"✓ Got data with {len(data)} keys")
    print(f"Version: {data.get('Version')}")
    
    # Test simple model
    try:
        decoded = msgspec.json.decode(json.dumps(data), type=SimpleWorldstate, strict=True)
        print(f"✓ Decoding successful")
        print(f"  - Type: {type(decoded)}")
        print(f"  - Version: {decoded.version}")
        print(f"  - WorldSeed: {decoded.world_seed}")
        print(f"  - MobileVersion: {decoded.mobile_version}")
        print(f"  - BuildLabel: {decoded.build_label}")
        print(f"  - Time: {decoded.time}")
        return True
    except Exception as e:
        print(f"✗ Decoding failed: {e}")
        return False

def check_msgspec_issue():
    """Check what's wrong with the current msgspec setup."""
    print(f"\n🔍 Checking msgspec setup...")
    
    # Test with the actual model
    from app.clients.warframe.worldstate.parsers.worldstate import WorldstateModel
    
    print(f"WorldstateModel: {WorldstateModel}")
    print(f"Annotations: {WorldstateModel.__annotations__}")
    
    # Check if the model can be instantiated
    try:
        # Try to create an instance
        instance = WorldstateModel()
        print(f"✓ Can create instance: {instance}")
        print(f"  - Type: {type(instance)}")
        
        # Check field values
        print(f"  - Version field: {getattr(instance, 'version', 'Not found')}")
        print(f"  - WorldSeed field: {getattr(instance, 'world_seed', 'Not found')}")
        
    except Exception as e:
        print(f"✗ Cannot create instance: {e}")
    
    # Check the field definitions
    print(f"\nChecking field definitions...")
    import inspect
    
    try:
        signature = inspect.signature(WorldstateModel)
        print(f"Signature: {signature}")
        
        for name, param in signature.parameters.items():
            print(f"  - {name}: {param}")
            
    except Exception as e:
        print(f"✗ Cannot get signature: {e}")

def test_field_mapping():
    """Test if the field mapping is the issue."""
    print(f"\n🔍 Testing field mapping...")
    
    # Create a model with explicit field mapping
    class TestModel(msgspec.Struct):
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

async def main():
    """Main test function."""
    print("🔧 Testing msgspec setup and field mapping")
    print("=" * 60)
    
    # Test simple model
    simple_success = test_simple_model()
    
    # Check msgspec setup
    check_msgspec_issue()
    
    # Test field mapping
    mapping_success = test_field_mapping()
    
    # Summary
    print(f"\n📊 Test Results:")
    print("=" * 40)
    print(f"Simple model: {'✓ PASS' if simple_success else '✗ FAIL'}")
    print(f"Field mapping: {'✓ PASS' if mapping_success else '✗ FAIL'}")
    
    if simple_success and mapping_success:
        print(f"\n🎉 Both tests passed!")
        print(f"The issue might be in the complex model structure.")
    else:
        print(f"\n❌ Basic msgspec functionality is failing.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())