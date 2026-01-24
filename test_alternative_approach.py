#!/usr/bin/env python3
"""
Try a completely different approach to fix the msgspec issue.
"""

import json
import msgspec
import asyncio
from app.config.settings import settings

def test_msgspec_convert():
    """Test using msgspec.convert without field mapping."""
    print("🔍 Testing msgspec.convert approach...")
    
    try:
        import aiohttp
        import json
        
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
        
        # Run the async function
        data = asyncio.run(get_data())
        if not data:
            print("✗ Could not fetch data")
            return False
            
        print(f"✓ Got data with {len(data)} keys")
        
        # Create a simple model without field mapping
        class SimpleWorldstate(msgspec.Struct):
            WorldSeed: str
            Version: int
            MobileVersion: str
            BuildLabel: str
            Time: int
            Events: list
            Goals: list
            Alerts: list
            Sorties: list
            ActiveMissions: list
            LiteSorties: list
            VoidTraders: list
            DailyDeals: list
            EndlessXpChoices: list
            SeasonInfo: dict
        
        try:
            # Use msgspec.convert instead of decode
            decoded = msgspec.convert(data, type=SimpleWorldstate, strict=True)
            print(f"✓ msgspec.convert works!")
            print(f"  - Type: {type(decoded)}")
            print(f"  - Version: {decoded.Version}")
            print(f"  - WorldSeed: {decoded.WorldSeed[:20]}...")
            print(f"  - MobileVersion: {decoded.MobileVersion}")
            print(f"  - BuildLabel: {decoded.BuildLabel}")
            print(f"  - Time: {decoded.Time}")
            print(f"  - Events: {len(decoded.Events)}")
            print(f"  - Goals: {len(decoded.Goals)}")
            print(f"  - Alerts: {len(decoded.Alerts)}")
            print(f"  - Sorties: {len(decoded.Sorties)}")
            print(f"  - ActiveMissions: {len(decoded.ActiveMissions)}")
            print(f"  - VoidTraders: {len(decoded.VoidTraders)}")
            print(f"  - DailyDeals: {len(decoded.DailyDeals)}")
            return True
        except Exception as e:
            print(f"✗ msgspec.convert failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_dynamic_struct():
    """Test creating a struct dynamically."""
    print(f"\n🔍 Testing dynamic struct creation...")
    
    try:
        # Create a struct from the data dynamically
        data = {
            "WorldSeed": "test",
            "Version": 10,
            "MobileVersion": "5.3.0.0",
            "BuildLabel": "test",
            "Time": 1234567890
        }
        
        # Create a simple model
        class TestModel(msgspec.Struct):
            WorldSeed: str
            Version: int
            MobileVersion: str
            BuildLabel: str
            Time: int
        
        decoded = msgspec.convert(data, type=TestModel, strict=True)
        print(f"✓ Dynamic struct works!")
        print(f"  - Version: {decoded.Version}")
        print(f"  - WorldSeed: {decoded.WorldSeed}")
        return True
    except Exception as e:
        print(f"✗ Dynamic struct failed: {e}")
        return False

def test_json_decode():
    """Test using msgspec.json.decode directly."""
    print(f"\n🔍 Testing msgspec.json.decode...")
    
    try:
        data = {
            "WorldSeed": "test",
            "Version": 10,
            "MobileVersion": "5.3.0.0",
            "BuildLabel": "test",
            "Time": 1234567890
        }
        
        class TestModel(msgspec.Struct):
            WorldSeed: str
            Version: int
            MobileVersion: str
            BuildLabel: str
            Time: int
        
        decoded = msgspec.json.decode(json.dumps(data), type=TestModel, strict=True)
        print(f"✓ json.decode works!")
        print(f"  - Version: {decoded.Version}")
        print(f"  - WorldSeed: {decoded.WorldSeed}")
        return True
    except Exception as e:
        print(f"✗ json.decode failed: {e}")
        return False

async def main():
    """Main test function."""
    print("🔧 Testing alternative msgspec approaches")
    print("=" * 60)
    
    # Test msgspec.convert
    convert_success = test_msgspec_convert()
    
    # Test dynamic struct
    dynamic_success = test_dynamic_struct()
    
    # Test json decode
    json_success = test_json_decode()
    
    # Summary
    print(f"\n📊 Test Results:")
    print("=" * 40)
    print(f"msgspec.convert: {'✓ PASS' if convert_success else '✗ FAIL'}")
    print(f"Dynamic struct: {'✓ PASS' if dynamic_success else '✗ FAIL'}")
    print(f"json.decode: {'✓ PASS' if json_success else '✗ FAIL'}")
    
    if convert_success:
        print(f"\n🎉 msgspec.convert works!")
        print(f"This is the solution - use msgspec.convert instead of msgspec.json.decode")
        print(f"And make sure the field names in the struct match the JSON field names exactly.")
    else:
        print(f"\n❌ All approaches failed.")

if __name__ == "__main__":
    asyncio.run(main())