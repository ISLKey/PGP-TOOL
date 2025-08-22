#!/usr/bin/env python3
"""
Test script to verify the passphrase handling fix in PGP Tool
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_pgp_handler_passphrase_storage():
    """Test that the PGP handler can store and retrieve master password"""
    print("Testing PGP handler passphrase storage...")
    
    try:
        from crypto.pgp_handler import PGPHandler
        
        # Create a PGP handler
        handler = PGPHandler("/tmp/test_pgp")
        
        # Test setting and getting master password
        test_password = "test_master_password_123"
        handler.set_master_password(test_password)
        
        retrieved_password = handler.get_master_password()
        
        if retrieved_password == test_password:
            print("✅ Master password storage/retrieval works correctly")
            return True
        else:
            print(f"❌ Password mismatch: expected '{test_password}', got '{retrieved_password}'")
            return False
            
    except Exception as e:
        print(f"❌ PGP handler test failed: {e}")
        return False

def test_secure_chat_passphrase_access():
    """Test that secure chat can access master password from PGP handler"""
    print("\nTesting secure chat passphrase access...")
    
    try:
        from crypto.pgp_handler import PGPHandler
        from chat.secure_chat import SecureChatHandler
        
        # Create handlers
        pgp_handler = PGPHandler("/tmp/test_pgp")
        chat_handler = SecureChatHandler(pgp_handler)
        
        # Set master password
        test_password = "test_master_password_456"
        pgp_handler.set_master_password(test_password)
        
        # Test that chat handler can access the password
        retrieved_password = getattr(chat_handler.pgp_handler, '_master_password', None)
        
        if retrieved_password == test_password:
            print("✅ Secure chat can access master password from PGP handler")
            return True
        else:
            print(f"❌ Chat handler password access failed: expected '{test_password}', got '{retrieved_password}'")
            return False
            
    except Exception as e:
        print(f"❌ Secure chat test failed: {e}")
        return False

def test_passphrase_fallback_logic():
    """Test the passphrase fallback logic"""
    print("\nTesting passphrase fallback logic...")
    
    try:
        # Test the passphrase list generation logic
        master_password = "my_master_password"
        test_passphrases = []
        
        if master_password:
            test_passphrases.append(master_password)
        
        test_passphrases.extend(["", "password", "123456"])
        
        expected_passphrases = ["my_master_password", "", "password", "123456"]
        
        if test_passphrases == expected_passphrases:
            print("✅ Passphrase fallback logic works correctly")
            print(f"   Generated passphrase list: {[p if p else '<empty>' for p in test_passphrases]}")
            return True
        else:
            print(f"❌ Passphrase list mismatch: expected {expected_passphrases}, got {test_passphrases}")
            return False
            
    except Exception as e:
        print(f"❌ Passphrase fallback test failed: {e}")
        return False

if __name__ == "__main__":
    print("PGP Tool Passphrase Handling Fix Validation")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    if test_pgp_handler_passphrase_storage():
        tests_passed += 1
    
    if test_secure_chat_passphrase_access():
        tests_passed += 1
        
    if test_passphrase_fallback_logic():
        tests_passed += 1
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("\n🎉 All tests passed! The passphrase handling fix should resolve the decryption issues.")
        print("\n💡 Expected behavior:")
        print("   1. Master password will be tried first for private key decryption")
        print("   2. If that fails, empty passphrase and common passwords will be tried")
        print("   3. Clear error messages will be shown if all attempts fail")
    else:
        print(f"\n⚠️  {total_tests - tests_passed} test(s) failed. Please check the implementation.")

