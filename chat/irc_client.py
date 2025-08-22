"""
IRC Client for PGP Tool
Handles IRC connections and message routing for secure chat
"""

import irc.client
import irc.connection
import ssl
import threading
import time
import random
import string
from typing import Dict, List, Optional, Callable


class IRCNetworks:
    """Predefined IRC networks - ENHANCED WITH FALLBACK OPTIONS"""
    
    NETWORKS = {
        "libera": {
            "name": "Libera Chat",
            "server": "irc.libera.chat",
            "port": 6697,
            "ssl": True,
            "fallback_port": 6667,
            "fallback_ssl": False,
            "description": "Largest FOSS-focused network"
        },
        "oftc": {
            "name": "OFTC",
            "server": "irc.oftc.net", 
            "port": 6697,
            "ssl": True,
            "fallback_port": 6667,
            "fallback_ssl": False,
            "description": "Open and Free Technology Community"
        },
        "efnet": {
            "name": "EFNet",
            "server": "irc.efnet.org",
            "port": 6697,
            "ssl": True,
            "fallback_port": 6667,
            "fallback_ssl": False,
            "description": "Original IRC network"
        }
    }
    
    @classmethod
    def get_network_list(cls):
        """Get list of network names"""
        return list(cls.NETWORKS.keys())
    
    @classmethod
    def get_network_info(cls, network_id):
        """Get network configuration"""
        return cls.NETWORKS.get(network_id)


class PGPIRCClient:
    """IRC client for PGP Tool secure chat"""
    
    def __init__(self):
        self.reactor = irc.client.Reactor()
        self.connection = None
        self.connected = False
        self.current_network = None
        self.nickname = None
        self.custom_servers = {}  # User-defined servers
        
        # Callbacks
        self.on_message_callback = None  # For backward compatibility
        self.on_private_message_callback = None  # For private messages
        self.on_channel_message_callback = None  # For channel messages
        self.on_connect_callback = None
        self.on_disconnect_callback = None
        self.on_error_callback = None
        
        # Threading
        self.reactor_thread = None
        self.running = False
        
        # Setup event handlers
        self.reactor.add_global_handler("welcome", self._on_welcome)
        self.reactor.add_global_handler("privmsg", self._on_privmsg)
        self.reactor.add_global_handler("pubmsg", self._on_pubmsg)  # Handle channel messages
        self.reactor.add_global_handler("disconnect", self._on_disconnect)
        self.reactor.add_global_handler("nicknameinuse", self._on_nick_in_use)
        
    def generate_random_nickname(self, prefix="PGPUser"):
        """Generate a random nickname"""
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"{prefix}_{suffix}"
    
    def add_custom_server(self, name: str, server: str, port: int, ssl: bool = True):
        """Add a custom IRC server"""
        self.custom_servers[name] = {
            "name": name,
            "server": server,
            "port": port,
            "ssl": ssl,
            "description": "Custom server"
        }
    
    def get_available_networks(self):
        """Get all available networks (predefined + custom)"""
        networks = IRCNetworks.NETWORKS.copy()
        networks.update(self.custom_servers)
        return networks
    
    def connect_to_network(self, network_id: str, nickname: str = None):
        """Connect to an IRC network - ENHANCED WITH FALLBACK CONNECTIONS"""
        if self.connected:
            self.disconnect()
        
        # Get network info
        if network_id in IRCNetworks.NETWORKS:
            network_info = IRCNetworks.NETWORKS[network_id]
        elif network_id in self.custom_servers:
            network_info = self.custom_servers[network_id]
        else:
            error_msg = f"Unknown network: {network_id}"
            if self.on_error_callback:
                self.on_error_callback(error_msg)
            return False
        
        # Set nickname
        if nickname is None:
            nickname = self.generate_random_nickname()
        self.nickname = nickname
        self.current_network = network_id
        
        # Try primary connection first, then fallback
        connection_attempts = [
            {
                "port": network_info["port"],
                "ssl": network_info["ssl"],
                "description": "SSL"
            }
        ]
        
        # Add fallback if available
        if "fallback_port" in network_info:
            connection_attempts.append({
                "port": network_info["fallback_port"],
                "ssl": network_info.get("fallback_ssl", False),
                "description": "non-SSL fallback"
            })
        
        for attempt in connection_attempts:
            try:
                print(f"DEBUG: Attempting {attempt['description']} connection to {network_info['name']} ({network_info['server']}:{attempt['port']})")
                
                # Create connection factory
                if attempt["ssl"]:
                    print("DEBUG: Setting up SSL connection")
                    # Create SSL context for modern Python versions
                    ssl_context = ssl.create_default_context()
                    # For IRC, we often need to disable hostname checking due to certificate issues
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
                    
                    def ssl_wrapper(sock):
                        try:
                            wrapped = ssl_context.wrap_socket(sock, server_hostname=network_info["server"])
                            print("DEBUG: SSL connection established")
                            return wrapped
                        except Exception as e:
                            print(f"DEBUG: SSL wrapping failed: {e}")
                            raise
                    
                    factory = irc.connection.Factory(wrapper=ssl_wrapper)
                else:
                    print("DEBUG: Setting up plain connection")
                    factory = irc.connection.Factory()
                
                print(f"DEBUG: Connecting with nickname: {nickname}")
                
                # Connect to server
                try:
                    self.connection = self.reactor.server().connect(
                        network_info["server"],
                        attempt["port"],
                        nickname,
                        connect_factory=factory
                    )
                    print("DEBUG: Connection object created successfully")
                except Exception as e:
                    error_msg = f"Failed to create {attempt['description']} connection: {str(e)}"
                    print(f"DEBUG: {error_msg}")
                    if attempt == connection_attempts[-1]:  # Last attempt
                        if self.on_error_callback:
                            self.on_error_callback(error_msg)
                        return False
                    else:
                        print("DEBUG: Trying fallback connection...")
                        continue
                
                # Start reactor in separate thread
                self.running = True
                self.reactor_thread = threading.Thread(target=self._run_reactor, daemon=True)
                self.reactor_thread.start()
                print("DEBUG: Reactor thread started")
                
                # Wait for connection to establish
                print("DEBUG: Waiting for connection to establish...")
                for i in range(10):  # Wait up to 10 seconds
                    time.sleep(1)
                    if self.connected:
                        print(f"DEBUG: {attempt['description']} connection established successfully")
                        return True
                    print(f"DEBUG: Waiting... ({i+1}/10)")
                
                # Connection timeout - try next method
                print(f"DEBUG: {attempt['description']} connection timed out")
                self.disconnect()
                time.sleep(1)
                
                if attempt == connection_attempts[-1]:  # Last attempt
                    error_msg = f"All connection attempts failed to {network_info['name']}"
                    if self.on_error_callback:
                        self.on_error_callback(error_msg)
                    return False
                else:
                    print("DEBUG: Trying fallback connection method...")
                    continue
                
            except Exception as e:
                error_msg = f"{attempt['description']} connection failed to {network_info['name']}: {str(e)}"
                print(f"DEBUG: {error_msg}")
                
                if attempt == connection_attempts[-1]:  # Last attempt
                    if self.on_error_callback:
                        self.on_error_callback(error_msg)
                    return False
                else:
                    print("DEBUG: Trying fallback connection method...")
                    continue
        
        return False
    
    def disconnect(self):
        """Disconnect from IRC"""
        if self.connection and self.connected:
            self.connection.quit("PGP Tool disconnecting")
        
        self.running = False
        self.connected = False
        
        if self.reactor_thread and self.reactor_thread.is_alive():
            # Give reactor time to clean up
            time.sleep(0.5)
    
    def send_private_message(self, target_nick: str, message: str):
        """Send a private message to a user"""
        if not self.connected or not self.connection:
            raise RuntimeError("Not connected to IRC")
        
        self.connection.privmsg(target_nick, message)
    
    def send_message(self, target: str, message: str):
        """Send a message to a user or channel"""
        if not self.connected or not self.connection:
            raise RuntimeError("Not connected to IRC")
        
        self.connection.privmsg(target, message)
    
    def change_nickname(self, new_nickname: str):
        """Change IRC nickname"""
        if not self.connected or not self.connection:
            raise RuntimeError("Not connected to IRC")
        
        self.connection.nick(new_nickname)
        self.nickname = new_nickname
    
    def _run_reactor(self):
        """Run IRC reactor in separate thread"""
        try:
            while self.running:
                self.reactor.process_once(timeout=0.2)
        except Exception as e:
            if self.on_error_callback:
                self.on_error_callback(f"IRC reactor error: {str(e)}")
    
    def _on_welcome(self, connection, event):
        """Handle successful connection - ENHANCED"""
        print("DEBUG: Received welcome message - connection successful")
        self.connected = True
        if self.on_connect_callback:
            try:
                self.on_connect_callback(self.current_network, self.nickname)
            except Exception as e:
                print(f"DEBUG: Error in connect callback: {e}")
    
    def _on_privmsg(self, connection, event):
        """Handle incoming private message - ENHANCED"""
        try:
            sender = event.source.nick
            target = event.target
            message = event.arguments[0]
            
            print(f"DEBUG: Received private message from {sender}: {message[:50]}...")
            
            # Call specific private message callback first
            if self.on_private_message_callback:
                self.on_private_message_callback(sender, target, message)
            # Fall back to general message callback for backward compatibility
            elif self.on_message_callback:
                self.on_message_callback(sender, target, message)
        except Exception as e:
            print(f"DEBUG: Error handling private message: {e}")
    
    def _on_pubmsg(self, connection, event):
        """Handle incoming channel message - ENHANCED"""
        try:
            sender = event.source.nick
            target = event.target  # This will be the channel name
            message = event.arguments[0]
            
            print(f"DEBUG: Received channel message from {sender} in {target}: {message[:50]}...")
            
            # Don't process our own messages
            if sender != self.nickname:
                # Call specific channel message callback first
                if self.on_channel_message_callback:
                    self.on_channel_message_callback(sender, target, message)
                # Fall back to general message callback for backward compatibility
                elif self.on_message_callback:
                    self.on_message_callback(sender, target, message)
        except Exception as e:
            print(f"DEBUG: Error handling channel message: {e}")
    
    def _on_disconnect(self, connection, event):
        """Handle disconnection - ENHANCED"""
        print("DEBUG: Disconnected from IRC")
        self.connected = False
        if self.on_disconnect_callback:
            try:
                self.on_disconnect_callback()
            except Exception as e:
                print(f"DEBUG: Error in disconnect callback: {e}")
    
    def _on_nick_in_use(self, connection, event):
        """Handle nickname already in use - ENHANCED"""
        print(f"DEBUG: Nickname {self.nickname} is in use, generating new one")
        # Try with a different random suffix
        new_nick = self.generate_random_nickname()
        print(f"DEBUG: Trying new nickname: {new_nick}")
        connection.nick(new_nick)
        self.nickname = new_nick
    
    def join_channel(self, channel: str):
        """Join an IRC channel"""
        if self.connected and self.connection:
            if not channel.startswith('#'):
                channel = f"#{channel}"
            self.connection.join(channel)
            return True
        return False
    
    def part_channel(self, channel: str, message: str = "Leaving"):
        """Leave an IRC channel"""
        if self.connected and self.connection:
            if not channel.startswith('#'):
                channel = f"#{channel}"
            self.connection.part([channel], message)
            return True
        return False
    
    def send_channel_message(self, channel: str, message: str):
        """Send a message to a channel"""
        if self.connected and self.connection:
            if not channel.startswith('#'):
                channel = f"#{channel}"
            self.connection.privmsg(channel, message)
            return True
        return False
    
    def set_message_callback(self, callback: Callable[[str, str, str], None]):
        """Set callback for incoming messages (sender, target, message)"""
        self.on_message_callback = callback
    
    def set_connect_callback(self, callback: Callable[[str, str], None]):
        """Set callback for successful connection"""
        self.on_connect_callback = callback
    
    def set_disconnect_callback(self, callback: Callable[[], None]):
        """Set callback for disconnection"""
        self.on_disconnect_callback = callback
    
    def set_error_callback(self, callback: Callable[[str], None]):
        """Set callback for errors"""
        self.on_error_callback = callback
    
    def get_connection_status(self):
        """Get current connection status"""
        return {
            "connected": self.connected,
            "network": self.current_network,
            "nickname": self.nickname,
            "server": IRCNetworks.get_network_info(self.current_network) if self.current_network else None
        }

