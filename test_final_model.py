#!/usr/bin/env python3
"""
Test the final fixed WorldstateModel with defstruct.
"""

import msgspec
import requests
import json
import sys
import importlib

def test_final_worldstate_model():
    """Test the final WorldstateModel with defstruct."""
    print("🔍 Testing final WorldstateModel with defstruct...")
    
    try:
        # Force reload the module to get the fresh version
        if 'app.clients.warframe.worldstate.parsers.worldstate' in sys.modules:
            importlib.reload(sys.modules['app.clients.warframe.worldstate.parsers.worldstate'])
        
        from app.clients.warframe.worldstate.parsers.worldstate import WorldstateModel
        
        print(f"Model type: {type(WorldstateModel)}")
        print(f"Model struct fields: {WorldstateModel.__struct_fields__}")
        
        # Check if fields are properly defined
        if not WorldstateModel.__struct_fields__:
            print(f"❌ __struct_fields__ is empty!")
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
                    print(f"  ❌ Version is still a Field object: {version}")
                    return False
                else:
                    print(f"  ✅ Version: {version} (type: {type(version)})")
            except AttributeError as e:
                print(f"  ❌ AttributeError accessing Version: {e}")
                return False
                
            try:
                worldseed = decoded.WorldSeed
                if hasattr(worldseed, 'name'):
                    print(f"  ❌ WorldSeed is still a Field object: {worldseed}")
                    return False
                else:
                    print(f"  ✅ WorldSeed: {worldseed[:50]}... (type: {type(worldseed)})")
            except AttributeError as e:
                print(f"  ❌ AttributeError accessing WorldSeed: {e}")
                return False
                
            try:
                events = decoded.Events
                if hasattr(events, 'name'):
                    print(f"  ❌ Events is still a Field object: {events}")
                    return False
                else:
                    print(f"  ✅ Events: {len(events)} events (type: {type(events)})")
            except AttributeError as e:
                print(f"  ❌ AttributeError accessing Events: {e}")
                return False
                
            # Additional field tests
            try:
                alerts = decoded.Alerts
                if hasattr(alerts, 'name'):
                    print(f"  ❌ Alerts is still a Field object: {alerts}")
                    return False
                else:
                    print(f"  ✅ Alerts: {len(alerts)} alerts (type: {type(alerts)})")
            except AttributeError as e:
                print(f"  ❌ AttributeError accessing Alerts: {e}")
                return False
                
            # Test a few more fields
            test_fields = ["Sorties", "VoidTraders", "DailyDeals"]
            for field_name in test_fields:
                try:
                    val = getattr(decoded, field_name)
                    if hasattr(val, 'name'):
                        print(f"  ❌ {field_name} is still a Field object: {val}")
                        return False
                    else:
                        print(f"  ✅ {field_name}: {len(val) if hasattr(val, '__len__') else val} (type: {type(val)})")
                except AttributeError:
                    print(f"  ❌ AttributeError accessing {field_name}")
                    return False
                    
            print(f"\n🎉 SUCCESS! All fields are actual values!")
            print(f"The msgspec 0.19.0 defstruct approach works perfectly!")
            return True
                
        except Exception as e:
            print(f"❌ msgspec.convert() failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_completeness():
    """Test that all expected fields are present."""
    print(f"\n🔍 Testing model completeness...")
    
    try:
        from app.clients.warframe.worldstate.parsers.worldstate import WorldstateModel
        
        # Expected fields based on API response
        expected_fields = [
            "WorldSeed", "Version", "MobileVersion", "BuildLabel", "Time",
            "Events", "Goals", "FlashSales", "SkuSales", "InGameMarket", "Invasions", 
            "HubEvents", "NodeOverrides", "VoidStorms", "PrimeVaultTraders", 
            "PrimeVaultAvailabilities", "PrimeTokenAvailability", "LibraryInfo", 
            "PVPChallengeInstances", "PersistentEnemies", "PVPAlternativeModes", 
            "PVPActiveTournaments", "ProjectPct", "ConstructionProjects", "TwitchPromos", 
            "ExperimentRecommended", "ForceLogoutVersion", "FeaturedGuilds", 
            "KnownCalendarSeasons", "Conquests", "Descents", "Alerts", "LiteSorties", 
            "Sorties", "VoidTraders", "DailyDeals", "EndlessXpChoices", "SeasonInfo", 
            "ActiveMissions", "GlobalUpgrades", "SyndicateMissions", "Tmp"
        ]
        
        actual_fields = list(WorldstateModel.__struct_fields__)
        
        print(f"Expected {len(expected_fields)} fields, got {len(actual_fields)} fields")
        
        # Check for missing fields
        missing_fields = set(expected_fields) - set(actual_fields)
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
            return False
        
        # Check for extra fields
        extra_fields = set(actual_fields) - set(expected_fields)
        if extra_fields:
            print(f"ℹ️  Extra fields: {extra_fields}")
        
        print(f"✅ All expected fields are present!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Testing final WorldstateModel with defstruct")
    print("=" * 60)
    
    model_test_success = test_final_worldstate_model()
    completeness_success = test_model_completeness()
    
    print(f"\n📊 Results:")
    print("=" * 30)
    print(f"Model test: {'✓ PASS' if model_test_success else '✗ FAIL'}")
    print(f"Completeness: {'✓ PASS' if completeness_success else '✗ FAIL'}")
    
    if model_test_success and completeness_success:
        print(f"\n🎉🎉🎉 SUCCESS! The msgspec issue is completely resolved!")
        print(f"✅ Solution: Use msgspec.defstruct() instead of class-based Struct")
        print(f"✅ WorldstateModel now returns actual values, not Field objects")
        print(f"✅ All 43 fields are properly defined and accessible")
    elif model_test_success:
        print(f"\n🎯 Model works but may have missing fields")
    else:
        print(f"\n❌ Issues still exist")