#!/usr/bin/env python3
"""
Test different msgspec approaches to find the working one.
"""

import json
import msgspec
from app.config.settings import settings
from app.clients.warframe.worldstate.parsers.worldstate import WorldstateModel

def test_msgspec_versions():
    """Test different msgspec decoding approaches."""
    print("🔍 Testing different msgspec approaches...")
    
    # Get sample data
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
    
    # Test different approaches
    approaches = []
    
    # Approach 1: Using msgspec.json.decode with strict=True
    print(f"\n1. msgspec.json.decode + strict=True:")
    try:
        decoded = msgspec.json.decode(json.dumps(data), type=WorldstateModel, strict=True)
        print(f"   ✓ Decoding successful")
        print(f"   - Type: {type(decoded)}")
        
        # Try to access fields
        try:
            version = decoded.version
            if hasattr(version, '__class__') and 'Field' in str(version.__class__):
                print(f"   ✗ Version is Field object: {version}")
                approaches.append(("json_decode_strict_true", False, "Field object"))
            else:
                print(f"   - Version: {version}")
                approaches.append(("json_decode_strict_true", True, "Success"))
        except Exception as e:
            print(f"   ✗ Field access failed: {e}")
            approaches.append(("json_decode_strict_true", False, str(e)))
            
    except Exception as e:
        print(f"   ✗ Decoding failed: {e}")
        approaches.append(("json_decode_strict_true", False, str(e)))
    
    # Approach 2: Using msgspec.json.decode with strict=False
    print(f"\n2. msgspec.json.decode + strict=False:")
    try:
        decoded = msgspec.json.decode(json.dumps(data), type=WorldstateModel, strict=False)
        print(f"   ✓ Decoding successful")
        print(f"   - Type: {type(decoded)}")
        
        # Try to access fields
        try:
            version = decoded.version
            if hasattr(version, '__class__') and 'Field' in str(version.__class__):
                print(f"   ✗ Version is Field object: {version}")
                approaches.append(("json_decode_strict_false", False, "Field object"))
            else:
                print(f"   - Version: {version}")
                approaches.append(("json_decode_strict_false", True, "Success"))
        except Exception as e:
            print(f"   ✗ Field access failed: {e}")
            approaches.append(("json_decode_strict_false", False, str(e)))
            
    except Exception as e:
        print(f"   ✗ Decoding failed: {e}")
        approaches.append(("json_decode_strict_false", False, str(e)))
    
    # Approach 3: Using msgspec.convert with strict=True
    print(f"\n3. msgspec.convert + strict=True:")
    try:
        decoded = msgspec.convert(data, type=WorldstateModel, strict=True)
        print(f"   ✓ Conversion successful")
        print(f"   - Type: {type(decoded)}")
        
        # Try to access fields
        try:
            version = decoded.version
            if hasattr(version, '__class__') and 'Field' in str(version.__class__):
                print(f"   ✗ Version is Field object: {version}")
                approaches.append(("convert_strict_true", False, "Field object"))
            else:
                print(f"   - Version: {version}")
                approaches.append(("convert_strict_true", True, "Success"))
        except Exception as e:
            print(f"   ✗ Field access failed: {e}")
            approaches.append(("convert_strict_true", False, str(e)))
            
    except Exception as e:
        print(f"   ✗ Conversion failed: {e}")
        approaches.append(("convert_strict_true", False, str(e)))
    
    # Approach 4: Using msgspec.convert with strict=False
    print(f"\n4. msgspec.convert + strict=False:")
    try:
        decoded = msgspec.convert(data, type=WorldstateModel, strict=False)
        print(f"   ✓ Conversion successful")
        print(f"   - Type: {type(decoded)}")
        
        # Try to access fields
        try:
            version = decoded.version
            if hasattr(version, '__class__') and 'Field' in str(version.__class__):
                print(f"   ✗ Version is Field object: {version}")
                approaches.append(("convert_strict_false", False, "Field object"))
            else:
                print(f"   - Version: {version}")
                approaches.append(("convert_strict_false", True, "Success"))
        except Exception as e:
            print(f"   ✗ Field access failed: {e}")
            approaches.append(("convert_strict_false", False, str(e)))
            
    except Exception as e:
        print(f"   ✗ Conversion failed: {e}")
        approaches.append(("convert_strict_false", False, str(e)))
    
    # Approach 5: Try using the model directly without field mapping
    print(f"\n5. Try direct model creation:")
    try:
        # Create a simple model without field mapping
        class SimpleWorldstate(msgspec.Struct):
            world_seed: str
            version: int
            mobile_version: str
            build_label: str
            time: int
        
        decoded = msgspec.json.decode(json.dumps(data), type=SimpleWorldstate, strict=True)
        print(f"   ✓ Simple model successful")
        print(f"   - Type: {type(decoded)}")
        print(f"   - Version: {decoded.version}")
        print(f"   - WorldSeed: {decoded.world_seed[:20]}...")
        approaches.append(("simple_model", True, "Success"))
            
    except Exception as e:
        print(f"   ✗ Simple model failed: {e}")
        approaches.append(("simple_model", False, str(e)))
    
    # Summary
    print(f"\n📊 Results Summary:")
    print("=" * 50)
    for approach, success, result in approaches:
        status = "✓" if success else "✗"
        print(f"{status} {approach}: {result}")
    
    # Find the working approach
    working_approaches = [name for name, success, _ in approaches if success]
    if working_approaches:
        print(f"\n🎯 Working approaches: {working_approaches}")
        return True
    else:
        print(f"\n❌ No working approaches found")
        return False

if __name__ == "__main__":
    test_msgspec_versions()