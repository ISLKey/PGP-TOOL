#!/usr/bin/env python3
"""
Shared Group Key Encryption for PGP Tool
Implements Method 2: Shared Group Key approach for secure group chat

This module provides:
- AES-256 symmetric encryption for group messages
- PGP encryption of group keys for each member
- Key distribution and management
- Secure group message encryption/decryption
"""

import os
import json
import time
import base64
import hashlib
from typing import Dict, List, Optional, Tuple
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import secrets


class GroupKey:
    """Represents a symmetric group encryption key"""
    
    def __init__(self, key_data: bytes = None, key_id: str = None):
        self.key_data = key_data or secrets.token_bytes(32)  # 256-bit AES key
        self.key_id = key_id or self._generate_key_id()
        self.created_at = time.time()
        self.version = 1
        
    def _generate_key_id(self) -> str:
        """Generate a unique identifier for this group key"""
        # Create a hash of the key data for identification
        hash_obj = hashlib.sha256(self.key_data)
        return hash_obj.hexdigest()[:16]  # Use first 16 chars as key ID
    
    def to_dict(self) -> dict:
        """Convert group key to dictionary for storage"""
        return {
            'key_data': base64.b64encode(self.key_data).decode(),
            'key_id': self.key_id,
            'created_at': self.created_at,
            'version': self.version
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GroupKey':
        """Create group key from dictionary"""
        key = cls()
        key.key_data = base64.b64decode(data['key_data'])
        key.key_id = data['key_id']
        key.created_at = data.get('created_at', time.time())
        key.version = data.get('version', 1)
        return key


class EncryptedGroupKey:
    """Represents a group key encrypted for a specific member"""
    
    def __init__(self, member_fingerprint: str, encrypted_key_data: str, key_id: str):
        self.member_fingerprint = member_fingerprint
        self.encrypted_key_data = encrypted_key_data  # PGP-encrypted group key
        self.key_id = key_id
        self.created_at = time.time()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return {
            'member_fingerprint': self.member_fingerprint,
            'encrypted_key_data': self.encrypted_key_data,
            'key_id': self.key_id,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'EncryptedGroupKey':
        """Create from dictionary"""
        return cls(
            data['member_fingerprint'],
            data['encrypted_key_data'],
            data['key_id']
        )


class GroupMessage:
    """Represents an encrypted group message"""
    
    def __init__(self, sender: str, group_id: str, encrypted_content: str, 
                 key_id: str, iv: str, timestamp: float = None):
        self.sender = sender
        self.group_id = group_id
        self.encrypted_content = encrypted_content
        self.key_id = key_id  # Which group key was used
        self.iv = iv  # Initialization vector for AES
        self.timestamp = timestamp or time.time()
        self.message_id = self._generate_message_id()
    
    def _generate_message_id(self) -> str:
        """Generate unique message ID"""
        data = f"{self.sender}{self.group_id}{self.timestamp}".encode()
        return hashlib.sha256(data).hexdigest()[:12]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for transmission"""
        return {
            'sender': self.sender,
            'group_id': self.group_id,
            'encrypted_content': self.encrypted_content,
            'key_id': self.key_id,
            'iv': self.iv,
            'timestamp': self.timestamp,
            'message_id': self.message_id
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GroupMessage':
        """Create from dictionary"""
        msg = cls(
            data['sender'],
            data['group_id'],
            data['encrypted_content'],
            data['key_id'],
            data['iv'],
            data.get('timestamp')
        )
        msg.message_id = data.get('message_id', msg.message_id)
        return msg


class SharedGroupKeyEncryption:
    """
    Implements shared group key encryption for secure group chat
    
    This class provides:
    - Group key generation and management
    - Member key distribution
    - Message encryption/decryption
    - Key rotation capabilities
    """
    
    def __init__(self, pgp_handler):
        self.pgp_handler = pgp_handler
        self.group_keys: Dict[str, GroupKey] = {}  # group_id -> GroupKey
        self.member_keys: Dict[str, Dict[str, EncryptedGroupKey]] = {}  # group_id -> {fingerprint -> EncryptedGroupKey}
        self.backend = default_backend()
    
    def create_group_key(self, group_id: str, member_fingerprints: List[str]) -> GroupKey:
        """
        Create a new group key and encrypt it for all members
        
        Args:
            group_id: Unique identifier for the group
            member_fingerprints: List of PGP fingerprints for group members
            
        Returns:
            GroupKey: The generated group key
            
        Raises:
            ValueError: If unable to encrypt key for any member
        """
        print(f"DEBUG: Creating group key for group '{group_id}' with {len(member_fingerprints)} members")
        
        # Generate new group key
        group_key = GroupKey()
        self.group_keys[group_id] = group_key
        
        # Initialize member keys storage for this group
        self.member_keys[group_id] = {}
        
        # Encrypt group key for each member
        for fingerprint in member_fingerprints:
            try:
                encrypted_key = self._encrypt_group_key_for_member(group_key, fingerprint)
                self.member_keys[group_id][fingerprint] = encrypted_key
                print(f"DEBUG: Successfully encrypted group key for member {fingerprint[:16]}...")
            except Exception as e:
                print(f"ERROR: Failed to encrypt group key for member {fingerprint}: {e}")
                raise ValueError(f"Failed to encrypt group key for member {fingerprint}: {e}")
        
        print(f"DEBUG: Group key created successfully. Key ID: {group_key.key_id}")
        return group_key
    
    def _encrypt_group_key_for_member(self, group_key: GroupKey, member_fingerprint: str) -> EncryptedGroupKey:
        """
        Encrypt a group key for a specific member using their PGP public key
        
        Args:
            group_key: The group key to encrypt
            member_fingerprint: PGP fingerprint of the member
            
        Returns:
            EncryptedGroupKey: The encrypted group key for this member
        """
        try:
            # Get member's public key
            public_key = self.pgp_handler.get_public_key(member_fingerprint)
            if not public_key:
                raise ValueError(f"Public key not found for fingerprint {member_fingerprint}")
            
            # Create a message containing the group key
            key_message = json.dumps({
                'group_key': base64.b64encode(group_key.key_data).decode(),
                'key_id': group_key.key_id,
                'created_at': group_key.created_at,
                'version': group_key.version
            })
            
            # Encrypt the key message with member's public key
            encrypted_result = self.pgp_handler.encrypt_message(key_message, member_fingerprint)
            
            if not encrypted_result or 'encrypted_message' not in encrypted_result:
                raise ValueError("PGP encryption failed")
            
            return EncryptedGroupKey(
                member_fingerprint=member_fingerprint,
                encrypted_key_data=encrypted_result['encrypted_message'],
                key_id=group_key.key_id
            )
            
        except Exception as e:
            print(f"DEBUG: Error encrypting group key for {member_fingerprint}: {e}")
            raise
    
    def add_member_to_group(self, group_id: str, member_fingerprint: str) -> bool:
        """
        Add a new member to an existing group by encrypting the group key for them
        
        Args:
            group_id: The group to add the member to
            member_fingerprint: PGP fingerprint of the new member
            
        Returns:
            bool: True if successful, False otherwise
        """
        if group_id not in self.group_keys:
            print(f"ERROR: Group {group_id} not found")
            return False
        
        if group_id not in self.member_keys:
            self.member_keys[group_id] = {}
        
        try:
            group_key = self.group_keys[group_id]
            encrypted_key = self._encrypt_group_key_for_member(group_key, member_fingerprint)
            self.member_keys[group_id][member_fingerprint] = encrypted_key
            
            print(f"DEBUG: Successfully added member {member_fingerprint[:16]}... to group {group_id}")
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to add member to group: {e}")
            return False
    
    def remove_member_from_group(self, group_id: str, member_fingerprint: str) -> bool:
        """
        Remove a member from a group (they can no longer decrypt new messages)
        Note: For complete security, the group key should be rotated after member removal
        
        Args:
            group_id: The group to remove the member from
            member_fingerprint: PGP fingerprint of the member to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        if group_id not in self.member_keys:
            return False
        
        if member_fingerprint in self.member_keys[group_id]:
            del self.member_keys[group_id][member_fingerprint]
            print(f"DEBUG: Removed member {member_fingerprint[:16]}... from group {group_id}")
            return True
        
        return False
    
    def encrypt_group_message(self, group_id: str, sender: str, message_content: str) -> Optional[GroupMessage]:
        """
        Encrypt a message for the group using the shared group key
        
        Args:
            group_id: The group to send the message to
            sender: Identifier of the message sender
            message_content: The plaintext message to encrypt
            
        Returns:
            GroupMessage: The encrypted message, or None if encryption failed
        """
        if group_id not in self.group_keys:
            print(f"ERROR: No group key found for group {group_id}")
            return None
        
        try:
            group_key = self.group_keys[group_id]
            
            # Generate random IV for this message
            iv = secrets.token_bytes(16)  # 128-bit IV for AES
            
            # Create AES cipher
            cipher = Cipher(
                algorithms.AES(group_key.key_data),
                modes.CBC(iv),
                backend=self.backend
            )
            encryptor = cipher.encryptor()
            
            # Pad message to AES block size (16 bytes)
            message_bytes = message_content.encode('utf-8')
            padding_length = 16 - (len(message_bytes) % 16)
            padded_message = message_bytes + bytes([padding_length] * padding_length)
            
            # Encrypt the message
            encrypted_content = encryptor.update(padded_message) + encryptor.finalize()
            
            # Create group message object
            group_message = GroupMessage(
                sender=sender,
                group_id=group_id,
                encrypted_content=base64.b64encode(encrypted_content).decode(),
                key_id=group_key.key_id,
                iv=base64.b64encode(iv).decode()
            )
            
            print(f"DEBUG: Successfully encrypted group message. Message ID: {group_message.message_id}")
            return group_message
            
        except Exception as e:
            print(f"ERROR: Failed to encrypt group message: {e}")
            return None
    
    def decrypt_group_message(self, group_message: GroupMessage, member_fingerprint: str) -> Optional[str]:
        """
        Decrypt a group message using the member's copy of the group key
        
        Args:
            group_message: The encrypted group message
            member_fingerprint: PGP fingerprint of the member trying to decrypt
            
        Returns:
            str: The decrypted message content, or None if decryption failed
        """
        group_id = group_message.group_id
        
        # Check if we have the group key
        if group_id not in self.group_keys:
            print(f"ERROR: No group key found for group {group_id}")
            return None
        
        # Check if this member has access to the group key
        if (group_id not in self.member_keys or 
            member_fingerprint not in self.member_keys[group_id]):
            print(f"ERROR: Member {member_fingerprint[:16]}... does not have access to group {group_id}")
            return None
        
        try:
            group_key = self.group_keys[group_id]
            
            # Verify key ID matches
            if group_message.key_id != group_key.key_id:
                print(f"ERROR: Key ID mismatch. Message key: {group_message.key_id}, Group key: {group_key.key_id}")
                return None
            
            # Decode encrypted content and IV
            encrypted_content = base64.b64decode(group_message.encrypted_content)
            iv = base64.b64decode(group_message.iv)
            
            # Create AES cipher
            cipher = Cipher(
                algorithms.AES(group_key.key_data),
                modes.CBC(iv),
                backend=self.backend
            )
            decryptor = cipher.decryptor()
            
            # Decrypt the message
            padded_message = decryptor.update(encrypted_content) + decryptor.finalize()
            
            # Remove padding
            padding_length = padded_message[-1]
            message_bytes = padded_message[:-padding_length]
            
            # Convert to string
            message_content = message_bytes.decode('utf-8')
            
            print(f"DEBUG: Successfully decrypted group message from {group_message.sender}")
            return message_content
            
        except Exception as e:
            print(f"ERROR: Failed to decrypt group message: {e}")
            return None
    
    def get_encrypted_key_for_member(self, group_id: str, member_fingerprint: str) -> Optional[EncryptedGroupKey]:
        """
        Get the encrypted group key for a specific member
        
        Args:
            group_id: The group ID
            member_fingerprint: The member's PGP fingerprint
            
        Returns:
            EncryptedGroupKey: The encrypted key for this member, or None if not found
        """
        if (group_id in self.member_keys and 
            member_fingerprint in self.member_keys[group_id]):
            return self.member_keys[group_id][member_fingerprint]
        return None
    
    def load_group_key_from_encrypted(self, group_id: str, encrypted_key: EncryptedGroupKey, 
                                    member_fingerprint: str, passphrase: str = None) -> bool:
        """
        Load a group key by decrypting an encrypted group key with member's private key
        
        Args:
            group_id: The group ID
            encrypted_key: The encrypted group key
            member_fingerprint: The member's PGP fingerprint
            passphrase: The member's private key passphrase
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Decrypt the group key using member's private key
            decryption_result = self.pgp_handler.decrypt_message(
                encrypted_key.encrypted_key_data,
                passphrase=passphrase
            )
            
            if not decryption_result or 'decrypted_message' not in decryption_result:
                print(f"ERROR: Failed to decrypt group key for member {member_fingerprint[:16]}...")
                return False
            
            # Parse the decrypted key data
            key_data = json.loads(decryption_result['decrypted_message'])
            
            # Create group key object
            group_key = GroupKey(
                key_data=base64.b64decode(key_data['group_key']),
                key_id=key_data['key_id']
            )
            group_key.created_at = key_data.get('created_at', time.time())
            group_key.version = key_data.get('version', 1)
            
            # Store the group key
            self.group_keys[group_id] = group_key
            
            # Initialize member keys if needed
            if group_id not in self.member_keys:
                self.member_keys[group_id] = {}
            
            # Store the encrypted key for this member
            self.member_keys[group_id][member_fingerprint] = encrypted_key
            
            print(f"DEBUG: Successfully loaded group key for group {group_id}")
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to load group key: {e}")
            return False
    
    def rotate_group_key(self, group_id: str, member_fingerprints: List[str]) -> bool:
        """
        Generate a new group key and encrypt it for all current members
        This should be done when members are removed for forward secrecy
        
        Args:
            group_id: The group to rotate the key for
            member_fingerprints: Current list of member fingerprints
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print(f"DEBUG: Rotating group key for group {group_id}")
            
            # Create new group key
            new_group_key = self.create_group_key(group_id, member_fingerprints)
            
            print(f"DEBUG: Group key rotated successfully. New key ID: {new_group_key.key_id}")
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to rotate group key: {e}")
            return False
    
    def export_group_data(self, group_id: str) -> Optional[dict]:
        """
        Export group encryption data for storage or backup
        
        Args:
            group_id: The group to export
            
        Returns:
            dict: The group data, or None if group not found
        """
        if group_id not in self.group_keys:
            return None
        
        group_key = self.group_keys[group_id]
        member_keys = self.member_keys.get(group_id, {})
        
        return {
            'group_id': group_id,
            'group_key': group_key.to_dict(),
            'member_keys': {fp: key.to_dict() for fp, key in member_keys.items()},
            'exported_at': time.time()
        }
    
    def import_group_data(self, group_data: dict) -> bool:
        """
        Import group encryption data from storage or backup
        
        Args:
            group_data: The group data to import
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            group_id = group_data['group_id']
            
            # Import group key
            group_key = GroupKey.from_dict(group_data['group_key'])
            self.group_keys[group_id] = group_key
            
            # Import member keys
            self.member_keys[group_id] = {}
            for fp, key_data in group_data['member_keys'].items():
                encrypted_key = EncryptedGroupKey.from_dict(key_data)
                self.member_keys[group_id][fp] = encrypted_key
            
            print(f"DEBUG: Successfully imported group data for group {group_id}")
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to import group data: {e}")
            return False

