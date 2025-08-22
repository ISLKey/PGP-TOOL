#!/usr/bin/env python3
"""
Test script to validate the chat profile selector fix
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_profile_selector():
    """Test the profile selector functionality"""
    print("🔍 Testing Chat Profile Selector Fix")
    print("=" * 50)
    
    try:
        # Test 1: Import required modules
        print("1. Testing module imports...")
        from crypto.key_generator import SecureKeyGenerator
        from gui.main_window import PGPToolMainWindow
        print("   ✅ Module imports successful")
        
        # Test 2: Create key generator
        print("2. Testing key generator creation...")
        import tempfile
        import os
        gnupg_home = os.path.join(tempfile.gettempdir(), "pgp_test")
        key_gen = SecureKeyGenerator(gnupg_home)
        print("   ✅ Key generator created")
        
        # Test 3: List private keys
        print("3. Testing private key listing...")
        try:
            private_keys = key_gen.list_keys(secret=True)
            print(f"   ✅ Found {len(private_keys)} private keys")
            
            if private_keys:
                print("   📋 Private key details:")
                for i, key in enumerate(private_keys):
                    uids = key.get('uids', ['Unknown'])
                    fingerprint = key.get('fingerprint', 'No fingerprint')
                    print(f"      {i+1}. {uids[0]} ({fingerprint[-8:]})")
            else:
                print("   ⚠️  No private keys found - this explains the empty dropdown!")
                
        except Exception as e:
            print(f"   ❌ Error listing private keys: {e}")
            
        # Test 4: Test PGP handler directly
        print("4. Testing PGP handler key listing...")
        try:
            if hasattr(key_gen, 'pgp_handler'):
                pgp_result = key_gen.pgp_handler.list_keys(secret=True)
                if pgp_result and pgp_result.get('success'):
                    pgp_keys = pgp_result.get('keys', [])
                    print(f"   ✅ PGP handler found {len(pgp_keys)} private keys")
                    
                    if pgp_keys:
                        print("   📋 PGP handler key details:")
                        for i, key in enumerate(pgp_keys):
                            uids = key.get('uids', key.get('user_ids', ['Unknown']))
                            fingerprint = key.get('fingerprint', key.get('key_id', 'No fingerprint'))
                            print(f"      {i+1}. {uids[0] if isinstance(uids, list) else uids} ({fingerprint[-8:] if fingerprint else 'N/A'})")
                else:
                    print(f"   ❌ PGP handler failed: {pgp_result}")
            else:
                print("   ❌ No PGP handler found")
                
        except Exception as e:
            print(f"   ❌ Error with PGP handler: {e}")
            
        # Test 5: Simulate profile creation
        print("5. Testing profile creation logic...")
        try:
            # Get keys using the same logic as the fixed method
            private_keys = key_gen.list_keys(secret=True)
            if not private_keys and hasattr(key_gen, 'pgp_handler'):
                pgp_result = key_gen.pgp_handler.list_keys(secret=True)
                if pgp_result and pgp_result.get('success'):
                    private_keys = pgp_result.get('keys', [])
            
            profiles = []
            for key in private_keys:
                # Extract name from user ID with better parsing
                uids = key.get('uids', [])
                if not uids:
                    uids = key.get('user_ids', [])
                
                if uids:
                    user_id = uids[0] if isinstance(uids, list) else str(uids)
                else:
                    user_id = 'Unknown User'
                
                # Parse name from user ID
                if '<' in user_id and '>' in user_id:
                    name = user_id.split('<')[0].strip()
                    if not name:
                        email_part = user_id.split('<')[1].split('>')[0]
                        name = email_part.split('@')[0] if '@' in email_part else email_part
                else:
                    name = user_id.strip()
                
                # Get fingerprint
                fingerprint = key.get('fingerprint', '')
                if not fingerprint:
                    fingerprint = key.get('key_id', '')
                
                if fingerprint:
                    short_fp = fingerprint[-8:] if len(fingerprint) >= 8 else fingerprint
                    profile_display = f"{name} ({short_fp})"
                    profiles.append(profile_display)
            
            print(f"   ✅ Created {len(profiles)} profiles")
            if profiles:
                print("   📋 Profile dropdown would show:")
                for i, profile in enumerate(profiles):
                    print(f"      {i+1}. {profile}")
            else:
                print("   ⚠️  No profiles created - dropdown would be empty")
                
        except Exception as e:
            print(f"   ❌ Error creating profiles: {e}")
            
        print("\n" + "=" * 50)
        
        if profiles:
            print("🎉 Profile selector should work correctly!")
            print("   The dropdown will be populated with your key pairs.")
        else:
            print("⚠️  Profile selector will be empty because no private keys were found.")
            print("   This could mean:")
            print("   - No key pairs have been generated yet")
            print("   - Keys are stored in a different location")
            print("   - There's an issue with key storage/retrieval")
            
        return len(profiles) > 0
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_profile_selector()
    sys.exit(0 if success else 1)

