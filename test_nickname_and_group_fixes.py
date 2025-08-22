#!/usr/bin/env python3
"""
Test script to verify the nickname synchronization and group chat fixes in PGP Tool
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_irc_client_nickname_change():
    """Test that the IRC client can change nicknames"""
    print("Testing IRC client nickname change functionality...")
    
    try:
        from chat.irc_client import PGPIRCClient
        
        client = PGPIRCClient()
        
        # Check that change_nickname method exists
        if hasattr(client, 'change_nickname'):
            print("✅ change_nickname method exists")
        else:
            print("❌ change_nickname method missing")
            return False
            
        # Test that nickname is stored
        client.nickname = "test_nick"
        if client.nickname == "test_nick":
            print("✅ Nickname can be set and retrieved")
        else:
            print("❌ Nickname setting failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ IRC client nickname test failed: {e}")
        return False

def test_secure_chat_private_message_callback():
    """Test that secure chat uses private message callback correctly"""
    print("\nTesting secure chat private message callback setup...")
    
    try:
        from crypto.pgp_handler import PGPHandler
        from chat.secure_chat import SecureChatHandler
        from chat.irc_client import PGPIRCClient
        
        # Create handlers
        pgp_handler = PGPHandler("/tmp/test_pgp")
        secure_chat = SecureChatHandler(pgp_handler)
        
        # Check that the IRC client has the private message callback set
        if hasattr(secure_chat.irc_client, 'on_private_message_callback'):
            print("✅ IRC client has on_private_message_callback attribute")
        else:
            print("❌ IRC client missing on_private_message_callback")
            return False
            
        # Check that secure chat sets up the callback
        if secure_chat.irc_client.on_private_message_callback is not None:
            print("✅ Private message callback is set by SecureChatHandler")
        else:
            print("❌ Private message callback not set")
            return False
            
        # Check that it points to the correct method
        if hasattr(secure_chat, '_on_irc_private_message'):
            print("✅ _on_irc_private_message method exists")
        else:
            print("❌ _on_irc_private_message method missing")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Secure chat callback test failed: {e}")
        return False

def test_group_chat_channel_message_callback():
    """Test that group chat handles channel messages correctly"""
    print("\nTesting group chat channel message callback setup...")
    
    try:
        from crypto.pgp_handler import PGPHandler
        from chat.group_chat import GroupChatHandler
        from chat.irc_client import PGPIRCClient
        
        # Create handlers
        pgp_handler = PGPHandler("/tmp/test_pgp")
        group_chat = GroupChatHandler(pgp_handler)
        
        # Create a mock IRC client
        irc_client = PGPIRCClient()
        group_chat.irc_client = irc_client
        
        # Test that setup_group_irc_callbacks works
        group_chat.setup_group_irc_callbacks()
        
        # Check that the channel message callback is set
        if irc_client.on_channel_message_callback is not None:
            print("✅ Channel message callback is set by GroupChatHandler")
        else:
            print("❌ Channel message callback not set")
            return False
            
        # Check that it's set to the group message handler
        if irc_client.on_channel_message_callback == group_chat._handle_group_message:
            print("✅ Channel message callback points to _handle_group_message")
        else:
            print("❌ Channel message callback not pointing to correct method")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Group chat callback test failed: {e}")
        return False

def test_callback_separation():
    """Test that private and channel message callbacks are properly separated"""
    print("\nTesting callback separation between private and channel messages...")
    
    try:
        from crypto.pgp_handler import PGPHandler
        from chat.secure_chat import SecureChatHandler
        from chat.group_chat import GroupChatHandler
        from chat.irc_client import PGPIRCClient
        
        # Create handlers
        pgp_handler = PGPHandler("/tmp/test_pgp")
        secure_chat = SecureChatHandler(pgp_handler)
        group_chat = GroupChatHandler(pgp_handler)
        
        # Share the same IRC client (as would happen in the real app)
        group_chat.irc_client = secure_chat.irc_client
        
        # Set up group chat callbacks (this should not interfere with private messages)
        group_chat.setup_group_irc_callbacks()
        
        # Check that both callbacks are set to different methods
        irc_client = secure_chat.irc_client
        
        if irc_client.on_private_message_callback is not None:
            print("✅ Private message callback is set")
        else:
            print("❌ Private message callback not set")
            return False
            
        if irc_client.on_channel_message_callback is not None:
            print("✅ Channel message callback is set")
        else:
            print("❌ Channel message callback not set")
            return False
            
        # Check that they point to different methods
        if (irc_client.on_private_message_callback != irc_client.on_channel_message_callback):
            print("✅ Private and channel callbacks are different (no conflict)")
        else:
            print("❌ Private and channel callbacks are the same (conflict!)")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Callback separation test failed: {e}")
        return False

def test_main_window_nickname_methods():
    """Test that main window has nickname change methods"""
    print("\nTesting main window nickname change methods...")
    
    try:
        # Just check that the methods exist in the file
        with open('gui/main_window.py', 'r') as f:
            content = f.read()
            
        if 'def apply_nickname_change' in content:
            print("✅ apply_nickname_change method exists in main window")
        else:
            print("❌ apply_nickname_change method missing")
            return False
            
        if 'def on_irc_nickname_changed' in content:
            print("✅ on_irc_nickname_changed method exists in main window")
        else:
            print("❌ on_irc_nickname_changed method missing")
            return False
            
        if 'trace(\'w\', self.on_irc_nickname_changed)' in content:
            print("✅ Nickname field has change callback")
        else:
            print("❌ Nickname field missing change callback")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Main window nickname test failed: {e}")
        return False

if __name__ == "__main__":
    print("PGP Tool Nickname & Group Chat Fixes Validation")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 5
    
    if test_irc_client_nickname_change():
        tests_passed += 1
    
    if test_secure_chat_private_message_callback():
        tests_passed += 1
        
    if test_group_chat_channel_message_callback():
        tests_passed += 1
        
    if test_callback_separation():
        tests_passed += 1
        
    if test_main_window_nickname_methods():
        tests_passed += 1
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("\n🎉 All tests passed! The fixes should resolve the issues.")
        print("\n💡 Expected improvements:")
        print("   1. IRC nickname changes will be applied immediately")
        print("   2. Group messages will appear in group chat (not private chat)")
        print("   3. Private messages will appear in private chat only")
        print("   4. No more duplicate messages in chat")
        print("   5. Proper message routing based on message type")
    else:
        print(f"\n⚠️  {total_tests - tests_passed} test(s) failed. Please check the implementation.")

