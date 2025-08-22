#!/usr/bin/env python3
"""
Simple IRC Connection Test for PGP Tool
This script tests IRC connectivity outside of the GUI to help debug connection issues
"""

import os
import sys
import time

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

def test_basic_connection():
    """Test basic IRC connection"""
    print("🔍 Testing basic IRC connection...")
    
    try:
        from chat.irc_client import PGPIRCClient, IRCNetworks
        
        # Create IRC client
        client = PGPIRCClient()
        print("✅ IRC client created")
        
        # Set up callbacks
        connection_success = False
        connection_error = None
        
        def on_connect(network, nickname):
            nonlocal connection_success
            connection_success = True
            print(f"✅ Connected to {network} as {nickname}")
        
        def on_error(error):
            nonlocal connection_error
            connection_error = error
            print(f"❌ Connection error: {error}")
        
        def on_disconnect():
            print("📡 Disconnected from IRC")
        
        client.set_connect_callback(on_connect)
        client.set_error_callback(on_error)
        client.set_disconnect_callback(on_disconnect)
        
        # Try connecting to different networks
        networks_to_try = ["libera", "oftc", "efnet"]
        
        for network in networks_to_try:
            print(f"\n🌐 Trying to connect to {network}...")
            
            # Reset status
            connection_success = False
            connection_error = None
            
            # Attempt connection
            result = client.connect_to_network(network, "TestUser_12345")
            print(f"Connection attempt result: {result}")
            
            # Wait for connection to establish
            print("⏳ Waiting for connection...")
            for i in range(10):  # Wait up to 10 seconds
                time.sleep(1)
                if connection_success:
                    print(f"✅ Successfully connected to {network}!")
                    client.disconnect()
                    time.sleep(1)
                    return True
                elif connection_error:
                    print(f"❌ Failed to connect to {network}: {connection_error}")
                    break
                print(f"   Waiting... ({i+1}/10)")
            
            if not connection_success and not connection_error:
                print(f"⏰ Connection to {network} timed out")
            
            # Disconnect before trying next network
            client.disconnect()
            time.sleep(2)
        
        print("\n❌ Failed to connect to any IRC network")
        return False
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_network_connectivity():
    """Test basic network connectivity"""
    print("\n🔍 Testing network connectivity...")
    
    import socket
    
    # Test DNS resolution and connectivity to IRC servers
    servers_to_test = [
        ("irc.libera.chat", 6697),
        ("irc.oftc.net", 6697),
        ("irc.efnet.org", 6697)
    ]
    
    for server, port in servers_to_test:
        try:
            print(f"🌐 Testing connection to {server}:{port}...")
            
            # Test DNS resolution
            ip = socket.gethostbyname(server)
            print(f"   DNS resolved to: {ip}")
            
            # Test TCP connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((server, port))
            sock.close()
            
            if result == 0:
                print(f"✅ Can connect to {server}:{port}")
            else:
                print(f"❌ Cannot connect to {server}:{port} (error {result})")
                
        except socket.gaierror as e:
            print(f"❌ DNS resolution failed for {server}: {e}")
        except Exception as e:
            print(f"❌ Connection test failed for {server}: {e}")

def main():
    """Run all connection tests"""
    print("🚀 PGP Tool IRC Connection Debug Test")
    print("=" * 50)
    
    # Test network connectivity first
    test_network_connectivity()
    
    # Test IRC connection
    success = test_basic_connection()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 IRC connection test PASSED!")
        print("The IRC client can connect successfully.")
        print("The issue may be in the GUI integration.")
    else:
        print("❌ IRC connection test FAILED!")
        print("This indicates a network connectivity issue.")
        print("\nPossible solutions:")
        print("• Check your internet connection")
        print("• Check if your firewall blocks IRC ports (6667/6697)")
        print("• Try connecting from a different network")
        print("• Contact your network administrator")

if __name__ == "__main__":
    main()

