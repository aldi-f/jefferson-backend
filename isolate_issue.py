#!/usr/bin/env python3
"""
Isolate the exact issue with accessing decoded fields.
"""

import asyncio
import json
import aiohttp
import msgspec
from app.config.settings import settings
from app.clients.warframe.worldstate.parsers.worldstate import WorldstateModel

async def get_data():
    """Get data from API."""
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

def test_field_access():
    """Test field access on decoded objects."""
    print("🔍 Testing field access issues...")
    
    # Create a simple test case
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
    
    print("1. Testing with simple data...")
    try:
        decoded = msgspec.json.decode(
            json.dumps(test_data), type=WorldstateModel, strict=True
        )
        print(f"   ✓ Decoding successful")
        print(f"   - Type: {type(decoded)}")
        print(f"   - Version: {decoded.version}")
        print(f"   - WorldSeed: {decoded.world_seed}")
        print(f"   - Events: {len(decoded.events)}")
        print(f"   ✓ All field accesses successful")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    print("\n2. Testing with real API data...")
    data = asyncio.run(get_data())
    if not data:
        print("   ✗ Could not get API data")
        return False
    
    try:
        decoded = msgspec.json.decode(
            json.dumps(data), type=WorldstateModel, strict=True
        )
        print(f"   ✓ Decoding successful")
        print(f"   - Type: {type(decoded)}")
        
        # Try accessing fields one by one
        try:
            version = decoded.version
            print(f"   - Version: {version}")
        except Exception as e:
            print(f"   ✗ Version access failed: {e}")
            return False
        
        try:
            world_seed = decoded.world_seed
            print(f"   - WorldSeed: {world_seed[:20]}..." if world_seed else "   - WorldSeed: None")
        except Exception as e:
            print(f"   ✗ WorldSeed access failed: {e}")
            return False
        
        try:
            events = decoded.events
            print(f"   - Events: {len(events)}")
        except Exception as e:
            print(f"   ✗ Events access failed: {e}")
            return False
        
        try:
            goals = decoded.goals
            print(f"   - Goals: {len(goals)}")
        except Exception as e:
            print(f"   ✗ Goals access failed: {e}")
            return False
        
        try:
            alerts = decoded.alerts
            print(f"   - Alerts: {len(alerts)}")
        except Exception as e:
            print(f"   ✗ Alerts access failed: {e}")
            return False
        
        print(f"   ✓ All field accesses successful")
        return True
        
    except Exception as e:
        print(f"   ✗ Decoding failed: {e}")
        return False

def inspect_event_data():
    """Inspect the structure of event data."""
    print("\n3. Inspecting event data structure...")
    
    data = asyncio.run(get_data())
    if not data or "Events" not in data:
        print("   ✗ No Events data found")
        return False
    
    events = data["Events"]
    if not events:
        print("   ✗ No events in data")
        return False
    
    first_event = events[0]
    print(f"   First event keys: {list(first_event.keys())}")
    print(f"   Event _id: {first_event.get('_id', 'Not found')}")
    
    # Try to parse with Event model
    try:
        from app.clients.warframe.worldstate.parsers.event import Event
        event = Event(**first_event)
        print(f"   ✓ Event parsing successful")
        print(f"   - Messages: {len(event.messages)}")
        print(f"   - Prop: {event.prop}")
        print(f"   - Priority: {event.priority}")
        return True
    except Exception as e:
        print(f"   ✗ Event parsing failed: {e}")
        return False

async def main():
    """Main test function."""
    print("🔍 Isolating field access issues")
    print("=" * 60)
    
    # Test field access
    field_success = test_field_access()
    
    # Inspect event data
    event_success = inspect_event_data()
    
    # Summary
    print(f"\n📊 Test Results:")
    print("=" * 40)
    print(f"Field access: {'✓ PASS' if field_success else '✗ FAIL'}")
    print(f"Event parsing: {'✓ PASS' if event_success else '✗ FAIL'}")
    
    if field_success and event_success:
        print(f"\n🎉 Field access is working correctly!")
        print(f"The issue might be in the client cache handling.")
    else:
        print(f"\n❌ Field access is failing. This is the root issue.")

if __name__ == "__main__":
    asyncio.run(main())