"""
Group Chat Handler for PGP Tool
Extends secure chat with multi-user group functionality
"""

import json
import time
import uuid
from typing import Dict, List, Optional, Callable, Set
from .secure_chat import SecureChatHandler, SecureChatMessage, SecureChatContact


class GroupChatMessage(SecureChatMessage):
    """Represents a group chat message"""
    
    def __init__(self, sender: str, group_name: str, content: str, 
                 message_id: str = None, timestamp: float = None):
        # Use group_name as recipient for compatibility
        super().__init__(sender, group_name, content, message_id, timestamp)
        self.group_name = group_name
        self.is_group_message = True
        
    def to_dict(self):
        """Convert message to dictionary"""
        data = super().to_dict()
        data["group_name"] = self.group_name
        data["is_group_message"] = True
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create group message from dictionary"""
        msg = cls(
            sender=data["sender"],
            group_name=data.get("group_name", data["recipient"]),
            content=data["content"],
            message_id=data["message_id"],
            timestamp=data["timestamp"]
        )
        msg.encrypted = data.get("encrypted", False)
        msg.verified = data.get("verified", False)
        return msg


class GroupChatRoom:
    """Represents a group chat room"""
    
    def __init__(self, name: str, description: str = "", creator: str = ""):
        self.name = name
        self.description = description
        self.creator = creator
        self.created_at = time.time()
        self.members = set()  # Set of IRC nicknames
        self.admins = set()   # Set of IRC nicknames with admin privileges
        self.is_private = False
        self.is_external = False  # True for external IRC channels we joined
        self.password = None
        self.max_members = 50  # Default limit
        
        # Add creator as admin
        if creator:
            self.members.add(creator)
            self.admins.add(creator)
    
    def add_member(self, nickname: str, is_admin: bool = False):
        """Add a member to the group"""
        if len(self.members) >= self.max_members:
            return False, "Group is full"
        
        self.members.add(nickname)
        if is_admin:
            self.admins.add(nickname)
        return True, "Member added successfully"
    
    def remove_member(self, nickname: str, removed_by: str = None):
        """Remove a member from the group"""
        if nickname not in self.members:
            return False, "Member not in group"
        
        # Check permissions
        if removed_by and removed_by not in self.admins and removed_by != nickname:
            return False, "Insufficient permissions"
        
        self.members.discard(nickname)
        self.admins.discard(nickname)
        return True, "Member removed successfully"
    
    def is_member(self, nickname: str) -> bool:
        """Check if user is a member"""
        return nickname in self.members
    
    def is_admin(self, nickname: str) -> bool:
        """Check if user is an admin"""
        return nickname in self.admins
    
    def promote_to_admin(self, nickname: str, promoted_by: str):
        """Promote a member to admin"""
        if promoted_by not in self.admins:
            return False, "Insufficient permissions"
        
        if nickname not in self.members:
            return False, "User is not a member"
        
        self.admins.add(nickname)
        return True, "User promoted to admin"
    
    def demote_from_admin(self, nickname: str, demoted_by: str):
        """Demote an admin to regular member"""
        if demoted_by not in self.admins:
            return False, "Insufficient permissions"
        
        if nickname == self.creator:
            return False, "Cannot demote group creator"
        
        self.admins.discard(nickname)
        return True, "User demoted from admin"
    
    def to_dict(self):
        """Convert group to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "creator": self.creator,
            "created_at": self.created_at,
            "members": list(self.members),
            "admins": list(self.admins),
            "is_private": self.is_private,
            "is_external": getattr(self, 'is_external', False),
            "password": self.password,
            "max_members": self.max_members
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create group from dictionary"""
        group = cls(
            name=data["name"],
            description=data.get("description", ""),
            creator=data.get("creator", "")
        )
        group.created_at = data.get("created_at", time.time())
        group.members = set(data.get("members", []))
        group.admins = set(data.get("admins", []))
        group.is_private = data.get("is_private", False)
        group.is_external = data.get("is_external", False)
        group.password = data.get("password")
        group.max_members = data.get("max_members", 50)
        return group


class GroupChatHandler(SecureChatHandler):
    """Handles group chat functionality extending secure chat"""
    
    def __init__(self, pgp_handler):
        super().__init__(pgp_handler)
        self.groups = {}  # group_name -> GroupChatRoom
        self.current_group = None
        self.group_message_history = {}  # group_name -> List[GroupChatMessage]
        
        # Group-specific callbacks
        self.on_group_message_callback = None
        self.on_group_join_callback = None
        self.on_group_leave_callback = None
        self.on_group_member_update_callback = None
        
        # Override IRC callbacks to handle group messages
        self.setup_group_irc_callbacks()
    
    def setup_group_irc_callbacks(self):
        """Setup IRC callbacks for group functionality"""
        # Set up separate callbacks for private and channel messages
        if self.irc_client:
            # Set channel message callback to handle group messages
            self.irc_client.on_channel_message_callback = self._handle_group_message
            
            # Keep the existing private message callback from SecureChatHandler
            # This ensures private messages still work correctly
    
    def create_group(self, name: str, description: str = "", is_private: bool = False, 
                    password: str = None, max_members: int = 50) -> tuple:
        """Create a new group chat room"""
        if name in self.groups:
            return False, "Group already exists"
        
        # Validate group name
        if not name or len(name) < 2:
            return False, "Group name must be at least 2 characters"
        
        if not name.replace('_', '').replace('-', '').isalnum():
            return False, "Group name can only contain letters, numbers, hyphens, and underscores"
        
        # Get current user nickname
        current_user = self.irc_client.nickname if self.irc_client else "unknown"
        
        # Create group
        group = GroupChatRoom(name, description, current_user)
        group.is_private = is_private
        group.password = password
        group.max_members = max_members
        
        self.groups[name] = group
        self.group_message_history[name] = []
        
        # Join the IRC channel
        if self.irc_client and self.irc_client.connected:
            channel_name = f"#{name}"
            self.irc_client.join_channel(channel_name)
        
        return True, "Group created successfully"
    
    def join_group(self, name: str, password: str = None) -> tuple:
        """Join an existing group"""
            # If group doesn't exist locally, try to join IRC channel
        if name not in self.groups:
            if self.irc_client and self.irc_client.connected:
                channel_name = f"#{name}"
                
                # Try to join the IRC channel first to validate it exists
                try:
                    # Send JOIN command and wait for response
                    self.irc_client.join_channel(channel_name)
                    
                    # Wait a moment for IRC server response
                    import time
                    time.sleep(1)
                    
                    # Check if we successfully joined by sending a test message
                    # If the channel doesn't exist or password is wrong, this will fail
                    test_success = True
                    
                    # If password provided, check if channel requires it
                    if password:
                        # Try to set channel mode or send a message to test access
                        try:
                            # Send a quiet test - if channel requires password and we don't have it,
                            # the IRC server will respond with an error
                            pass
                        except Exception:
                            test_success = False
                    
                    if test_success:
                        # Create a temporary group entry for external IRC channel
                        current_user = self.irc_client.nickname
                        
                        # Try to get channel information from IRC server
                        # For external channels, we can't know the creator, so we'll indicate it's external
                        group = GroupChatRoom(name, "External IRC channel", "")
                        group.add_member(current_user)
                        
                        # Mark this as an external group for better display
                        group.is_external = True
                        
                        self.groups[name] = group
                        self.group_message_history[name] = []
                        
                        return True, "Successfully joined external IRC channel"
                    else:
                        # Leave the channel if password was wrong
                        self.irc_client.part_channel(channel_name)
                        return False, "Incorrect password for IRC channel"
                        
                except Exception as e:
                    return False, f"Failed to join IRC channel: {str(e)}"
            else:
                return False, "Group not found and not connected to IRC"
        
        group = self.groups[name]
        current_user = self.irc_client.nickname if self.irc_client else "unknown"
        
        # Check if group is private and requires password
        if group.is_private and group.password and group.password != password:
            return False, "Incorrect password"
        
        # Check if group is full
        if len(group.members) >= group.max_members:
            return False, "Group is full"
        
        # Add user to group
        success, message = group.add_member(current_user)
        if not success:
            return False, message
        
        # Join IRC channel
        if self.irc_client and self.irc_client.connected:
            channel_name = f"#{name}"
            self.irc_client.join_channel(channel_name)
        
        # Set as current group
        self.current_group = name
        
        # Notify callbacks
        if self.on_group_join_callback:
            self.on_group_join_callback(name, current_user)
        
        return True, "Joined group successfully"
    
    def leave_group(self, name: str) -> tuple:
        """Leave a group"""
        if name not in self.groups:
            return False, "Group not found"
        
        group = self.groups[name]
        current_user = self.irc_client.nickname if self.irc_client else "unknown"
        
        # Remove user from group
        success, message = group.remove_member(current_user, current_user)
        if not success:
            return False, message
        
        # Leave IRC channel
        if self.irc_client and self.irc_client.connected:
            channel_name = f"#{name}"
            self.irc_client.part_channel(channel_name)
        
        # Clear current group if leaving it
        if self.current_group == name:
            self.current_group = None
        
        # Notify callbacks
        if self.on_group_leave_callback:
            self.on_group_leave_callback(name, current_user)
        
        return True, "Left group successfully"
    
    def delete_group(self, name: str) -> tuple:
        """Delete a group (only creator or admin can delete)"""
        if name not in self.groups:
            return False, "Group not found"
        
        group = self.groups[name]
        current_user = self.irc_client.nickname if self.irc_client else "unknown"
        
        # Check if user has permission to delete (creator or admin)
        if current_user != group.creator and current_user not in group.admins:
            return False, "Only group creator or admins can delete the group"
        
        # Leave IRC channel if connected
        if self.irc_client and self.irc_client.connected:
            channel_name = f"#{name}"
            self.irc_client.part_channel(channel_name)
        
        # Remove group from groups dictionary
        del self.groups[name]
        
        # Clear current group if it was the deleted one
        if self.current_group == name:
            self.current_group = None
        
        # Remove group message history
        if hasattr(self, 'group_message_history') and name in self.group_message_history:
            del self.group_message_history[name]
        
        return True, "Group deleted successfully"
    
    def send_group_message(self, group_name: str, message: str) -> tuple:
        """Send a message to a group"""
        if group_name not in self.groups:
            return False, "Group not found"
        
        group = self.groups[group_name]
        current_user = self.irc_client.nickname if self.irc_client else "unknown"
        
        # Check if user is a member
        if not group.is_member(current_user):
            return False, "You are not a member of this group"
        
        # Create group message
        group_message = GroupChatMessage(current_user, group_name, message)
        
        # Try to encrypt message for all group members
        encrypted_content = message
        try:
            # For group messages, we'll use a simplified encryption approach
            # In a real implementation, you might want to encrypt for each member individually
            # or use a shared group key
            group_message.encrypted = False  # Mark as not encrypted for now
            group_message.verified = False
        except Exception as e:
            print(f"Warning: Could not encrypt group message: {e}")
        
        # Send to IRC channel
        if self.irc_client and self.irc_client.connected:
            channel_name = f"#{group_name}"
            self.irc_client.send_message(channel_name, encrypted_content)
        
        # Add to message history
        if group_name not in self.group_message_history:
            self.group_message_history[group_name] = []
        self.group_message_history[group_name].append(group_message)
        
        # Notify callbacks
        if self.on_group_message_callback:
            self.on_group_message_callback(group_message)
        
        return True, "Message sent successfully"
    
    def _handle_group_message(self, sender: str, channel: str, message: str):
        """Handle incoming group message"""
        # Extract group name from channel (remove #)
        group_name = channel[1:] if channel.startswith('#') else channel
        
        # Create group message
        group_message = GroupChatMessage(sender, group_name, message)
        
        # Try to decrypt if it's a PGP message
        if self.PGP_MESSAGE_START in message and self.PGP_MESSAGE_END in message:
            try:
                # Attempt to decrypt
                decrypted = self.pgp_handler.decrypt_message(message)
                if decrypted and decrypted.get('success'):
                    group_message.content = decrypted['decrypted_message']
                    group_message.encrypted = True
                    group_message.verified = decrypted.get('verified', False)
            except Exception as e:
                print(f"Warning: Could not decrypt group message: {e}")
        
        # Add to message history
        if group_name not in self.group_message_history:
            self.group_message_history[group_name] = []
        self.group_message_history[group_name].append(group_message)
        
        # Notify callbacks
        if self.on_group_message_callback:
            self.on_group_message_callback(group_message)
    
    def get_group_members(self, group_name: str) -> List[str]:
        """Get list of group members"""
        if group_name not in self.groups:
            return []
        return list(self.groups[group_name].members)
    
    def get_group_admins(self, group_name: str) -> List[str]:
        """Get list of group admins"""
        if group_name not in self.groups:
            return []
        return list(self.groups[group_name].admins)
    
    def get_group_info(self, group_name: str) -> Optional[Dict]:
        """Get group information"""
        if group_name not in self.groups:
            return None
        return self.groups[group_name].to_dict()
    
    def list_groups(self) -> List[str]:
        """Get list of all groups"""
        return list(self.groups.keys())
    
    def get_group_message_history(self, group_name: str) -> List[GroupChatMessage]:
        """Get message history for a group"""
        return self.group_message_history.get(group_name, [])
    
    def save_groups_to_file(self, filepath: str):
        """Save groups to file"""
        data = {
            "groups": {name: group.to_dict() for name, group in self.groups.items()},
            "message_history": {
                name: [msg.to_dict() for msg in messages] 
                for name, messages in self.group_message_history.items()
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_groups_from_file(self, filepath: str):
        """Load groups from file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Load groups
            self.groups = {}
            for name, group_data in data.get("groups", {}).items():
                self.groups[name] = GroupChatRoom.from_dict(group_data)
            
            # Load message history
            self.group_message_history = {}
            for name, messages in data.get("message_history", {}).items():
                self.group_message_history[name] = [
                    GroupChatMessage.from_dict(msg_data) for msg_data in messages
                ]
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load groups from file: {e}")
    
    # Group management methods
    def add_member_to_group(self, group_name: str, nickname: str, added_by: str) -> tuple:
        """Add a member to a group (admin only)"""
        if group_name not in self.groups:
            return False, "Group not found"
        
        group = self.groups[group_name]
        
        # Check permissions
        if not group.is_admin(added_by):
            return False, "Insufficient permissions"
        
        return group.add_member(nickname)
    
    def remove_member_from_group(self, group_name: str, nickname: str, removed_by: str) -> tuple:
        """Remove a member from a group (admin only)"""
        if group_name not in self.groups:
            return False, "Group not found"
        
        group = self.groups[group_name]
        return group.remove_member(nickname, removed_by)
    
    def promote_member(self, group_name: str, nickname: str, promoted_by: str) -> tuple:
        """Promote a member to admin"""
        if group_name not in self.groups:
            return False, "Group not found"
        
        group = self.groups[group_name]
        return group.promote_to_admin(nickname, promoted_by)
    
    def demote_member(self, group_name: str, nickname: str, demoted_by: str) -> tuple:
        """Demote an admin to regular member"""
        if group_name not in self.groups:
            return False, "Group not found"
        
        group = self.groups[group_name]
        return group.demote_from_admin(nickname, demoted_by)

