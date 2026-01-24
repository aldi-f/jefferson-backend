#!/usr/bin/env python3
"""
Debug the specific decoding issue in the worldstate client.
"""

import asyncio
import json
import aiohttp
import msgspec
from pathlib import Path
from app.config.settings import settings
from app.clients.warframe.worldstate.parsers.worldstate import WorldstateModel

async def get_raw_data():
    """Get raw data from the actual client URL."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(settings.WORLDSTATE_URL) as response:
                if response.status == 200:
                    text = await response.text()
                    return json.loads(text)
                else:
                    print(f"HTTP error: {response.status}")
                    return None
    except Exception as e:
        print(f"Request error: {e}")
        return None

def test_decoding_methods(data):
    """Test different decoding methods with the actual data."""
    print(f"\n🔍 Testing decoding with actual API data...")
    print(f"Data type: {type(data)}")
    print(f"Data keys: {list(data.keys())}")
    print(f"Version: {data.get('Version')}")
    
    methods = []
    
    # Method 1: Current client method (json.dumps + decode)
    print(f"\n1. Client method (json.dumps + msgspec.json.decode):")
    try:
        encoded = json.dumps(data)
        decoded = msgspec.json.decode(encoded, type=WorldstateModel, strict=False)
        print(f"   ✓ Success!")
        print(f"   - Type: {type(decoded)}")
        print(f"   - WorldSeed: {decoded.world_seed[:20]}..." if decoded.world_seed else "   - WorldSeed: None")
        print(f"   - Version: {decoded.version}")
        print(f"   - Events: {len(decoded.events)}")
        print(f"   - Goals: {len(decoded.goals)}")
        print(f"   - Alerts: {len(decoded.alerts)}")
        methods.append(("client_method", True, decoded))
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        methods.append(("client_method", False, str(e)))
    
    # Method 2: Direct decode (no json.dumps)
    print(f"\n2. Direct decode (no json.dumps):")
    try:
        decoded = msgspec.json.decode(json.dumps(data), type=WorldstateModel, strict=False)
        print(f"   ✓ Success!")
        print(f"   - Type: {type(decoded)}")
        print(f"   - WorldSeed: {decoded.world_seed[:20]}..." if decoded.world_seed else "   - WorldSeed: None")
        print(f"   - Version: {decoded.version}")
        print(f"   - Events: {len(decoded.events)}")
        print(f"   - Goals: {len(decoded.goals)}")
        print(f"   - Alerts: {len(decoded.alerts)}")
        methods.append(("direct_decode", True, decoded))
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        methods.append(("direct_decode", False, str(e)))
    
    # Method 3: msgspec.convert
    print(f"\n3. msgspec.convert:")
    try:
        decoded = msgspec.convert(data, type=WorldstateModel, strict=False)
        print(f"   ✓ Success!")
        print(f"   - Type: {type(decoded)}")
        print(f"   - WorldSeed: {decoded.world_seed[:20]}..." if decoded.world_seed else "   - WorldSeed: None")
        print(f"   - Version: {decoded.version}")
        print(f"   - Events: {len(decoded.events)}")
        print(f"   - Goals: {len(decoded.goals)}")
        print(f"   - Alerts: {len(decoded.alerts)}")
        methods.append(("msgspec_convert", True, decoded))
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        methods.append(("msgspec_convert", False, str(e)))
    
    # Method 4: strict=True
    print(f"\n4. strict=True:")
    try:
        decoded = msgspec.json.decode(json.dumps(data), type=WorldstateModel, strict=True)
        print(f"   ✓ Success!")
        print(f"   - Type: {type(decoded)}")
        methods.append(("strict_true", True, decoded))
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        methods.append(("strict_true", False, str(e)))
    
    return methods

def inspect_model():
    """Inspect the WorldstateModel to check for issues."""
    print(f"\n🔍 Inspecting WorldstateModel...")
    print(f"Model: {WorldstateModel}")
    print(f"Annotations: {WorldstateModel.__annotations__}")
    
    # Check field mappings
    import inspect
    fields = inspect.signature(WorldstateModel).parameters
    print(f"Fields: {list(fields.keys())}")
    
    # Check if all required fields are present
    required_fields = ['world_seed', 'version', 'mobile_version', 'build_label', 'time']
    for field in required_fields:
        if field in WorldstateModel.__annotations__:
            print(f"   ✓ {field}")
        else:
            print(f"   ✗ {field} missing")

async def main():
    """Main debug function."""
    print("🔍 Debugging worldstate client decoding issue")
    print("=" * 60)
    
    # Inspect the model
    inspect_model()
    
    # Get actual data
    print(f"\n📡 Fetching actual API data...")
    data = await get_raw_data()
    
    if data:
        # Test different decoding methods
        methods = test_decoding_methods(data)
        
        # Summary
        print(f"\n📊 Summary:")
        print("=" * 40)
        for method_name, success, result in methods:
            status = "✓" if success else "✗"
            if success:
                print(f"{status} {method_name}: Success")
            else:
                print(f"{status} {method_name}: {result}")
        
        # Find the working method
        working_methods = [name for name, success, _ in methods if success]
        if working_methods:
            print(f"\n🎯 Working methods: {working_methods}")
            print("The issue might be in the client implementation.")
        else:
            print(f"\n❌ No working methods found - issue is in msgspec definition")
            
    else:
        print(f"\n❌ Could not fetch API data")

if __name__ == "__main__":
    asyncio.run(main())