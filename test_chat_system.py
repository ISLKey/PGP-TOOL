#!/usr/bin/env python3
"""
Chat System Validation Test for PGP Tool v4.2.0
Tests all the fixes implemented for the chat system
"""

import os
import sys
import tempfile
import shutil
import time

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

def test_imports():
    """Test that all chat-related modules can be imported"""
    print("🔍 Testing module imports...")
    
    try:
        # Test IRC client import
        from chat.irc_client import PGPIRCClient, IRCNetworks
        print("✅ IRC client import successful")
        
        # Test secure chat import
        from chat.secure_chat import SecureChatHandler, SecureChatContact, SecureChatMessage
        print("✅ Secure chat import successful")
        
        # Test group chat import
        from chat.group_chat import GroupChatHandler, GroupChatRoom, GroupChatMessage
        print("✅ Group chat import successful")
        
        # Test main window import (this will test if all dependencies are resolved)
        from gui.main_window import PGPToolMainWindow
        print("✅ Main window import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_irc_client():
    """Test IRC client basic functionality"""
    print("\n🔍 Testing IRC client...")
    
    try:
        from chat.irc_client import PGPIRCClient, IRCNetworks
        
        # Test IRC client creation
        client = PGPIRCClient()
        print("✅ IRC client creation successful")
        
        # Test network list
        networks = IRCNetworks.get_network_list()
        if networks and len(networks) > 0:
            print(f"✅ Found {len(networks)} predefined networks: {networks}")
        else:
            print("❌ No networks found")
            return False
        
        # Test network info
        network_info = IRCNetworks.get_network_info("libera")
        if network_info:
            print(f"✅ Network info retrieved: {network_info['name']}")
        else:
            print("❌ Failed to get network info")
            return False
        
        # Test nickname generation
        nickname = client.generate_random_nickname()
        if nickname and len(nickname) > 5:
            print(f"✅ Nickname generation successful: {nickname}")
        else:
            print("❌ Nickname generation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ IRC client test failed: {e}")
        return False

def test_secure_chat_handler():
    """Test secure chat handler basic functionality"""
    print("\n🔍 Testing secure chat handler...")
    
    try:
        from chat.secure_chat import SecureChatHandler, SecureChatContact
        from crypto.pgp_handler import PGPHandler
        
        # Create a temporary directory for testing
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create PGP handler
            pgp_handler = PGPHandler(temp_dir)
            print("✅ PGP handler creation successful")
            
            # Create secure chat handler
            chat_handler = SecureChatHandler(pgp_handler)
            print("✅ Secure chat handler creation successful")
            
            # Test contact creation (without actual key import)
            test_contact = SecureChatContact("Test User", "testuser", "1234567890ABCDEF")
            if test_contact.name == "Test User" and test_contact.irc_nickname == "testuser":
                print("✅ Contact creation successful")
            else:
                print("❌ Contact creation failed")
                return False
            
            # Test contact storage
            chat_handler.contacts["testuser"] = test_contact
            retrieved_contact = chat_handler.get_contact("testuser")
            if retrieved_contact and retrieved_contact.name == "Test User":
                print("✅ Contact storage and retrieval successful")
            else:
                print("❌ Contact storage failed")
                return False
            
            return True
            
        finally:
            # Clean up temp directory
            shutil.rmtree(temp_dir, ignore_errors=True)
        
    except Exception as e:
        print(f"❌ Secure chat handler test failed: {e}")
        return False

def test_group_chat_handler():
    """Test group chat handler basic functionality"""
    print("\n🔍 Testing group chat handler...")
    
    try:
        from chat.group_chat import GroupChatHandler, GroupChatRoom
        from crypto.pgp_handler import PGPHandler
        
        # Create a temporary directory for testing
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create PGP handler
            pgp_handler = PGPHandler(temp_dir)
            print("✅ PGP handler creation successful")
            
            # Create group chat handler
            group_handler = GroupChatHandler(pgp_handler)
            print("✅ Group chat handler creation successful")
            
            # Test group room creation
            test_room = GroupChatRoom("TestGroup", "A test group", "testcreator")
            if test_room.name == "TestGroup" and test_room.creator == "testcreator":
                print("✅ Group room creation successful")
            else:
                print("❌ Group room creation failed")
                return False
            
            # Test member management
            success, message = test_room.add_member("testuser1")
            if success:
                print("✅ Member addition successful")
            else:
                print(f"❌ Member addition failed: {message}")
                return False
            
            # Test admin check
            if test_room.is_admin("testcreator"):
                print("✅ Creator admin status correct")
            else:
                print("❌ Creator admin status incorrect")
                return False
            
            return True
            
        finally:
            # Clean up temp directory
            shutil.rmtree(temp_dir, ignore_errors=True)
        
    except Exception as e:
        print(f"❌ Group chat handler test failed: {e}")
        return False

def test_main_window_chat_integration():
    """Test main window chat integration (without actually starting GUI)"""
    print("\n🔍 Testing main window chat integration...")
    
    try:
        from gui.main_window import PGPToolMainWindow
        
        # Test that the main window class has the required chat methods
        required_methods = [
            'refresh_chat_profiles',
            'on_chat_profile_changed', 
            'refresh_chat_contacts',
            'connect_to_chat',
            '_check_connection_status',
            'show_group_info_dialog'
        ]
        
        for method_name in required_methods:
            if hasattr(PGPToolMainWindow, method_name):
                print(f"✅ Method {method_name} exists")
            else:
                print(f"❌ Method {method_name} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Main window integration test failed: {e}")
        return False

def test_dependencies():
    """Test that all required dependencies are available"""
    print("\n🔍 Testing dependencies...")
    
    required_modules = [
        'cryptography',
        'irc',
        'tkinter'
    ]
    
    for module_name in required_modules:
        try:
            if module_name == 'tkinter':
                import tkinter
            elif module_name == 'cryptography':
                import cryptography
            elif module_name == 'irc':
                import irc
            print(f"✅ {module_name} available")
        except ImportError:
            print(f"❌ {module_name} not available")
            return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Starting PGP Tool Chat System Validation Tests")
    print("=" * 60)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Module Imports", test_imports),
        ("IRC Client", test_irc_client),
        ("Secure Chat Handler", test_secure_chat_handler),
        ("Group Chat Handler", test_group_chat_handler),
        ("Main Window Integration", test_main_window_chat_integration)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Chat system is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

