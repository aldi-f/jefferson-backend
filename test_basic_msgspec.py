#!/usr/bin/env python3
"""
Test basic msgspec functionality to understand the issue.
"""

import msgspec
import json

def test_basic_msgspec():
    """Test basic msgspec functionality."""
    print("🔍 Testing basic msgspec functionality...")
    
    try:
        print(f"Msgspec version: {msgspec.__version__}")
        
        # Test 1: Basic conversion
        print(f"\n1. Basic msgspec.convert() test:")
        data = {"test_field": 42, "another_field": "hello"}
        
        class TestModel(msgspec.Struct):
            test_field: int
            another_field: str
        
        decoded = msgspec.convert(data, type=TestModel, strict=True)
        print(f"   Input: {data}")
        print(f"   Output: {decoded}")
        print(f"   Type: {type(decoded)}")
        print(f"   Dir: {[attr for attr in dir(decoded) if not attr.startswith('_')]}")
        
        if hasattr(decoded, 'test_field'):
            print(f"   ✓ test_field = {decoded.test_field}")
        else:
            print(f"   ✗ No test_field attribute")
            
        # Test 2: JSON decode
        print(f"\n2. msgspec.json.decode() test:")
        json_str = json.dumps(data)
        decoded_json = msgspec.json.decode(json_str, type=TestModel, strict=True)
        print(f"   JSON: {json_str}")
        print(f"   Decoded: {decoded_json}")
        
        if hasattr(decoded_json, 'test_field'):
            print(f"   ✓ test_field = {decoded_json.test_field}")
        else:
            print(f"   ✗ No test_field attribute")
            
        # Test 3: Check struct fields
        print(f"\n3. Struct field inspection:")
        print(f"   Struct fields: {TestModel.__struct_fields__}")
        print(f"   Struct config: {TestModel.__struct_config__}")
        
        # Test 4: Try with different strict setting
        print(f"\n4. Test with strict=False:")
        try:
            decoded_loose = msgspec.convert(data, type=TestModel, strict=False)
            print(f"   Decoded (strict=False): {decoded_loose}")
            if hasattr(decoded_loose, 'test_field'):
                print(f"   ✓ test_field = {decoded_loose.test_field}")
            else:
                print(f"   ✗ No test_field attribute")
        except Exception as e:
            print(f"   ✗ strict=False failed: {e}")
            
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_msgspec_alternatives():
    """Test alternative msgspec approaches."""
    print(f"\n🔍 Testing msgspec alternatives...")
    
    try:
        # Test using msgspec.Decoder
        print(f"\n1. Using msgspec.Decoder:")
        data = {"test_field": 42, "another_field": "hello"}
        
        class TestModel(msgspec.Struct):
            test_field: int
            another_field: str
        
        decoder = msgspec.Decoder(TestModel)
        json_str = json.dumps(data)
        decoded = decoder.decode(json_str)
        
        print(f"   Decoded: {decoded}")
        print(f"   Type: {type(decoded)}")
        
        if hasattr(decoded, 'test_field'):
            print(f"   ✓ test_field = {decoded.test_field}")
        else:
            print(f"   ✗ No test_field attribute")
            
        # Test using struct method
        print(f"\n2. Using struct method:")
        try:
            decoded_struct = TestModel(**data)
            print(f"   Struct creation: {decoded_struct}")
            if hasattr(decoded_struct, 'test_field'):
                print(f"   ✓ test_field = {decoded_struct.test_field}")
            else:
                print(f"   ✗ No test_field attribute")
        except Exception as e:
            print(f"   ✗ Struct creation failed: {e}")
            
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Testing basic msgspec functionality")
    print("=" * 50)
    
    basic_success = test_basic_msgspec()
    alternatives_success = test_msgspec_alternatives()
    
    print(f"\n📊 Results:")
    print("=" * 30)
    print(f"Basic msgspec: {'✓ PASS' if basic_success else '✗ FAIL'}")
    print(f"Alternatives: {'✓ PASS' if alternatives_success else '✗ FAIL'}")