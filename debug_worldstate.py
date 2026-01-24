#!/usr/bin/env python3
"""
Debug script to understand the worldstate API response and msgspec decoding issue.
"""

import asyncio
import json
import logging
import aiohttp
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def debug_worldstate_response():
    """Debug the actual worldstate API response."""
    
    # Use the URL from settings if available, otherwise use a known working URL
    test_url = "https://api.warframestat.us/pc"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(test_url) as response:
                logger.info(f"Response status: {response.status}")
                
                if response.status == 200:
                    # Get raw text
                    raw_text = await response.text()
                    logger.info(f"Raw response length: {len(raw_text)}")
                    logger.info(f"Raw response (first 500 chars): {raw_text[:500]}")
                    
                    # Try to parse as JSON
                    try:
                        data = json.loads(raw_text)
                        logger.info(f"Successfully parsed JSON")
                        logger.info(f"JSON keys: {list(data.keys())}")
                        
                        # Check if it's the expected structure
                        if "Version" in data:
                            logger.info("✓ Found 'Version' field - looks like worldstate data")
                            logger.info(f"Version: {data.get('Version')}")
                            logger.info(f"Events count: {len(data.get('Events', []))}")
                            logger.info(f"Goals count: {len(data.get('Goals', []))}")
                            logger.info(f"Alerts count: {len(data.get('Alerts', []))}")
                        else:
                            logger.warning("⚠ 'Version' field not found - might be different structure")
                            logger.info(f"Top level keys: {list(data.keys())}")
                        
                        return data
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error: {e}")
                        logger.error(f"Response text: {raw_text}")
                        return None
                else:
                    logger.error(f"HTTP error: {response.status}")
                    return None
                    
    except Exception as e:
        logger.error(f"Request error: {e}")
        return None

def test_msgspec_decoding(data):
    """Test msgspec decoding with the actual data."""
    try:
        # Import the worldstate model
        import sys
        sys.path.append(str(Path(__file__).parent))
        
        from app.clients.warframe.worldstate.parsers.worldstate import WorldstateModel
        import msgspec
        from msgspec import json as msgspec_json
        
        logger.info("\n=== Testing msgspec decoding ===")
        
        # Method 1: Direct decoding (what the client should do)
        logger.info("Method 1: Direct msgspec.json.decode()")
        try:
            decoded = msgspec_json.decode(json.dumps(data), type=WorldstateModel, strict=False)
            logger.info(f"✓ Direct decoding successful!")
            logger.info(f"  - Type: {type(decoded)}")
            logger.info(f"  - WorldSeed: {decoded.world_seed[:20]}..." if decoded.world_seed else "  - WorldSeed: None")
            logger.info(f"  - Version: {decoded.version}")
            logger.info(f"  - Events count: {len(decoded.events)}")
            logger.info(f"  - Goals count: {len(decoded.goals)}")
            logger.info(f"  - Alerts count: {len(decoded.alerts)}")
            return decoded
        except Exception as e:
            logger.error(f"✗ Direct decoding failed: {e}")
        
        # Method 2: Using msgspec.convert (alternative)
        logger.info("\nMethod 2: Using msgspec.convert()")
        try:
            decoded = msgspec.convert(data, type=WorldstateModel, strict=False)
            logger.info(f"✓ Convert decoding successful!")
            logger.info(f"  - Type: {type(decoded)}")
            logger.info(f"  - WorldSeed: {decoded.world_seed[:20]}..." if decoded.world_seed else "  - WorldSeed: None")
            logger.info(f"  - Version: {decoded.version}")
            logger.info(f"  - Events count: {len(decoded.events)}")
            logger.info(f"  - Goals count: {len(decoded.goals)}")
            logger.info(f"  - Alerts count: {len(decoded.alerts)}")
            return decoded
        except Exception as e:
            logger.error(f"✗ Convert decoding failed: {e}")
        
        # Method 3: Try with strict=True
        logger.info("\nMethod 3: With strict=True")
        try:
            decoded = msgspec_json.decode(json.dumps(data), type=WorldstateModel, strict=True)
            logger.info(f"✓ Strict decoding successful!")
            return decoded
        except Exception as e:
            logger.error(f"✗ Strict decoding failed: {e}")
            
        return None
        
    except ImportError as e:
        logger.error(f"Could not import WorldstateModel: {e}")
        return None

async def main():
    """Main debug function."""
    logger.info("🔍 Debugging worldstate API response and msgspec decoding")
    
    # Get the actual API response
    logger.info("\n1. Fetching worldstate API response...")
    data = await debug_worldstate_response()
    
    if data:
        logger.info("\n2. Testing msgspec decoding...")
        decoded = test_msgspec_decoding(data)
        
        if decoded:
            logger.info("\n🎉 Success! msgspec decoding works correctly.")
        else:
            logger.error("\n❌ msgspec decoding failed. Check the error messages above.")
    else:
        logger.error("\n❌ Could not fetch worldstate data.")

if __name__ == "__main__":
    asyncio.run(main())