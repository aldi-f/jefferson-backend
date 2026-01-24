#!/usr/bin/env python3
"""
Test the actual URL used by the worldstate client.
"""

import asyncio
import aiohttp
import json
from app.config.settings import settings

async def test_actual_url():
    """Test the actual WORLDSTATE_URL from settings."""
    print(f"🔍 Testing URL: {settings.WORLDSTATE_URL}")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test without parameters
            print("\n1. Testing basic request...")
            async with session.get(settings.WORLDSTATE_URL) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    text = await response.text()
                    print(f"   Response length: {len(text)}")
                    print(f"   Response (first 200 chars): {text[:200]}")
                    
                    # Try to parse as JSON
                    try:
                        data = json.loads(text)
                        print(f"   ✓ Parsed successfully as JSON")
                        print(f"   Data type: {type(data)}")
                        
                        if isinstance(data, dict):
                            print(f"   Keys: {list(data.keys())}")
                            if "Version" in data:
                                print(f"   ✓ Found 'Version' field")
                                print(f"   Version: {data['Version']}")
                            else:
                                print(f"   ⚠ No 'Version' field found")
                        elif isinstance(data, list):
                            print(f"   Array with {len(data)} items")
                            
                    except json.JSONDecodeError as e:
                        print(f"   ✗ Not valid JSON: {e}")
                else:
                    print(f"   ✗ Request failed")
            
            # Test with User-Agent
            print("\n2. Testing with User-Agent...")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            async with session.get(settings.WORLDSTATE_URL, headers=headers) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    text = await response.text()
                    print(f"   Response length: {len(text)}")
                    print(f"   Response (first 200 chars): {text[:200]}")
                else:
                    print(f"   ✗ Request failed")
                    
    except Exception as e:
        print(f"✗ Error testing URL: {e}")

async def test_alternative_urls():
    """Test some alternative URLs that might work."""
    alternative_urls = [
        "https://api.warframestat.us/pc",
        "https://api.warframestat.us",
        "https://raw.githubusercontent.com/WFCD/warframe-public-data/master/data/worldstate.json"
    ]
    
    print(f"\n🔍 Testing alternative URLs...")
    
    for url in alternative_urls:
        print(f"\nTesting: {url}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    print(f"   Status: {response.status}")
                    if response.status == 200:
                        text = await response.text()
                        print(f"   Response length: {len(text)}")
                        
                        # Try to parse as JSON
                        try:
                            data = json.loads(text)
                            print(f"   ✓ Parsed successfully as JSON")
                            
                            if isinstance(data, dict):
                                print(f"   Keys: {list(data.keys())}")
                                if "Version" in data or "timestamp" in data:
                                    print(f"   ✓ Looks like worldstate data")
                            elif isinstance(data, list):
                                print(f"   Array with {len(data)} items")
                                
                        except json.JSONDecodeError as e:
                            print(f"   ✗ Not valid JSON: {e}")
                    else:
                        print(f"   ✗ Request failed")
        except Exception as e:
            print(f"   ✗ Error: {e}")

async def main():
    """Main test function."""
    print("🔍 Testing worldstate client URL and alternatives")
    print("=" * 60)
    
    await test_actual_url()
    await test_alternative_urls()
    
    print("\n" + "=" * 60)
    print("📝 Summary: Check which URL returns the expected structure")

if __name__ == "__main__":
    asyncio.run(main())