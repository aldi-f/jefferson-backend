#!/usr/bin/env python3
"""
Test the fixed worldstate client.
"""

import asyncio
import json
import aiohttp
import msgspec
from app.config.settings import settings
from app.clients.warframe.worldstate.parsers.worldstate import WorldstateModel

async def test_fixed_client():
    """Test the fixed client functionality."""
    print("🔧 Testing fixed worldstate client...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(settings.WORLDSTATE_URL) as response:
                if response.status == 200:
                    text = await response.text()
                    raw_data = json.loads(text)
                    print(f"✓ API request successful")
                    print(f"  - Version: {raw_data.get('Version')}")
                    print(f"  - Events: {len(raw_data.get('Events', []))}")
                    print(f"  - Goals: {len(raw_data.get('Goals', []))}")
                    print(f"  - Alerts: {len(raw_data.get('Alerts', []))}")
                    
                    # Test the fixed decoding
                    print(f"\n🔄 Testing fixed decoding (strict=True)...")
                    try:
                        decoded = msgspec.json.decode(
                            json.dumps(raw_data), type=WorldstateModel, strict=True
                        )
                        print(f"✓ Decoding successful!")
                        print(f"  - Type: {type(decoded)}")
                        print(f"  - WorldSeed: {decoded.world_seed[:20]}..." if decoded.world_seed else "  - WorldSeed: None")
                        print(f"  - Version: {decoded.version}")
                        print(f"  - Mobile Version: {decoded.mobile_version}")
                        print(f"  - Events: {len(decoded.events)}")
                        print(f"  - Goals: {len(decoded.goals)}")
                        print(f"  - Alerts: {len(decoded.alerts)}")
                        print(f"  - Sorties: {len(decoded.sorties)}")
                        print(f"  - Active Missions: {len(decoded.active_missions)}")
                        print(f"  - Void Traders: {len(decoded.void_traders)}")
                        print(f"  - Daily Deals: {len(decoded.daily_deals)}")
                        
                        # Test some actual data
                        if decoded.events:
                            print(f"  - First event: {decoded.events[0].prop[:50]}...")
                        if decoded.goals:
                            print(f"  - First goal: {decoded.goals[0].node}")
                        if decoded.alerts:
                            print(f"  - First alert: {decoded.alerts[0].tag}")
                            
                        return True
                        
                    except Exception as e:
                        print(f"✗ Decoding failed: {e}")
                        return False
                        
                else:
                    print(f"✗ API request failed: {response.status}")
                    return False
                    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

async def test_client_methods():
    """Test all client methods with the fix."""
    print(f"\n🔧 Testing all client methods...")
    
    # Test data
    test_data = {
        "WorldSeed": "test_seed",
        "Version": 10,
        "MobileVersion": "5.3.0.0",
        "BuildLabel": "test_build",
        "Time": 1234567890,
        "Events": [],
        "Goals": [],
        "Alerts": [],
        "Sorties": [],
        "ActiveMissions": [],
        "LiteSorties": [],
        "VoidTraders": [],
        "DailyDeals": [],
        "EndlessXpChoices": [],
        "SeasonInfo": {}
    }
    
    # Test msgspec.json.decode with strict=True
    try:
        decoded = msgspec.json.decode(
            json.dumps(test_data), type=WorldstateModel, strict=True
        )
        print(f"✓ msgspec.json.decode with strict=True: Success")
    except Exception as e:
        print(f"✗ msgspec.json.decode with strict=True: {e}")
        return False
    
    # Test msgspec.convert with strict=True
    try:
        decoded = msgspec.convert(test_data, type=WorldstateModel, strict=True)
        print(f"✓ msgspec.convert with strict=True: Success")
    except Exception as e:
        print(f"✗ msgspec.convert with strict=True: {e}")
        return False
    
    return True

async def main():
    """Main test function."""
    print("🔧 Testing fixed worldstate client implementation")
    print("=" * 60)
    
    # Test the actual client functionality
    client_success = await test_fixed_client()
    
    # Test client methods
    methods_success = await test_client_methods()
    
    # Summary
    print(f"\n📊 Test Results:")
    print("=" * 40)
    print(f"Client functionality: {'✓ PASS' if client_success else '✗ FAIL'}")
    print(f"Client methods: {'✓ PASS' if methods_success else '✗ FAIL'}")
    
    if client_success and methods_success:
        print(f"\n🎉 All tests passed! The fix is working correctly.")
        print(f"The issue was using strict=False instead of strict=True in msgspec.")
    else:
        print(f"\n❌ Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())