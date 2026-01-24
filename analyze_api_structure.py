#!/usr/bin/env python3
"""
Analyze the actual API response structure and create the correct msgspec.
"""

import asyncio
import json
import aiohttp
from pathlib import Path

async def get_actual_api_structure():
    """Get the actual API response structure."""
    test_url = "https://api.warframestat.us/pc"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(test_url) as response:
                if response.status == 200:
                    raw_text = await response.text()
                    data = json.loads(raw_text)
                    return data
                else:
                    print(f"HTTP error: {response.status}")
                    return None
    except Exception as e:
        print(f"Request error: {e}")
        return None

def analyze_structure(data, indent=0):
    """Recursively analyze the structure of the API response."""
    prefix = "  " * indent
    if isinstance(data, dict):
        print(f"{prefix}Dictionary with {len(data)} keys:")
        for key, value in data.items():
            print(f"{prefix}  - {key}: {type(value).__name__}", end="")
            if isinstance(value, (list, dict)) and len(value) > 0:
                print(f" (length: {len(value)})")
                if isinstance(value, list) and len(value) > 0:
                    analyze_structure(value[0], indent + 2)
                elif isinstance(value, dict):
                    analyze_structure(value, indent + 2)
            else:
                print()
    elif isinstance(data, list):
        print(f"{prefix}List with {len(data)} items:")
        if data:
            analyze_structure(data[0], indent + 1)
    else:
        print(f"{prefix}Value: {data}")

async def main():
    """Main analysis function."""
    print("🔍 Analyzing actual Warframe API structure...")
    
    # Get the actual API response
    data = await get_actual_api_structure()
    
    if data:
        print("\n📊 API Response Structure Analysis:")
        print("=" * 50)
        
        # Top-level structure
        print("\n📋 Top-level fields:")
        for key, value in data.items():
            print(f"  - {key}: {type(value).__name__}", end="")
            if isinstance(value, (list, dict)):
                print(f" ({len(value)} items)")
            else:
                print()
        
        # Analyze a few key structures
        print("\n🔍 Detailed analysis of key structures:")
        
        # News structure (what we call Events)
        if "news" in data and data["news"]:
            print("\n📰 News structure (our 'Events'):")
            analyze_structure(data["news"][0])
        
        # Alerts structure
        if "alerts" in data and data["alerts"]:
            print("\n🚨 Alerts structure:")
            analyze_structure(data["alerts"][0])
        
        # Fissures structure (our ActiveMissions)
        if "fissures" in data and data["fissures"]:
            print("\n🌀 Fissures structure (our 'ActiveMissions'):")
            analyze_structure(data["fissures"][0])
        
        # Sortie structure
        if "sortie" in data and data["sortie"]:
            print("\n🚀 Sortie structure:")
            analyze_structure(data["sortie"])
        
        print("\n" + "=" * 50)
        print("📝 Summary: The API uses different field names and structures!")
        
    else:
        print("❌ Could not fetch API data.")

if __name__ == "__main__":
    asyncio.run(main())