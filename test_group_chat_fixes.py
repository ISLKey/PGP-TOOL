#!/usr/bin/env python3
"""
Test script to verify the group chat fixes in PGP Tool
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_irc_client_separate_callbacks():
    """Test that the IRC client has separate callbacks for private and channel messages"""
    print("Testing IRC client separate callbacks...")
    
    try:
        from chat.irc_client import PGPIRCClient
        
        client = PGPIRCClient()
        
        # Check that separate callback attributes exist
        if hasattr(client, 'on_private_message_callback'):
            print("✅ on_private_message_callback attribute exists")
        else:
            print("❌ on_private_message_callback attribute missing")
            return False
            
        if hasattr(client, 'on_channel_message_callback'):
            print("✅ on_channel_message_callback attribute exists")
        else:
            print("❌ on_channel_message_callback attribute missing")
            return False
            
        # Test setting callbacks
        def test_private_callback(sender, target, message):
            pass
            
        def test_channel_callback(sender, target, message):
            pass
            
        client.on_private_message_callback = test_private_callback
        client.on_channel_message_callback = test_channel_callback
        
        if client.on_private_message_callback == test_private_callback:
            print("✅ Private message callback can be set")
        else:
            print("❌ Private message callback setting failed")
            return False
            
        if client.on_channel_message_callback == test_channel_callback:
            print("✅ Channel message callback can be set")
        else:
            print("❌ Channel message callback setting failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ IRC client test failed: {e}")
        return False

def test_group_chat_room_external_attribute():
    """Test that GroupChatRoom supports is_external attribute"""
    print("\nTesting GroupChatRoom external attribute...")
    
    try:
        from chat.group_chat import GroupChatRoom
        
        # Test creating a regular group
        regular_group = GroupChatRoom("test_group", "Test description", "creator")
        
        if hasattr(regular_group, 'is_external'):
            print("✅ is_external attribute exists")
        else:
            print("❌ is_external attribute missing")
            return False
            
        if regular_group.is_external == False:
            print("✅ is_external defaults to False")
        else:
            print("❌ is_external should default to False")
            return False
            
        # Test setting is_external to True
        regular_group.is_external = True
        if regular_group.is_external == True:
            print("✅ is_external can be set to True")
        else:
            print("❌ is_external setting failed")
            return False
            
        # Test to_dict includes is_external
        group_dict = regular_group.to_dict()
        if 'is_external' in group_dict:
            print("✅ to_dict includes is_external")
        else:
            print("❌ to_dict missing is_external")
            return False
            
        # Test from_dict handles is_external
        test_data = {
            'name': 'external_group',
            'description': 'External IRC channel',
            'creator': '',
            'is_external': True,
            'members': ['user1'],
            'admins': []
        }
        
        external_group = GroupChatRoom.from_dict(test_data)
        if external_group.is_external == True:
            print("✅ from_dict correctly sets is_external")
        else:
            print("❌ from_dict failed to set is_external")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ GroupChatRoom test failed: {e}")
        return False

def test_group_chat_handler_callback_setup():
    """Test that GroupChatHandler sets up callbacks correctly"""
    print("\nTesting GroupChatHandler callback setup...")
    
    try:
        from crypto.pgp_handler import PGPHandler
        from chat.group_chat import GroupChatHandler
        from chat.irc_client import PGPIRCClient
        
        # Create handlers
        pgp_handler = PGPHandler("/tmp/test_pgp")
        group_handler = GroupChatHandler(pgp_handler)
        
        # Create a mock IRC client
        irc_client = PGPIRCClient()
        group_handler.irc_client = irc_client
        
        # Test that setup_group_irc_callbacks works
        group_handler.setup_group_irc_callbacks()
        
        # Check that the channel message callback is set
        if irc_client.on_channel_message_callback is not None:
            print("✅ Channel message callback is set by GroupChatHandler")
        else:
            print("❌ Channel message callback not set")
            return False
            
        # Check that it's set to the group message handler
        if irc_client.on_channel_message_callback == group_handler._handle_group_message:
            print("✅ Channel message callback points to _handle_group_message")
        else:
            print("❌ Channel message callback not pointing to correct method")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ GroupChatHandler test failed: {e}")
        return False

if __name__ == "__main__":
    print("PGP Tool Group Chat Fixes Validation")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    if test_irc_client_separate_callbacks():
        tests_passed += 1
    
    if test_group_chat_room_external_attribute():
        tests_passed += 1
        
    if test_group_chat_handler_callback_setup():
        tests_passed += 1
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("\n🎉 All tests passed! The group chat fixes should resolve the issues.")
        print("\n💡 Expected improvements:")
        print("   1. Group messages will appear in group chat instead of private chat")
        print("   2. Group creator information will be displayed correctly")
        print("   3. External IRC channels will be properly identified")
        print("   4. Member count will be accurate for tracked members")
    else:
        print(f"\n⚠️  {total_tests - tests_passed} test(s) failed. Please check the implementation.")

