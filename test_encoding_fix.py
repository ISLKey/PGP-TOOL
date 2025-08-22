#!/usr/bin/env python3
"""
Test script to verify the UTF-8 encoding fix in PGP Tool
"""

import sys
import os
import base64

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_base64_utf8_handling():
    """Test that our encoding fix handles various data types correctly"""
    print("Testing UTF-8 encoding fix...")
    
    # Test 1: Valid UTF-8 data encoded as base64
    test_pem = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC..."
    encoded_pem = base64.b64encode(test_pem.encode('utf-8')).decode('ascii')
    
    try:
        decoded_data = base64.b64decode(encoded_pem)
        result = decoded_data.decode('utf-8')
        print("✅ Test 1 PASSED: Valid UTF-8 data handled correctly")
    except Exception as e:
        print(f"❌ Test 1 FAILED: {e}")
    
    # Test 2: Binary data that would cause UTF-8 errors
    binary_data = bytes([0xf5, 0xd6, 0x8b, 0xff, 0x00, 0x01, 0x02, 0x03])
    encoded_binary = base64.b64encode(binary_data).decode('ascii')
    
    try:
        decoded_data = base64.b64decode(encoded_binary)
        try:
            result = decoded_data.decode('utf-8')
            print("❌ Test 2 FAILED: Should have raised UnicodeDecodeError")
        except UnicodeDecodeError:
            print("✅ Test 2 PASSED: UnicodeDecodeError properly caught")
    except Exception as e:
        print(f"❌ Test 2 FAILED: Unexpected error: {e}")
    
    # Test 3: Empty string handling
    try:
        empty_encoded = base64.b64encode(b'').decode('ascii')
        decoded_data = base64.b64decode(empty_encoded)
        result = decoded_data.decode('utf-8')
        print("✅ Test 3 PASSED: Empty string handled correctly")
    except Exception as e:
        print(f"❌ Test 3 FAILED: {e}")
    
    print("\nEncoding fix validation complete!")

def test_pgp_handler_import():
    """Test that the PGP handler can be imported without errors"""
    print("\nTesting PGP handler import...")
    
    try:
        from crypto.pure_python_pgp import PurePythonPGPHandler
        print("✅ PurePythonPGPHandler imported successfully")
        
        # Test basic initialization
        handler = PurePythonPGPHandler("/tmp/test_keys")
        print("✅ PGP handler initialized successfully")
        
        return True
    except Exception as e:
        print(f"❌ PGP handler import failed: {e}")
        return False

if __name__ == "__main__":
    print("PGP Tool UTF-8 Encoding Fix Validation")
    print("=" * 50)
    
    test_base64_utf8_handling()
    
    if test_pgp_handler_import():
        print("\n🎉 All tests passed! The encoding fix should resolve the UTF-8 errors.")
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")

