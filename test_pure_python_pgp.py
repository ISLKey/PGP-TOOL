#!/usr/bin/env python3
"""
Test script for Pure Python PGP implementation
Tests the fixed version without GPG dependency
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing module imports...")
    
    try:
        from crypto.pure_python_pgp import PurePythonPGPHandler
        print("✓ PurePythonPGPHandler imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import PurePythonPGPHandler: {e}")
        return False
    
    try:
        from crypto.pgp_handler import PGPHandler
        print("✓ PGPHandler imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import PGPHandler: {e}")
        return False
    
    try:
        from crypto.key_generator import SecureKeyGenerator
        print("✓ SecureKeyGenerator imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import SecureKeyGenerator: {e}")
        return False
    
    try:
        from crypto.entropy import EntropyCollector
        print("✓ EntropyCollector imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import EntropyCollector: {e}")
        return False
    
    return True

def test_key_generation():
    """Test key generation functionality"""
    print("\nTesting key generation...")
    
    from crypto.key_generator import SecureKeyGenerator
    
    # Create temporary directory
    test_dir = tempfile.mkdtemp(prefix="pgp_test_")
    
    try:
        generator = SecureKeyGenerator(test_dir)
        
        # Test entropy collection
        entropy_collector = generator.start_entropy_collection(64)  # Small target for testing
        
        # Simulate entropy collection
        for i in range(50):
            entropy_collector.add_mouse_movement(i * 10, i * 15)
            entropy_collector.add_key_press(65 + (i % 26), i * 0.01)
        
        entropy_collector.add_random_text("Test entropy text for key generation")
        
        if not entropy_collector.is_sufficient():
            print("✗ Insufficient entropy collected")
            return False
        
        print("✓ Entropy collection successful")
        
        # Test key generation
        result = generator.generate_key_with_entropy(
            name="Test User",
            email="test@example.com",
            passphrase="test_passphrase_123",
            key_length=2048
        )
        
        if not result['success']:
            print(f"✗ Key generation failed: {result['error']}")
            return False
        
        print(f"✓ Key generation successful: {result['fingerprint']}")
        
        # Test key listing
        public_keys = generator.list_keys(secret=False)
        private_keys = generator.list_keys(secret=True)
        
        if len(public_keys) == 0 or len(private_keys) == 0:
            print("✗ Generated keys not found in keyring")
            return False
        
        print(f"✓ Keys found in keyring: {len(public_keys)} public, {len(private_keys)} private")
        
        generator.cleanup()
        return True
        
    except Exception as e:
        print(f"✗ Key generation test failed: {e}")
        return False
    finally:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

def test_message_encryption():
    """Test message encryption and decryption"""
    print("\nTesting message encryption/decryption...")
    
    from crypto.key_generator import SecureKeyGenerator
    
    # Create temporary directory
    test_dir = tempfile.mkdtemp(prefix="pgp_test_")
    
    try:
        generator = SecureKeyGenerator(test_dir)
        
        # Generate a test key first
        entropy_collector = generator.start_entropy_collection(64)
        for i in range(50):
            entropy_collector.add_mouse_movement(i * 5, i * 7)
        
        key_result = generator.generate_key_with_entropy(
            name="Test User",
            email="test@example.com",
            passphrase="test_passphrase_123",
            key_length=2048
        )
        
        if not key_result['success']:
            print(f"✗ Failed to generate test key: {key_result['error']}")
            return False
        
        fingerprint = key_result['fingerprint']
        
        # Test message encryption
        test_message = "This is a test message for encryption!"
        
        encrypt_result = generator.encrypt_message(test_message, [fingerprint])
        
        if not encrypt_result['success']:
            print(f"✗ Message encryption failed: {encrypt_result['error']}")
            return False
        
        print("✓ Message encryption successful")
        
        # Test message decryption
        encrypted_message = encrypt_result['encrypted_message']
        
        decrypt_result = generator.decrypt_message(encrypted_message, "test_passphrase_123")
        
        if not decrypt_result['success']:
            print(f"✗ Message decryption failed: {decrypt_result['error']}")
            return False
        
        decrypted_message = decrypt_result['decrypted_message']
        
        if decrypted_message != test_message:
            print("✗ Decrypted message doesn't match original")
            return False
        
        print("✓ Message decryption successful")
        
        generator.cleanup()
        return True
        
    except Exception as e:
        print(f"✗ Message encryption test failed: {e}")
        return False
    finally:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

def test_key_import_export():
    """Test key import and export functionality"""
    print("\nTesting key import/export...")
    
    from crypto.key_generator import SecureKeyGenerator
    
    # Create temporary directory
    test_dir = tempfile.mkdtemp(prefix="pgp_test_")
    
    try:
        generator = SecureKeyGenerator(test_dir)
        
        # Generate a test key
        entropy_collector = generator.start_entropy_collection(64)
        for i in range(50):
            entropy_collector.add_mouse_movement(i * 2, i * 3)
        
        key_result = generator.generate_key_with_entropy(
            name="Export Test User",
            email="export@example.com",
            passphrase="export_passphrase_123",
            key_length=2048
        )
        
        if not key_result['success']:
            print(f"✗ Failed to generate test key: {key_result['error']}")
            return False
        
        fingerprint = key_result['fingerprint']
        
        # Test public key export
        export_result = generator.export_public_key(fingerprint)
        
        if not export_result['success']:
            print(f"✗ Public key export failed: {export_result['error']}")
            return False
        
        public_key_data = export_result['public_key']
        print("✓ Public key export successful")
        
        # Create new generator and test import
        generator.cleanup()
        test_dir2 = tempfile.mkdtemp(prefix="pgp_import_")
        generator2 = SecureKeyGenerator(test_dir2)
        
        # Import public key
        import_result = generator2.import_key(public_key_data)
        
        if not import_result['success']:
            print(f"✗ Public key import failed: {import_result['error']}")
            return False
        
        print("✓ Public key import successful")
        
        # Verify imported keys
        imported_public = generator2.list_keys(secret=False)
        
        if len(imported_public) == 0:
            print("✗ Imported keys not found")
            return False
        
        print("✓ Imported keys verified")
        
        generator2.cleanup()
        if os.path.exists(test_dir2):
            shutil.rmtree(test_dir2)
        
        return True
        
    except Exception as e:
        print(f"✗ Key import/export test failed: {e}")
        return False
    finally:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

def test_gui_startup():
    """Test that the GUI can start without errors"""
    print("\nTesting GUI startup...")
    
    try:
        # Test config import
        import config
        print("✓ Config module imported")
        
        # Test GUI imports
        from gui.main_window import PGPToolMainWindow
        print("✓ Main window class imported")
        
        from gui.dialogs import KeyGenerationDialog, ImportKeyDialog
        print("✓ Dialog classes imported")
        
        # Test main module
        import main
        print("✓ Main module imported")
        
        print("✓ All GUI components can be imported successfully")
        return True
        
    except Exception as e:
        print(f"✗ GUI startup test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Pure Python PGP Implementation - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Key Generation", test_key_generation),
        ("Message Encryption", test_message_encryption),
        ("Key Import/Export", test_key_import_export),
        ("GUI Startup", test_gui_startup)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * len(test_name))
        
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! The pure Python PGP implementation is working correctly.")
        return True
    else:
        print("✗ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

