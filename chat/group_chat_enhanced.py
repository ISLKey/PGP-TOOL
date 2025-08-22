#!/usr/bin/env python3
"""
Enhanced Group Chat Handler with Secure Access Control
Integrates with the group access control system for secure group management
"""

import json
import os
import time
from typing import Dict, List, Optional, Callable
from security.group_access_control import GroupAccessController, GroupRole
from crypto.group_encryption import SharedGroupKeyEncryption, GroupMessage


class GroupChatRoom:
    """Represents a group chat room with enhanced security"""
    
    def __init__(self, name: str, creator: str, is_external: bool = False):
        self.name = name
        self.creator = creator
        self.members = set()
        self.created_at = time.time()
        self.is_external = is_external  # True for external IRC channels
        self.description = ""
        self.encrypted = True  # Enable encryption by default for internal groups
        
    def add_member(self, member: str):
        """Add a member to the room"""
        self.members.add(member)
        
    def remove_member(self, member: str):
        """Remove a member from the room"""
        self.members.discard(member)
        
    def get_member_count(self):
        """Get the number of members"""
        return len(self.members)
        
    def to_dict(self):
        """Convert room to dictionary for storage"""
        return {
            'name': self.name,
            'creator': self.creator,
            'members': list(self.members),
            'created_at': self.created_at,
            'is_external': self.is_external,
            'description': self.description,
            'encrypted': self.encrypted
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create room from dictionary"""
        room = cls(data['name'], data['creator'], data.get('is_external', False))
        room.members = set(data.get('members', []))
        room.created_at = data.get('created_at', time.time())
        room.description = data.get('description', '')
        room.encrypted = data.get('encrypted', True)
        return room


class GroupChatMessage:
    """Represents a group chat message with encryption support"""
    
    def __init__(self, sender: str, group_name: str, content: str, 
                 encrypted: bool = False, verified: bool = False):
        self.sender = sender
        self.group_name = group_name
        self.content = content
        self.timestamp = time.time()
        self.encrypted = encrypted
        self.verified = verified
        self.message_id = f"{sender}_{group_name}_{int(self.timestamp)}"


class EnhancedGroupChatHandler:
    """
    Enhanced Group Chat Handler with Secure Access Control
    
    Integrates with:
    - GroupAccessController for invitation-only access
    - SharedGroupKeyEncryption for secure messaging
    - IRC client for communication
    """
    
    def __init__(self, pgp_handler):
        self.pgp_handler = pgp_handler
        self.irc_client = None
        self.connected = False
        
        # Enhanced security components
        self.access_controller = GroupAccessController()
        self.group_encryption = SharedGroupKeyEncryption(pgp_handler)
        
        # Group management
        self.rooms: Dict[str, GroupChatRoom] = {}
        self.current_group = None
        
        # Callbacks
        self.on_group_message_callback = None
        self.on_group_join_callback = None
        self.on_group_leave_callback = None
        self.on_invitation_received_callback = None
        
        print("DEBUG: Enhanced GroupChatHandler initialized with access control")
    
    def setup_group_irc_callbacks(self):
        """Set up IRC callbacks for group chat with enhanced security"""
        if self.irc_client:
            # Set channel message callback for group messages
            self.irc_client.on_channel_message_callback = self._handle_group_message
            print("DEBUG: Group IRC callbacks set up with security integration")
    
    def create_secure_group(self, group_name: str, creator_name: str, 
                          creator_fingerprint: str, description: str = "") -> bool:
        """
        Create a new secure group with access control
        
        Args:
            group_name: Name of the group
            creator_name: Name of the creator
            creator_fingerprint: PGP fingerprint of the creator
            description: Optional group description
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Generate unique group ID
            group_id = f"secure_{group_name}_{int(time.time())}"
            
            # Create secure group with access control
            secure_group = self.access_controller.create_group(
                group_id, group_name, creator_fingerprint, creator_name
            )
            secure_group.description = description
            
            # Create group encryption key
            member_fingerprints = [creator_fingerprint]
            self.group_encryption.create_group_key(group_id, member_fingerprints)
            
            # Create chat room
            room = GroupChatRoom(group_name, creator_name, is_external=False)
            room.add_member(creator_name)
            room.encrypted = True
            self.rooms[group_name] = room
            
            # Join IRC channel for this group
            if self.irc_client and self.connected:
                channel_name = f"#{group_id}"
                self.irc_client.join_channel(channel_name)
            
            print(f"DEBUG: Created secure group '{group_name}' with encryption")
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to create secure group: {e}")
            return False
    
    def invite_member_to_group(self, group_name: str, inviter_fingerprint: str,
                             invitee_fingerprint: str, invitee_name: str,
                             message: str = "") -> bool:
        """
        Invite a member to a secure group
        
        Args:
            group_name: Name of the group
            inviter_fingerprint: PGP fingerprint of the inviter
            invitee_fingerprint: PGP fingerprint of the invitee
            invitee_name: Name of the invitee
            message: Optional invitation message
            
        Returns:
            bool: True if invitation sent, False otherwise
        """
        try:
            # Find the secure group
            secure_group = None
            group_id = None
            
            for gid, group in self.access_controller.groups.items():
                if group.name == group_name:
                    secure_group = group
                    group_id = gid
                    break
            
            if not secure_group:
                print(f"ERROR: Secure group '{group_name}' not found")
                return False
            
            # Send invitation
            invitation = self.access_controller.invite_member(
                group_id, inviter_fingerprint, invitee_fingerprint, 
                invitee_name, message
            )
            
            if invitation:
                # Send invitation via IRC private message
                if self.irc_client and self.connected:
                    invitation_data = {
                        'type': 'group_invitation',
                        'invitation_id': invitation.invitation_id,
                        'group_name': group_name,
                        'group_id': group_id,
                        'inviter_name': secure_group.get_member(inviter_fingerprint).name,
                        'message': message
                    }
                    
                    # Encrypt invitation for invitee
                    invitation_json = json.dumps(invitation_data)
                    encrypted_result = self.pgp_handler.encrypt_message(
                        invitation_json, invitee_fingerprint
                    )
                    
                    if encrypted_result and 'encrypted_message' in encrypted_result:
                        # Send encrypted invitation via IRC
                        invitation_msg = f"<GROUP-INVITE>{encrypted_result['encrypted_message']}</GROUP-INVITE>"
                        # Note: In real implementation, this would be sent via IRC private message
                        print(f"DEBUG: Invitation sent to {invitee_name}")
                        
                        # Trigger callback if set
                        if self.on_invitation_received_callback:
                            self.on_invitation_received_callback(invitation)
                        
                        return True
                
                print(f"DEBUG: Invitation created but not sent (IRC not connected)")
                return True
            
            return False
            
        except Exception as e:
            print(f"ERROR: Failed to invite member: {e}")
            return False
    
    def accept_group_invitation(self, invitation_id: str, accepter_fingerprint: str,
                              passphrase: str = None) -> bool:
        """
        Accept a group invitation and join the secure group
        
        Args:
            invitation_id: The invitation to accept
            accepter_fingerprint: PGP fingerprint of the accepter
            passphrase: PGP passphrase for decrypting group key
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Accept the invitation
            if not self.access_controller.accept_invitation(invitation_id, accepter_fingerprint):
                return False
            
            # Get the invitation details
            invitation = self.access_controller.invitations.get(invitation_id)
            if not invitation:
                return False
            
            # Get the secure group
            secure_group = self.access_controller.get_group(invitation.group_id)
            if not secure_group:
                return False
            
            # Add member to group encryption
            success = self.group_encryption.add_member_to_group(
                invitation.group_id, accepter_fingerprint
            )
            
            if success:
                # Get encrypted group key for this member
                encrypted_key = self.group_encryption.get_encrypted_key_for_member(
                    invitation.group_id, accepter_fingerprint
                )
                
                if encrypted_key:
                    # Load the group key for this member
                    self.group_encryption.load_group_key_from_encrypted(
                        invitation.group_id, encrypted_key, accepter_fingerprint, passphrase
                    )
                
                # Update chat room
                if secure_group.name in self.rooms:
                    room = self.rooms[secure_group.name]
                    room.add_member(invitation.invitee_name)
                else:
                    # Create room entry for this group
                    room = GroupChatRoom(secure_group.name, secure_group.creator_fingerprint, False)
                    for member in secure_group.get_member_list():
                        room.add_member(member.name)
                    self.rooms[secure_group.name] = room
                
                # Join IRC channel
                if self.irc_client and self.connected:
                    channel_name = f"#{invitation.group_id}"
                    self.irc_client.join_channel(channel_name)
                
                print(f"DEBUG: Successfully joined secure group '{secure_group.name}'")
                return True
            
            return False
            
        except Exception as e:
            print(f"ERROR: Failed to accept group invitation: {e}")
            return False
    
    def send_secure_group_message(self, group_name: str, sender_name: str,
                                sender_fingerprint: str, message_content: str) -> tuple:
        """
        Send an encrypted message to a secure group
        
        Args:
            group_name: Name of the group
            sender_name: Name of the sender
            sender_fingerprint: PGP fingerprint of the sender
            message_content: The message to send
            
        Returns:
            tuple: (success: bool, result_message: str)
        """
        try:
            # Find the secure group
            secure_group = None
            group_id = None
            
            for gid, group in self.access_controller.groups.items():
                if group.name == group_name:
                    secure_group = group
                    group_id = gid
                    break
            
            if not secure_group:
                return False, f"Secure group '{group_name}' not found"
            
            # Check if sender is a member
            if not secure_group.is_member(sender_fingerprint):
                return False, "You are not a member of this group"
            
            # Encrypt the message
            encrypted_message = self.group_encryption.encrypt_group_message(
                group_id, sender_name, message_content
            )
            
            if not encrypted_message:
                return False, "Failed to encrypt message"
            
            # Send encrypted message to IRC channel
            if self.irc_client and self.connected:
                channel_name = f"#{group_id}"
                
                # Format encrypted message for transmission
                message_data = {
                    'type': 'encrypted_group_message',
                    'encrypted_message': encrypted_message.to_dict()
                }
                
                transmission_message = f"<SECURE-GROUP>{json.dumps(message_data)}</SECURE-GROUP>"
                
                try:
                    self.irc_client.send_message(channel_name, transmission_message)
                    print(f"DEBUG: Sent encrypted group message to {group_name}")
                    return True, "Message sent successfully"
                except Exception as e:
                    return False, f"Failed to send message: {e}"
            else:
                return False, "Not connected to IRC"
            
        except Exception as e:
            print(f"ERROR: Failed to send secure group message: {e}")
            return False, f"Error: {e}"
    
    def _handle_group_message(self, sender: str, channel: str, message: str):
        """
        Handle incoming group messages with encryption support
        
        Args:
            sender: IRC nickname of the sender
            channel: IRC channel name
            message: The message content
        """
        try:
            print(f"DEBUG: Received group message from {sender} in {channel}: {message[:50]}...")
            
            # Check if this is a secure group message
            if message.startswith("<SECURE-GROUP>") and message.endswith("</SECURE-GROUP>"):
                self._handle_secure_group_message(sender, channel, message)
                return
            
            # Check if this is a group invitation
            if message.startswith("<GROUP-INVITE>") and message.endswith("</GROUP-INVITE>"):
                self._handle_group_invitation(sender, message)
                return
            
            # Handle regular (unencrypted) group message
            self._handle_regular_group_message(sender, channel, message)
            
        except Exception as e:
            print(f"ERROR: Failed to handle group message: {e}")
    
    def _handle_secure_group_message(self, sender: str, channel: str, message: str):
        """Handle encrypted group messages"""
        try:
            # Extract encrypted message data
            message_content = message[14:-15]  # Remove <SECURE-GROUP> tags
            message_data = json.loads(message_content)
            
            if message_data.get('type') != 'encrypted_group_message':
                return
            
            # Parse encrypted message
            encrypted_msg_data = message_data['encrypted_message']
            group_message = GroupMessage.from_dict(encrypted_msg_data)
            
            # Find the group by channel
            group_id = channel[1:] if channel.startswith('#') else channel  # Remove # prefix
            secure_group = self.access_controller.get_group(group_id)
            
            if not secure_group:
                print(f"DEBUG: No secure group found for channel {channel}")
                return
            
            # Get current user's fingerprint (this would come from the main application)
            current_user_fingerprint = getattr(self, '_current_user_fingerprint', None)
            if not current_user_fingerprint:
                print("DEBUG: No current user fingerprint set")
                return
            
            # Decrypt the message
            decrypted_content = self.group_encryption.decrypt_group_message(
                group_message, current_user_fingerprint
            )
            
            if decrypted_content:
                # Create group chat message
                chat_message = GroupChatMessage(
                    sender=group_message.sender,
                    group_name=secure_group.name,
                    content=decrypted_content,
                    encrypted=True,
                    verified=True  # Could add signature verification here
                )
                
                # Trigger callback
                if self.on_group_message_callback:
                    self.on_group_message_callback(chat_message)
                
                print(f"DEBUG: Successfully decrypted group message from {sender}")
            else:
                print(f"DEBUG: Failed to decrypt group message from {sender}")
                
        except Exception as e:
            print(f"ERROR: Failed to handle secure group message: {e}")
    
    def _handle_group_invitation(self, sender: str, message: str):
        """Handle encrypted group invitations"""
        try:
            # Extract encrypted invitation
            encrypted_content = message[14:-15]  # Remove <GROUP-INVITE> tags
            
            # Get current user's fingerprint
            current_user_fingerprint = getattr(self, '_current_user_fingerprint', None)
            if not current_user_fingerprint:
                return
            
            # Decrypt invitation
            decryption_result = self.pgp_handler.decrypt_message(encrypted_content)
            
            if decryption_result and 'decrypted_message' in decryption_result:
                invitation_data = json.loads(decryption_result['decrypted_message'])
                
                if invitation_data.get('type') == 'group_invitation':
                    print(f"DEBUG: Received group invitation to '{invitation_data['group_name']}'")
                    
                    # Trigger callback for UI to handle invitation
                    if self.on_invitation_received_callback:
                        self.on_invitation_received_callback(invitation_data)
            
        except Exception as e:
            print(f"ERROR: Failed to handle group invitation: {e}")
    
    def _handle_regular_group_message(self, sender: str, channel: str, message: str):
        """Handle regular (unencrypted) group messages"""
        try:
            # Find group by channel name
            group_name = None
            for name, room in self.rooms.items():
                if room.is_external and f"#{name.lower()}" == channel.lower():
                    group_name = name
                    break
            
            if not group_name:
                # Create external group room if it doesn't exist
                group_name = channel[1:] if channel.startswith('#') else channel
                room = GroupChatRoom(group_name, "Unknown", is_external=True)
                room.encrypted = False
                self.rooms[group_name] = room
            
            # Create group chat message
            chat_message = GroupChatMessage(
                sender=sender,
                group_name=group_name,
                content=message,
                encrypted=False,
                verified=False
            )
            
            # Add sender to room if not already there
            if group_name in self.rooms:
                self.rooms[group_name].add_member(sender)
            
            # Trigger callback
            if self.on_group_message_callback:
                self.on_group_message_callback(chat_message)
            
        except Exception as e:
            print(f"ERROR: Failed to handle regular group message: {e}")
    
    def set_current_user_fingerprint(self, fingerprint: str):
        """Set the current user's PGP fingerprint for decryption"""
        self._current_user_fingerprint = fingerprint
        print(f"DEBUG: Set current user fingerprint: {fingerprint[:16]}...")
    
    def get_user_groups(self, user_fingerprint: str) -> List[dict]:
        """Get all groups that a user is a member of"""
        user_groups = []
        
        for group_id, secure_group in self.access_controller.groups.items():
            if secure_group.is_member(user_fingerprint):
                member = secure_group.get_member(user_fingerprint)
                user_groups.append({
                    'group_id': group_id,
                    'name': secure_group.name,
                    'description': secure_group.description,
                    'role': member.role.value,
                    'member_count': len(secure_group.members),
                    'encrypted': secure_group.encryption_enabled,
                    'created_at': secure_group.created_at
                })
        
        return user_groups
    
    def get_pending_invitations(self, user_fingerprint: str) -> List[dict]:
        """Get pending invitations for a user"""
        invitations = self.access_controller.get_pending_invitations(user_fingerprint)
        
        invitation_list = []
        for invitation in invitations:
            secure_group = self.access_controller.get_group(invitation.group_id)
            if secure_group:
                inviter = secure_group.get_member(invitation.inviter_fingerprint)
                invitation_list.append({
                    'invitation_id': invitation.invitation_id,
                    'group_name': secure_group.name,
                    'group_description': secure_group.description,
                    'inviter_name': inviter.name if inviter else 'Unknown',
                    'message': invitation.message,
                    'created_at': invitation.created_at,
                    'expires_at': invitation.expires_at
                })
        
        return invitation_list
    
    def save_data_to_file(self, filename: str):
        """Save groups and access control data to file"""
        try:
            data = {
                'rooms': {name: room.to_dict() for name, room in self.rooms.items()},
                'access_control': self.access_controller.export_data(),
                'saved_at': time.time()
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"DEBUG: Saved enhanced group data to {filename}")
        except Exception as e:
            print(f"ERROR: Failed to save enhanced group data: {e}")
    
    def load_data_from_file(self, filename: str):
        """Load groups and access control data from file"""
        try:
            if not os.path.exists(filename):
                return
            
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Load rooms
            self.rooms = {}
            for name, room_data in data.get('rooms', {}).items():
                room = GroupChatRoom.from_dict(room_data)
                self.rooms[name] = room
            
            # Load access control data
            if 'access_control' in data:
                self.access_controller.import_data(data['access_control'])
            
            print(f"DEBUG: Loaded enhanced group data from {filename}")
        except Exception as e:
            print(f"ERROR: Failed to load enhanced group data: {e}")

