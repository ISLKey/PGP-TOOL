#!/usr/bin/env python3
"""
Comprehensive diagnostic tool to understand key storage and retrieval issues
"""

import sys
import os
import json
import glob

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def diagnose_key_storage():
    """Comprehensive diagnosis of key storage and retrieval"""
    print("🔍 PGP Tool Key Storage Diagnostic")
    print("=" * 60)
    
    # Step 1: Check file system for key storage
    print("1. CHECKING FILE SYSTEM FOR KEY STORAGE")
    print("-" * 40)
    
    # Look for common key storage locations
    possible_locations = [
        os.path.expanduser("~/.pgp_tool"),
        os.path.expanduser("~/.gnupg"),
        os.path.join(os.getcwd(), "data"),
        os.path.join(os.getcwd(), "data_storage"),
        os.path.join(os.getcwd(), "keys"),
        "/tmp/pgp_tool",
        "/tmp/gnupg"
    ]
    
    found_locations = []
    for location in possible_locations:
        if os.path.exists(location):
            found_locations.append(location)
            print(f"   ✅ Found: {location}")
            
            # List contents
            try:
                contents = os.listdir(location)
                if contents:
                    print(f"      Contents: {', '.join(contents[:10])}")  # Show first 10 items
                    if len(contents) > 10:
                        print(f"      ... and {len(contents) - 10} more items")
                else:
                    print("      (empty directory)")
            except PermissionError:
                print("      (permission denied)")
        else:
            print(f"   ❌ Not found: {location}")
    
    # Step 2: Check for JSON key files
    print("\n2. SEARCHING FOR JSON KEY FILES")
    print("-" * 40)
    
    json_patterns = [
        "**/*keys*.json",
        "**/*public*.json", 
        "**/*private*.json",
        "**/keys.json",
        "**/public_keys.json",
        "**/private_keys.json"
    ]
    
    found_json_files = []
    for pattern in json_patterns:
        files = glob.glob(pattern, recursive=True)
        for file in files:
            if file not in found_json_files:
                found_json_files.append(file)
                print(f"   ✅ Found JSON file: {file}")
                
                # Try to read and analyze
                try:
                    with open(file, 'r') as f:
                        data = json.load(f)
                    
                    if isinstance(data, dict):
                        print(f"      Structure: {list(data.keys())}")
                        
                        # Check for key data
                        for key, value in data.items():
                            if isinstance(value, dict):
                                print(f"      {key}: {len(value)} items")
                            elif isinstance(value, list):
                                print(f"      {key}: {len(value)} items")
                            else:
                                print(f"      {key}: {type(value).__name__}")
                    else:
                        print(f"      Type: {type(data).__name__}")
                        
                except Exception as e:
                    print(f"      Error reading: {e}")
    
    if not found_json_files:
        print("   ❌ No JSON key files found")
    
    # Step 3: Test key generator initialization
    print("\n3. TESTING KEY GENERATOR INITIALIZATION")
    print("-" * 40)
    
    try:
        from crypto.key_generator import SecureKeyGenerator
        
        # Try different initialization methods
        init_methods = [
            ("Default home", os.path.expanduser("~/.pgp_tool")),
            ("Current directory", os.path.join(os.getcwd(), "data_storage")),
            ("Temp directory", "/tmp/pgp_tool_test")
        ]
        
        for method_name, gnupg_home in init_methods:
            print(f"   Testing {method_name}: {gnupg_home}")
            try:
                key_gen = SecureKeyGenerator(gnupg_home)
                print(f"      ✅ Initialization successful")
                
                # Test key listing
                try:
                    public_keys = key_gen.list_keys(secret=False)
                    private_keys = key_gen.list_keys(secret=True)
                    print(f"      📊 Public keys: {len(public_keys)}")
                    print(f"      📊 Private keys: {len(private_keys)}")
                    
                    if private_keys:
                        print("      🔑 Private key details:")
                        for i, key in enumerate(private_keys[:3]):  # Show first 3
                            uids = key.get('uids', key.get('user_ids', ['Unknown']))
                            fingerprint = key.get('fingerprint', key.get('key_id', 'No fingerprint'))
                            print(f"         {i+1}. {uids[0] if isinstance(uids, list) else uids}")
                            print(f"            Fingerprint: {fingerprint}")
                    
                except Exception as e:
                    print(f"      ❌ Key listing failed: {e}")
                    
            except Exception as e:
                print(f"      ❌ Initialization failed: {e}")
    
    except Exception as e:
        print(f"   ❌ Failed to import SecureKeyGenerator: {e}")
    
    # Step 4: Test PGP handler directly
    print("\n4. TESTING PGP HANDLER DIRECTLY")
    print("-" * 40)
    
    try:
        from crypto.pgp_handler import PGPHandler
        
        # Try different initialization methods
        for method_name, gnupg_home in init_methods:
            print(f"   Testing PGP handler with {method_name}: {gnupg_home}")
            try:
                pgp_handler = PGPHandler(gnupg_home)
                print(f"      ✅ PGP handler initialization successful")
                
                # Test key listing
                try:
                    public_result = pgp_handler.list_keys(secret=False)
                    private_result = pgp_handler.list_keys(secret=True)
                    
                    print(f"      📊 Public keys result: {public_result}")
                    print(f"      📊 Private keys result: {private_result}")
                    
                    if private_result and private_result.get('success'):
                        private_keys = private_result.get('keys', [])
                        print(f"      🔑 Found {len(private_keys)} private keys via PGP handler")
                        
                        for i, key in enumerate(private_keys[:3]):
                            uids = key.get('uids', key.get('user_ids', ['Unknown']))
                            fingerprint = key.get('fingerprint', key.get('key_id', 'No fingerprint'))
                            print(f"         {i+1}. {uids[0] if isinstance(uids, list) else uids}")
                            print(f"            Fingerprint: {fingerprint}")
                    
                except Exception as e:
                    print(f"      ❌ PGP handler key listing failed: {e}")
                    
            except Exception as e:
                print(f"      ❌ PGP handler initialization failed: {e}")
    
    except Exception as e:
        print(f"   ❌ Failed to import PGPHandler: {e}")
    
    # Step 5: Check main window key generator
    print("\n5. TESTING MAIN WINDOW KEY GENERATOR")
    print("-" * 40)
    
    try:
        # Try to simulate how the main window initializes the key generator
        print("   Simulating main window initialization...")
        
        # This is how the main window typically initializes
        from crypto.key_generator import SecureKeyGenerator
        import tempfile
        
        # Use the same logic as the main window
        gnupg_home = os.path.expanduser("~/.pgp_tool")
        if not os.path.exists(gnupg_home):
            os.makedirs(gnupg_home, exist_ok=True)
            
        key_gen = SecureKeyGenerator(gnupg_home)
        print(f"      ✅ Main window style initialization successful")
        print(f"      📁 Using directory: {gnupg_home}")
        
        # Test the exact methods used by refresh_chat_profiles
        try:
            private_keys = key_gen.list_keys(secret=True)
            print(f"      📊 list_keys(secret=True): {len(private_keys)} keys")
            
            if hasattr(key_gen, 'pgp_handler'):
                pgp_result = key_gen.pgp_handler.list_keys(secret=True)
                print(f"      📊 pgp_handler.list_keys(secret=True): {pgp_result}")
            else:
                print(f"      ❌ No pgp_handler attribute found")
                
        except Exception as e:
            print(f"      ❌ Key listing failed: {e}")
            
    except Exception as e:
        print(f"   ❌ Main window simulation failed: {e}")
    
    # Step 6: Summary and recommendations
    print("\n6. SUMMARY AND RECOMMENDATIONS")
    print("-" * 40)
    
    print("   📋 Findings:")
    print(f"      • Found {len(found_locations)} potential key storage locations")
    print(f"      • Found {len(found_json_files)} JSON key files")
    
    print("\n   💡 Recommendations:")
    if not found_locations:
        print("      • No key storage directories found - keys may not be persisting")
    if not found_json_files:
        print("      • No JSON key files found - check key storage implementation")
    
    print("\n   🔧 Next Steps:")
    print("      1. Check if keys are being saved to the correct location")
    print("      2. Verify the key generation process is working")
    print("      3. Ensure the chat system is looking in the right place")
    print("      4. Test with a fresh key generation and immediate profile refresh")

if __name__ == "__main__":
    diagnose_key_storage()

