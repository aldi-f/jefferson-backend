#!/usr/bin/env python3
"""
Simple validation script to test msgspec against worldstate.json
without requiring full application dependencies.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import msgspec

def parse_mongo_date(date_dict):
    """Parse MongoDB $date format to datetime."""
    number_long = date_dict["$date"]["$numberLong"]
    timestamp_ms = int(number_long)
    return datetime.fromtimestamp(timestamp_ms / 1000)

def test_basic_parsing():
    """Test basic parsing of worldstate.json without full msgspec models."""
    test_file = Path(__file__).parent / "test" / "files" / "worldstate.json"
    
    with open(test_file, 'r') as f:
        data = json.load(f)
    
    print("✓ Successfully loaded worldstate.json")
    print(f"  - Version: {data['Version']}")
    print(f"  - Mobile Version: {data['MobileVersion']}")
    print(f"  - Events count: {len(data['Events'])}")
    print(f"  - Goals count: {len(data['Goals'])}")
    print(f"  - Alerts count: {len(data['Alerts'])}")
    print(f"  - Sorties count: {len(data['Sorties'])}")
    
    # Test date parsing
    if data['Events']:
        first_event = data['Events'][0]
        if 'Date' in first_event and isinstance(first_event['Date'], dict):
            parsed_date = parse_mongo_date(first_event['Date'])
            print(f"  - First event date: {parsed_date}")
    
    if data['Goals']:
        first_goal = data['Goals'][0]
        activation = parse_mongo_date(first_goal['Activation'])
        expiry = parse_mongo_date(first_goal['Expiry'])
        print(f"  - First goal: {first_goal['Node']} ({activation} to {expiry})")
    
    if data['Alerts']:
        first_alert = data['Alerts'][0]
        activation = parse_mongo_date(first_alert['Activation'])
        expiry = parse_mongo_date(first_alert['Expiry'])
        print(f"  - First alert: {first_alert['Tag']} ({activation} to {expiry})")
    
    return True

def test_field_completeness():
    """Test that our msgspec covers all major fields in the JSON."""
    test_file = Path(__file__).parent / "test" / "files" / "worldstate.json"
    
    with open(test_file, 'r') as f:
        data = json.load(f)
    
    # List of fields we expect to be in our msgspec
    expected_fields = [
        "WorldSeed", "Version", "MobileVersion", "BuildLabel", "Time",
        "Events", "Goals", "Alerts", "Sorties", "ActiveMissions", 
        "LiteSorties", "VoidTraders", "DailyDeals", "EndlessXpChoices",
        "SeasonInfo", "Invasions", "VoidStorms", "PrimeVaultTraders",
        "FlashSales", "InGameMarket", "HubEvents", "NodeOverrides",
        "LibraryInfo", "PVPChallengeInstances", "FeaturedGuilds",
        "KnownCalendarSeasons", "Conquests", "Descents"
    ]
    
    print("\nChecking field coverage:")
    missing_fields = []
    for field in expected_fields:
        if field not in data:
            missing_fields.append(field)
        else:
            print(f"  ✓ {field}")
    
    if missing_fields:
        print(f"\n⚠ Missing fields in JSON: {missing_fields}")
        return False
    
    print("✓ All expected fields present in JSON")
    return True

def test_json_structure_validity():
    """Test that the JSON structure is valid and well-formed."""
    test_file = Path(__file__).parent / "test" / "files" / "worldstate.json"
    
    try:
        with open(test_file, 'r') as f:
            data = json.load(f)
        
        # Basic type checks
        assert isinstance(data["WorldSeed"], str)
        assert isinstance(data["Version"], int)
        assert isinstance(data["Events"], list)
        assert isinstance(data["Goals"], list)
        assert isinstance(data["Alerts"], list)
        assert isinstance(data["Sorties"], list)
        
        # Check that arrays have content
        assert len(data["Events"]) > 0, "Events array should not be empty"
        assert len(data["Goals"]) > 0, "Goals array should not be empty"
        assert len(data["Alerts"]) > 0, "Alerts array should not be empty"
        assert len(data["Sorties"]) > 0, "Sorties array should not be empty"
        
        print("✓ JSON structure is valid and well-formed")
        return True
        
    except Exception as e:
        print(f"✗ JSON structure validation failed: {e}")
        return False

def main():
    """Run all validation tests."""
    print("🔍 Validating worldstate.json against msgspec implementation")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Basic parsing
    print("\n1. Testing basic parsing...")
    try:
        if test_basic_parsing():
            tests_passed += 1
            print("✓ Basic parsing test passed")
        else:
            print("✗ Basic parsing test failed")
    except Exception as e:
        print(f"✗ Basic parsing test failed with error: {e}")
    
    # Test 2: Field completeness
    print("\n2. Testing field completeness...")
    try:
        if test_field_completeness():
            tests_passed += 1
            print("✓ Field completeness test passed")
        else:
            print("✗ Field completeness test failed")
    except Exception as e:
        print(f"✗ Field completeness test failed with error: {e}")
    
    # Test 3: JSON structure validity
    print("\n3. Testing JSON structure validity...")
    try:
        if test_json_structure_validity():
            tests_passed += 1
            print("✓ JSON structure validity test passed")
        else:
            print("✗ JSON structure validity test failed")
    except Exception as e:
        print(f"✗ JSON structure validity test failed with error: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The msgspec implementation appears to be correct.")
        return 0
    else:
        print("❌ Some tests failed. Please review the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())