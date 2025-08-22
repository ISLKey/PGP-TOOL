#!/usr/bin/env python3
"""
Decryption Debug Test for PGP Tool v4.2.0
Tests the decryption process to identify why messages fail to decrypt
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crypto.pure_python_pgp import PurePythonPGPHandler
from security.data_encryption import SecureDataManager
import json

def test_decryption_debug():
    """Test decryption with detailed debugging"""
    print("=== PGP Tool v4.2.0 - Decryption Debug Test ===")
    print()
    
    try:
        # Initialize data manager (simulating login)
        data_dir = os.path.join(os.path.dirname(__file__), "data_storage")
        data_manager = SecureDataManager(data_dir)
        
        # Initialize PGP handler
        gnupg_home = os.path.join(os.path.dirname(__file__), "data_storage")
        pgp_handler = PurePythonPGPHandler(gnupg_home=gnupg_home, master_password="")
        
        print("1. Testing key listing...")
        private_keys = pgp_handler.list_keys(secret=True)
        public_keys = pgp_handler.list_keys(secret=False)
        
        print(f"   Private keys found: {len(private_keys)}")
        print(f"   Public keys found: {len(public_keys)}")
        
        if private_keys:
            for i, key in enumerate(private_keys):
                print(f"   Private Key {i+1}: {key.get('fingerprint', 'N/A')}")
        
        if public_keys:
            for i, key in enumerate(public_keys):
                print(f"   Public Key {i+1}: {key.get('fingerprint', 'N/A')}")
        
        print()
        print("2. Testing message format...")
        
        # Create a test encrypted message
        if len(private_keys) > 0 and len(public_keys) > 0:
            test_message = "Hello, this is a test message for decryption debugging!"
            
            print(f"   Original message: {test_message}")
            
            # Try to encrypt with the first public key
            public_key_fp = public_keys[0]['fingerprint']
            print(f"   Encrypting with public key: {public_key_fp}")
            
            encrypt_result = pgp_handler.encrypt_message(test_message, public_key_fp)
            
            if encrypt_result and encrypt_result.get('success'):
                encrypted_message = encrypt_result['encrypted_message']
                print(f"   Encryption successful!")
                print(f"   Encrypted message length: {len(encrypted_message)}")
                print(f"   Encrypted message preview: {encrypted_message[:100]}...")
                
                print()
                print("3. Testing decryption...")
                
                # Try to decrypt with empty passphrase
                print("   Trying decryption with empty passphrase...")
                decrypt_result = pgp_handler.decrypt_message(encrypted_message, "")
                
                if decrypt_result and decrypt_result.get('success'):
                    print("   ✅ Decryption successful with empty passphrase!")
                    print(f"   Decrypted message: {decrypt_result['decrypted_message']}")
                else:
                    print(f"   ❌ Decryption failed: {decrypt_result.get('error', 'Unknown error')}")
                    
                    # Try with some common passphrases
                    test_passphrases = ["password", "123456", "test"]
                    for passphrase in test_passphrases:
                        print(f"   Trying decryption with passphrase: {passphrase}")
                        decrypt_result = pgp_handler.decrypt_message(encrypted_message, passphrase)
                        
                        if decrypt_result and decrypt_result.get('success'):
                            print(f"   ✅ Decryption successful with passphrase: {passphrase}")
                            print(f"   Decrypted message: {decrypt_result['decrypted_message']}")
                            break
                    else:
                        print("   ❌ All decryption attempts failed")
                        
                        # Debug the key data
                        print()
                        print("4. Debugging key data...")
                        
                        private_key_fp = private_keys[0]['fingerprint']
                        print(f"   Private key fingerprint: {private_key_fp}")
                        
                        # Check if the keys match
                        if private_key_fp == public_key_fp:
                            print("   ✅ Private and public key fingerprints match")
                        else:
                            print("   ❌ Private and public key fingerprints don't match!")
                            print(f"   Private: {private_key_fp}")
                            print(f"   Public:  {public_key_fp}")
                        
                        # Check key storage format
                        try:
                            key_data = pgp_handler.keys["private_keys"][private_key_fp]
                            print(f"   Private key data keys: {list(key_data.keys())}")
                            
                            if "private_key" in key_data:
                                private_key_str = key_data["private_key"]
                                print(f"   Private key format: {type(private_key_str)}")
                                print(f"   Private key length: {len(private_key_str)}")
                                print(f"   Private key starts with: {private_key_str[:50]}...")
                                
                                if private_key_str.startswith("-----"):
                                    print("   ✅ Private key appears to be in PEM format")
                                else:
                                    print("   ⚠️  Private key appears to be encrypted/encoded")
                            
                        except Exception as e:
                            print(f"   ❌ Error accessing private key data: {e}")
            else:
                print(f"   ❌ Encryption failed: {encrypt_result.get('error', 'Unknown error')}")
        else:
            print("   ⚠️  No keys available for testing")
        
        print()
        print("=== Debug Test Complete ===")
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_decryption_debug()

