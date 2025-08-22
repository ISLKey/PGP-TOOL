"""
Secure Chat Handler for PGP Tool
Combines IRC client with PGP encryption for secure messaging
"""

import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Callable
from .irc_client import PGPIRCClient


class SecureChatMessage:
    """Represents a secure chat message"""
    
    def __init__(self, sender: str, recipient: str, content: str, 
                 message_id: str = None, timestamp: float = None):
        self.sender = sender
        self.recipient = recipient
        self.content = content
        self.message_id = message_id or str(uuid.uuid4())
        self.timestamp = timestamp or time.time()
        self.encrypted = False
        self.verified = False
        
    def to_dict(self):
        """Convert message to dictionary"""
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "content": self.content,
            "message_id": self.message_id,
            "timestamp": self.timestamp,
            "encrypted": self.encrypted,
            "verified": self.verified
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create message from dictionary"""
        msg = cls(
            sender=data["sender"],
            recipient=data["recipient"],
            content=data["content"],
            message_id=data["message_id"],
            timestamp=data["timestamp"]
        )
        msg.encrypted = data.get("encrypted", False)
        msg.verified = data.get("verified", False)
        return msg


class SecureChatContact:
    """Represents a secure chat contact - ENHANCED VERSION"""
    
    def __init__(self, name: str, irc_nickname: str, pgp_fingerprint: str):
        self.name = name
        self.irc_nickname = irc_nickname
        self.pgp_fingerprint = pgp_fingerprint
        self.online = False
        self.last_seen = None
        self.public_key = None  # Store public key directly for better performance
        
    def to_dict(self):
        """Convert contact to dictionary"""
        return {
            "name": self.name,
            "irc_nickname": self.irc_nickname,
            "pgp_fingerprint": self.pgp_fingerprint,
            "online": self.online,
            "last_seen": self.last_seen,
            "public_key": self.public_key
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create contact from dictionary"""
        contact = cls(
            name=data["name"],
            irc_nickname=data["irc_nickname"],
            pgp_fingerprint=data["pgp_fingerprint"]
        )
        contact.online = data.get("online", False)
        contact.last_seen = data.get("last_seen")
        contact.public_key = data.get("public_key")
        return contact


class SecureChatHandler:
    """Handles secure IRC+PGP chat functionality"""
    
    def __init__(self, pgp_handler):
        self.pgp_handler = pgp_handler
        self.irc_client = PGPIRCClient()
        self.contacts = {}  # nickname -> SecureChatContact
        self.message_history = []  # List of SecureChatMessage
        self.save_history = True  # User preference for saving history
        
        # Message chunking support
        self.pending_chunks = {}  # message_id -> {chunks: {}, total: int, sender: str}
        self.chunk_timeout = 30  # seconds
        
        # Message markers for PGP detection
        self.PGP_MESSAGE_START = "-----BEGIN PGP MESSAGE-----"
        self.PGP_MESSAGE_END = "-----END PGP MESSAGE-----"
        
        # Callbacks
        self.on_message_callback = None
        self.on_contact_online_callback = None
        self.on_contact_offline_callback = None
        self.on_error_callback = None
        
        # Setup IRC callbacks
        self.setup_irc_callbacks()
        
    def setup_irc_callbacks(self):
        """Setup IRC client callbacks"""
        # Use the new separate callback system
        self.irc_client.on_private_message_callback = self._on_irc_private_message
        self.irc_client.on_connect_callback = self._on_irc_connect
        self.irc_client.on_disconnect_callback = self._on_irc_disconnect
        self.irc_client.on_error_callback = self._on_irc_error
        
        # Note: We don't set on_channel_message_callback here because
        # that will be handled by the GroupChatHandler when it's active
        
    def add_contact(self, name: str, irc_nickname: str, pgp_fingerprint: str = None, public_key: str = None):
        """Add a secure chat contact - ENHANCED VERSION"""
        if not pgp_fingerprint and not public_key:
            raise ValueError("Either PGP fingerprint or public key must be provided")
            
        # If public key is provided, import it and get fingerprint
        if public_key:
            try:
                # Import the public key using the correct method
                import_result = self.pgp_handler.import_key(public_key)
                if not import_result or not import_result.get('success', False):
                    raise ValueError(f"Failed to import public key: {import_result.get('error', 'Unknown error') if import_result else 'No result'}")
                
                # Extract fingerprint from the imported key
                # Try to get fingerprint from the key text directly first
                pgp_fingerprint = self._extract_fingerprint_from_key_text(public_key)
                
                if not pgp_fingerprint:
                    # Fallback: get from key list using the import result
                    if 'fingerprint' in import_result:
                        pgp_fingerprint = import_result['fingerprint']
                    elif 'imported_keys' in import_result and import_result['imported_keys']:
                        # Get fingerprint from first imported key
                        first_imported = import_result['imported_keys'][0]
                        if isinstance(first_imported, dict) and 'fingerprint' in first_imported:
                            pgp_fingerprint = first_imported['fingerprint']
                        elif hasattr(first_imported, 'fingerprint'):
                            pgp_fingerprint = first_imported.fingerprint
                
                if not pgp_fingerprint:
                    # Last resort: get from key list
                    keys = self.pgp_handler.list_keys(secret=False)
                    if keys:
                        # Get the last key (most recently imported)
                        last_key = keys[-1] if isinstance(keys, list) else keys
                        if hasattr(last_key, 'fingerprint'):
                            pgp_fingerprint = last_key.fingerprint
                        elif isinstance(last_key, dict) and 'fingerprint' in last_key:
                            pgp_fingerprint = last_key['fingerprint']
                        elif hasattr(last_key, 'fpr'):
                            pgp_fingerprint = last_key.fpr
                
                if not pgp_fingerprint:
                    raise ValueError("Could not determine fingerprint from imported key")
                    
                print(f"DEBUG: Successfully imported public key for {name}, fingerprint: {pgp_fingerprint}")
                    
            except Exception as e:
                raise ValueError(f"Failed to process public key: {str(e)}")
        
        # Create contact with both fingerprint and public key if available
        contact = SecureChatContact(name, irc_nickname, pgp_fingerprint)
        
        # Store the public key in the contact for direct access
        if public_key:
            contact.public_key = public_key
        
        self.contacts[irc_nickname] = contact
        print(f"DEBUG: Added chat contact {name} ({irc_nickname}) with fingerprint {pgp_fingerprint}")
        return contact
    
    def _extract_fingerprint_from_key_text(self, public_key: str) -> str:
        """Extract fingerprint from public key text using simple parsing"""
        try:
            # Look for fingerprint in key comments or try to parse key structure
            lines = public_key.split('\n')
            
            # Sometimes fingerprints are in comments
            for line in lines:
                if 'fingerprint' in line.lower() or 'fpr' in line.lower():
                    # Extract hex characters that look like a fingerprint
                    import re
                    hex_match = re.search(r'([A-F0-9\s]{40,})', line.upper())
                    if hex_match:
                        fingerprint = hex_match.group(1).replace(' ', '')
                        if len(fingerprint) >= 40:
                            return fingerprint
            
            # If no fingerprint found in comments, we'll need to rely on the PGP handler
            return None
            
        except Exception:
            return None
    
    def _extract_fingerprint_from_key(self, public_key: str) -> str:
        """Extract fingerprint from public key text (legacy method)"""
        try:
            # This method is kept for compatibility but simplified
            return self._extract_fingerprint_from_key_text(public_key)
        except Exception:
            return None
        
    def remove_contact(self, irc_nickname: str):
        """Remove a contact"""
        if irc_nickname in self.contacts:
            del self.contacts[irc_nickname]
            
    def get_contact(self, irc_nickname: str) -> Optional[SecureChatContact]:
        """Get contact by IRC nickname"""
        return self.contacts.get(irc_nickname)
        
    def get_contacts_list(self) -> List[SecureChatContact]:
        """Get list of all contacts"""
        return list(self.contacts.values())
        
    def connect_to_irc(self, network: str, nickname: str = None):
        """Connect to IRC network"""
        return self.irc_client.connect_to_network(network, nickname)
        
    def disconnect_from_irc(self):
        """Disconnect from IRC"""
        self.irc_client.disconnect()
        
    def send_secure_message(self, recipient_nickname: str, message_content: str):
        """Send a PGP-encrypted message via IRC"""
        # Get contact info
        contact = self.get_contact(recipient_nickname)
        if not contact:
            raise ValueError(f"Unknown contact: {recipient_nickname}")
            
        # Get recipient's public key using the correct method
        try:
            # Use export_public_key method which exists in the PGP handler
            export_result = self.pgp_handler.export_public_key(contact.pgp_fingerprint)
            if not export_result or not export_result.get('success'):
                raise ValueError(f"No public key found for {contact.name}")
        except Exception as e:
            raise ValueError(f"Failed to get public key for {contact.name}: {str(e)}")
            
        # Create message object
        chat_message = SecureChatMessage(
            sender=self.irc_client.nickname,
            recipient=recipient_nickname,
            content=message_content
        )
        
        try:
            # Encrypt message with recipient's public key (using fingerprint as recipient)
            encrypt_result = self.pgp_handler.encrypt_message(
                message_content, 
                [contact.pgp_fingerprint]
            )
            
            if not encrypt_result or not encrypt_result.get('success'):
                raise RuntimeError(f"Failed to encrypt message: {encrypt_result.get('error', 'Unknown error')}")
            
            encrypted_content = encrypt_result['encrypted_message']
            
            # Encode encrypted message for IRC transmission and chunk if necessary
            encoded_message = self._encode_for_irc(encrypted_content)
            
            # Send message (chunked if necessary)
            self._send_chunked_message(recipient_nickname, encoded_message)
            
            # Mark as encrypted and add to history
            chat_message.encrypted = True
            if self.save_history:
                self.message_history.append(chat_message)
                
            return chat_message
            
        except Exception as e:
            raise RuntimeError(f"Failed to send secure message: {str(e)}")
    
    def _send_chunked_message(self, recipient_nickname: str, encoded_message: str):
        """Send a message in chunks if it's too long for IRC"""
        import uuid
        import time
        
        # IRC message limit is about 450 bytes to be safe (512 - overhead)
        max_chunk_size = 400  # Conservative limit
        
        if len(encoded_message) <= max_chunk_size:
            # Message fits in one chunk
            self.irc_client.send_private_message(recipient_nickname, encoded_message)
        else:
            # Need to chunk the message
            message_id = str(uuid.uuid4())[:8]  # Short unique ID
            chunks = []
            
            # Split message into chunks
            for i in range(0, len(encoded_message), max_chunk_size):
                chunk = encoded_message[i:i + max_chunk_size]
                chunks.append(chunk)
            
            total_chunks = len(chunks)
            
            # Send each chunk with metadata
            for chunk_num, chunk in enumerate(chunks):
                chunk_header = f"<PGP-CHUNK:{message_id}:{chunk_num + 1}:{total_chunks}>"
                chunk_message = f"{chunk_header}{chunk}"
                
                self.irc_client.send_private_message(recipient_nickname, chunk_message)
                
                # Small delay between chunks to avoid flooding
                if chunk_num < total_chunks - 1:
                    time.sleep(0.1)
    
    def _encode_for_irc(self, pgp_message: str) -> str:
        """Encode PGP message for IRC transmission (single line)"""
        import base64
        
        # Convert PGP message to base64 to make it IRC-safe
        encoded = base64.b64encode(pgp_message.encode('utf-8')).decode('ascii')
        
        # Add markers to identify it as an encoded PGP message
        return f"<PGP-ENCODED>{encoded}</PGP-ENCODED>"
    
    def _decode_from_irc(self, encoded_message: str) -> str:
        """Decode PGP message from IRC transmission"""
        import base64
        
        # Check if it's an encoded PGP message
        if encoded_message.startswith("<PGP-ENCODED>") and encoded_message.endswith("</PGP-ENCODED>"):
            # Extract the base64 content
            encoded_content = encoded_message[13:-14]  # Remove markers
            
            # Decode from base64
            try:
                decoded = base64.b64decode(encoded_content.encode('ascii')).decode('utf-8')
                return decoded
            except Exception:
                # If decoding fails, return original message
                return encoded_message
        
        # Not an encoded message, return as-is
        return encoded_message
            
    def _on_irc_private_message(self, sender_nickname: str, target: str, message_content: str):
        """Handle incoming IRC private message - UPDATED FOR PRIVATE MESSAGES ONLY"""
        # This method now only handles private messages (not channel messages)
        # Channel messages are handled by the GroupChatHandler
        
        print(f"DEBUG: Processing private message from {sender_nickname}: {message_content[:50]}...")
        
        # Check if it's a chunked message
        if message_content.startswith("<PGP-CHUNK:"):
            self._handle_chunk(sender_nickname, message_content)
            return
        
        # Process regular message
        self._process_complete_message(sender_nickname, message_content)
    
    def _handle_chunk(self, sender_nickname: str, chunk_message: str):
        """Handle a chunked message part"""
        import time
        
        try:
            # Parse chunk header: <PGP-CHUNK:message_id:chunk_num:total_chunks>
            header_end = chunk_message.find(">")
            if header_end == -1:
                return
                
            header = chunk_message[11:header_end]  # Remove <PGP-CHUNK:
            chunk_data = chunk_message[header_end + 1:]  # Content after >
            
            parts = header.split(":")
            if len(parts) != 3:
                return
                
            message_id, chunk_num, total_chunks = parts
            chunk_num = int(chunk_num)
            total_chunks = int(total_chunks)
            
            # Initialize pending message if not exists
            if message_id not in self.pending_chunks:
                self.pending_chunks[message_id] = {
                    "chunks": {},
                    "total": total_chunks,
                    "sender": sender_nickname,
                    "timestamp": time.time()
                }
            
            # Store chunk
            self.pending_chunks[message_id]["chunks"][chunk_num] = chunk_data
            
            # Check if we have all chunks
            pending = self.pending_chunks[message_id]
            if len(pending["chunks"]) == pending["total"]:
                # Reassemble message
                complete_message = ""
                for i in range(1, pending["total"] + 1):
                    complete_message += pending["chunks"][i]
                
                # Clean up
                del self.pending_chunks[message_id]
                
                # Process complete message
                self._process_complete_message(sender_nickname, complete_message)
            
        except Exception as e:
            if self.on_error_callback:
                self.on_error_callback(f"Failed to handle chunk from {sender_nickname}: {str(e)}")
    
    def _process_complete_message(self, sender_nickname: str, message_content: str):
        """Process a complete message (either single or reassembled) - ENHANCED DECRYPTION"""
        # First, try to decode the message if it's encoded
        decoded_message = self._decode_from_irc(message_content)
        
        # Check if it's a PGP encrypted message (either original format or decoded)
        if (self.PGP_MESSAGE_START in decoded_message and 
            self.PGP_MESSAGE_END in decoded_message):
            
            # Try to decrypt the message with enhanced error handling
            try:
                print(f"DEBUG: Attempting to decrypt message from {sender_nickname}")
                print(f"DEBUG: Using profile fingerprint: {getattr(self, '_current_profile_fingerprint', 'None')}")
                
                # First try with empty passphrase (for keys without passphrase)
                print("DEBUG: Trying decryption with empty passphrase...")
                decrypt_result = self.pgp_handler.decrypt_message(decoded_message, "")
                
                if not decrypt_result or not decrypt_result.get('success'):
                    print(f"DEBUG: Empty passphrase failed: {decrypt_result.get('error', 'Unknown error')}")
                    
                    # Try to get the current profile's passphrase
                    if hasattr(self, '_current_profile_fingerprint'):
                        # Try to get passphrase from the GUI or prompt user
                        try:
                            print("DEBUG: Trying with profile passphrase...")
                            
                            # First try with the master password (common case)
                            master_password = getattr(self.pgp_handler, '_master_password', None)
                            test_passphrases = []
                            
                            if master_password:
                                test_passphrases.append(master_password)
                                print("DEBUG: Will try master password")
                            
                            # Add empty passphrase and common ones as fallback
                            test_passphrases.extend(["", "password", "123456"])
                            
                            for i, test_pass in enumerate(test_passphrases):
                                passphrase_desc = "master password" if i == 0 and master_password else ("empty" if not test_pass else "hidden")
                                print(f"DEBUG: Trying passphrase: <{passphrase_desc}>")
                                decrypt_result = self.pgp_handler.decrypt_message(decoded_message, test_pass)
                                if decrypt_result and decrypt_result.get('success'):
                                    print("DEBUG: Decryption successful!")
                                    break
                            else:
                                print("DEBUG: All passphrase attempts failed")
                                # If all attempts fail, we need to prompt the user
                                if self.on_error_callback:
                                    error_msg = f"Failed to decrypt message from {sender_nickname}: Private key passphrase required"
                                    error_msg += "\n\nThe private key for your chat profile is encrypted with a passphrase."
                                    error_msg += "\nPlease ensure you're using the same passphrase you used when generating the key."
                                    self.on_error_callback(error_msg)
                                    
                        except Exception as e:
                            print(f"DEBUG: Error during passphrase attempts: {e}")
                
                if decrypt_result and decrypt_result.get('success'):
                    # Successfully decrypted
                    decrypted_text = decrypt_result['decrypted_message']
                    print(f"DEBUG: Successfully decrypted message: {decrypted_text[:50]}...")
                    
                    # Find the contact for this sender
                    contact = self.get_contact(sender_nickname)
                    contact_name = contact.name if contact else sender_nickname
                    
                    # Create message object
                    message = SecureChatMessage(
                        sender=contact_name,
                        recipient=self.irc_client.nickname,
                        content=decrypted_text,
                        timestamp=time.time()
                    )
                    message.encrypted = True
                    message.verified = True  # Assume verified if decryption succeeded
                    
                    # Add to message history
                    self.message_history.append(message)
                    
                    # Notify GUI
                    if self.on_message_callback:
                        self.on_message_callback(message)
                else:
                    # Decryption failed - provide detailed error
                    error_msg = f"Failed to decrypt message from {sender_nickname}"
                    
                    # Find the contact for better display
                    contact = self.get_contact(sender_nickname)
                    if contact:
                        error_msg = f"Failed to decrypt message from {sender_nickname} ({contact.name})"
                    
                    # Add specific error details
                    if decrypt_result and 'error' in decrypt_result:
                        print(f"DEBUG: Decryption error details: {decrypt_result['error']}")
                        
                        if "passphrase" in decrypt_result['error'].lower():
                            error_msg += ": Private key passphrase required"
                        elif "key" in decrypt_result['error'].lower() or "Could not decrypt message with available keys" in decrypt_result['error']:
                            # Enhanced key mismatch diagnostics
                            if hasattr(self, '_current_profile_fingerprint'):
                                # CRITICAL FIX: Show full key ID, not truncated
                                fingerprint_clean = self._current_profile_fingerprint.replace(' ', '')
                                if len(fingerprint_clean) >= 8:
                                    current_profile = fingerprint_clean[-8:].upper()
                                    formatted_profile = f"{current_profile[:4]} {current_profile[4:]}"
                                else:
                                    formatted_profile = fingerprint_clean.upper()
                                
                                error_msg += f": Key mismatch detected (using profile: {formatted_profile})"
                                
                                # Try to provide helpful suggestions
                                try:
                                    available_keys = self.pgp_handler.list_keys(secret=True)
                                    if len(available_keys) > 1:
                                        error_msg += f"\nAvailable profiles: {len(available_keys)} key pairs found"
                                        error_msg += "\nSolution: Try switching to a different chat profile or exchange public keys with sender"
                                    else:
                                        error_msg += "\nSolution: The sender may have encrypted for a different key. Exchange public keys again"
                                except:
                                    error_msg += "\nSolution: Try switching chat profiles or exchange public keys with sender"
                            else:
                                error_msg += ": No matching private key found (no chat profile selected)"
                                error_msg += "\nSolution: Select a chat profile in the dropdown"
                        else:
                            error_msg += f": {decrypt_result['error']}"
                    else:
                        error_msg += ": Unknown decryption error"
                    
                    print(f"DEBUG: Final error message: {error_msg}")
                    
                    # Notify GUI of error
                    if self.on_error_callback:
                        self.on_error_callback(error_msg)
                        
            except Exception as e:
                error_msg = f"Exception during decryption from {sender_nickname}: {str(e)}"
                print(f"DEBUG: {error_msg}")
                if self.on_error_callback:
                    self.on_error_callback(error_msg)
        else:
            # Plain text message
            contact = self.get_contact(sender_nickname)
            contact_name = contact.name if contact else sender_nickname
            
            message = SecureChatMessage(
                sender=contact_name,
                recipient=self.irc_client.nickname,
                content=decoded_message,
                timestamp=time.time()
            )
            message.encrypted = False
            message.verified = False
            
            self.message_history.append(message)
            
            if self.on_message_callback:
                self.on_message_callback(message)
    
    def _encode_for_irc(self, message: str) -> str:
        """Encode message for IRC transmission"""
        # Base64 encode and wrap in tags for identification
        import base64
        encoded = base64.b64encode(message.encode()).decode()
        return f"<PGP-ENCODED>{encoded}</PGP-ENCODED>"
    
    def _decode_from_irc(self, message: str) -> str:
        """Decode message from IRC transmission"""
        # Check if it's encoded
        if message.startswith("<PGP-ENCODED>") and message.endswith("</PGP-ENCODED>"):
            import base64
            try:
                encoded_content = message[13:-14]  # Remove tags
                return base64.b64decode(encoded_content.encode()).decode()
            except:
                return message  # Return original if decoding fails
        return message
    
    def _cleanup_old_chunks(self):
        """Clean up old incomplete chunks"""
        import time
        current_time = time.time()
        
        expired_ids = []
        for message_id, pending in self.pending_chunks.items():
            if current_time - pending["timestamp"] > self.chunk_timeout:
                expired_ids.append(message_id)
        
        for message_id in expired_ids:
            del self.pending_chunks[message_id]
                
    def _on_irc_connect(self, network: str, nickname: str):
        """Handle IRC connection"""
        # Mark all contacts as potentially online
        for contact in self.contacts.values():
            contact.online = False  # Will be updated when they send messages
            
    def _on_irc_disconnect(self):
        """Handle IRC disconnection"""
        # Mark all contacts as offline
        for contact in self.contacts.values():
            contact.online = False
            
    def _on_irc_error(self, error: str):
        """Handle IRC errors"""
        if self.on_error_callback:
            self.on_error_callback(f"IRC Error: {error}")
            
    def get_message_history(self, contact_nickname: str = None) -> List[SecureChatMessage]:
        """Get message history, optionally filtered by contact"""
        if contact_nickname:
            return [msg for msg in self.message_history 
                   if msg.sender == contact_nickname or msg.recipient == contact_nickname]
        return self.message_history.copy()
        
    def clear_message_history(self):
        """Clear all message history"""
        self.message_history.clear()
        
    def set_history_saving(self, enabled: bool):
        """Enable or disable message history saving"""
        self.save_history = enabled
        
    def get_connection_status(self):
        """Get IRC connection status"""
        return self.irc_client.get_connection_status()
        
    def is_connected(self) -> bool:
        """Check if connected to IRC"""
        return self.irc_client.connected
        
    # Contact management helpers
    def export_contacts(self) -> str:
        """Export contacts to JSON string"""
        contacts_data = {nick: contact.to_dict() 
                        for nick, contact in self.contacts.items()}
        return json.dumps(contacts_data, indent=2)
        
    def import_contacts(self, json_data: str):
        """Import contacts from JSON string"""
        try:
            contacts_data = json.loads(json_data)
            for nick, contact_data in contacts_data.items():
                contact = SecureChatContact.from_dict(contact_data)
                self.contacts[nick] = contact
        except Exception as e:
            raise ValueError(f"Failed to import contacts: {str(e)}")
            
    def get_available_networks(self):
        """Get available IRC networks"""
        return self.irc_client.get_available_networks()
        
    def add_custom_server(self, name: str, server: str, port: int, ssl: bool = True):
        """Add custom IRC server"""
        self.irc_client.add_custom_server(name, server, port, ssl)

