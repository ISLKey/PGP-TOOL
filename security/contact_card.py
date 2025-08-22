"""
Contact Card System for PGP Tool
Encrypted contact sharing with name, IRC nickname, and public PGP key
"""

import json
import base64
import time
from typing import Dict, Any, Optional, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os


class ContactCard:
    """Represents a contact card with encrypted data"""
    
    def __init__(self, name: str, irc_nickname: str, public_key: str, 
                 email: str = "", notes: str = ""):
        self.name = name
        self.irc_nickname = irc_nickname
        self.public_key = public_key
        self.email = email
        self.notes = notes
        self.created_date = time.strftime("%Y-%m-%d %H:%M:%S")
        self.version = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert contact card to dictionary"""
        return {
            "name": self.name,
            "irc_nickname": self.irc_nickname,
            "public_key": self.public_key,
            "email": self.email,
            "notes": self.notes,
            "created_date": self.created_date,
            "version": self.version,
            "card_type": "PGP_TOOL_CONTACT_CARD"
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContactCard':
        """Create contact card from dictionary"""
        card = cls(
            name=data.get("name", ""),
            irc_nickname=data.get("irc_nickname", ""),
            public_key=data.get("public_key", ""),
            email=data.get("email", ""),
            notes=data.get("notes", "")
        )
        card.created_date = data.get("created_date", card.created_date)
        card.version = data.get("version", "1.0")
        return card


class ContactCardManager:
    """Manages contact card encryption, decryption, and file operations"""
    
    def __init__(self):
        self.card_extension = ".pgpcard"
        self.card_header = "-----BEGIN PGP TOOL CONTACT CARD-----"
        self.card_footer = "-----END PGP TOOL CONTACT CARD-----"
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def encrypt_contact_card(self, contact_card: ContactCard, password: str) -> str:
        """Encrypt contact card with password"""
        try:
            # Generate salt
            salt = os.urandom(16)
            
            # Derive key
            key = self._derive_key(password, salt)
            fernet = Fernet(key)
            
            # Prepare data
            card_data = contact_card.to_dict()
            json_data = json.dumps(card_data, indent=2)
            
            # Encrypt
            encrypted_data = fernet.encrypt(json_data.encode())
            
            # Combine salt and encrypted data
            combined_data = salt + encrypted_data
            
            # Encode to base64
            encoded_data = base64.b64encode(combined_data).decode()
            
            # Format as contact card
            formatted_card = f"{self.card_header}\n"
            formatted_card += f"Version: {contact_card.version}\n"
            formatted_card += f"Created: {contact_card.created_date}\n"
            formatted_card += f"Contact: {contact_card.name}\n"
            formatted_card += "\n"
            
            # Add data in chunks for readability
            chunk_size = 64
            for i in range(0, len(encoded_data), chunk_size):
                formatted_card += encoded_data[i:i+chunk_size] + "\n"
            
            formatted_card += f"{self.card_footer}\n"
            
            return formatted_card
            
        except Exception as e:
            raise Exception(f"Failed to encrypt contact card: {str(e)}")
    
    def decrypt_contact_card(self, encrypted_card: str, password: str) -> ContactCard:
        """Decrypt contact card with password"""
        try:
            # Extract data between headers
            lines = encrypted_card.strip().split('\n')
            start_idx = -1
            end_idx = -1
            
            for i, line in enumerate(lines):
                if self.card_header in line:
                    start_idx = i + 1
                elif self.card_footer in line:
                    end_idx = i
                    break
            
            if start_idx == -1 or end_idx == -1:
                raise Exception("Invalid contact card format")
            
            # Skip metadata lines and get data
            data_lines = []
            for i in range(start_idx, end_idx):
                line = lines[i].strip()
                if line and not line.startswith(('Version:', 'Created:', 'Contact:')):
                    data_lines.append(line)
            
            # Combine data lines
            encoded_data = ''.join(data_lines)
            
            # Decode from base64
            combined_data = base64.b64decode(encoded_data)
            
            # Extract salt and encrypted data
            salt = combined_data[:16]
            encrypted_data = combined_data[16:]
            
            # Derive key
            key = self._derive_key(password, salt)
            fernet = Fernet(key)
            
            # Decrypt
            decrypted_data = fernet.decrypt(encrypted_data)
            json_data = decrypted_data.decode()
            
            # Parse JSON
            card_data = json.loads(json_data)
            
            # Validate card type
            if card_data.get("card_type") != "PGP_TOOL_CONTACT_CARD":
                raise Exception("Invalid contact card type")
            
            # Create contact card
            return ContactCard.from_dict(card_data)
            
        except Exception as e:
            raise Exception(f"Failed to decrypt contact card: {str(e)}")
    
    def export_contact_card(self, contact_card: ContactCard, file_path: str, password: str = None) -> bool:
        """Export contact card to file with optional password protection"""
        try:
            if password:
                # Export as encrypted contact card
                encrypted_card = self.encrypt_contact_card(contact_card, password)
                content = encrypted_card
            else:
                # Export as unencrypted JSON
                card_data = contact_card.to_dict()
                card_data["encrypted"] = False
                content = json.dumps(card_data, indent=2)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            raise Exception(f"Failed to export contact card: {str(e)}")
    
    def import_contact_card(self, file_path: str, password: str = None) -> ContactCard:
        """Import contact card from file (encrypted or unencrypted)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to parse as JSON first (unencrypted)
            try:
                data = json.loads(content)
                if isinstance(data, dict) and data.get("encrypted") == False:
                    # Unencrypted contact card
                    return ContactCard.from_dict(data)
            except json.JSONDecodeError:
                pass
            
            # Must be encrypted, require password
            if not password:
                raise Exception("This contact card is encrypted and requires a password")
            
            return self.decrypt_contact_card(content, password)
            
        except Exception as e:
            raise Exception(f"Failed to import contact card: {str(e)}")
    
    def validate_contact_card_file(self, file_path: str) -> Tuple[bool, str]:
        """Validate if file is a contact card (encrypted or unencrypted)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for unencrypted JSON format first
            try:
                data = json.loads(content)
                if isinstance(data, dict) and data.get("card_type") == "PGP_TOOL_CONTACT_CARD":
                    # Valid unencrypted contact card
                    contact_name = data.get('name', 'Unknown')
                    created_date = data.get('created_date', 'Unknown')
                    version = data.get('version', 'Unknown')
                    encryption_status = "Unencrypted" if data.get("encrypted") == False else "Unknown format"
                    
                    info = f"Contact Card: {contact_name}"
                    info += f"\nCreated: {created_date}"
                    info += f"\nVersion: {version}"
                    info += f"\nFormat: {encryption_status}"
                    
                    return True, info
            except json.JSONDecodeError:
                pass
            
            # Check for encrypted format
            if self.card_header in content and self.card_footer in content:
                # Extract metadata from encrypted format
                lines = content.strip().split('\n')
                metadata = {}
                
                for line in lines:
                    if line.startswith('Version:'):
                        metadata['version'] = line.split(':', 1)[1].strip()
                    elif line.startswith('Created:'):
                        metadata['created'] = line.split(':', 1)[1].strip()
                    elif line.startswith('Contact:'):
                        metadata['contact'] = line.split(':', 1)[1].strip()
                
                info = f"Contact Card: {metadata.get('contact', 'Unknown')}"
                if metadata.get('created'):
                    info += f"\nCreated: {metadata['created']}"
                if metadata.get('version'):
                    info += f"\nVersion: {metadata['version']}"
                info += f"\nFormat: Encrypted"
                
                return True, info
            
            # Neither format matched
            return False, "Not a valid PGP Tool contact card file"
            
        except Exception as e:
            return False, f"Error reading file: {str(e)}"
    
    def create_contact_card_from_key_data(self, name: str, irc_nickname: str, 
                                        key_data: str, email: str = "", 
                                        notes: str = "") -> ContactCard:
        """Create contact card from key data"""
        return ContactCard(
            name=name,
            irc_nickname=irc_nickname,
            public_key=key_data,
            email=email,
            notes=notes
        )
    
    def extract_key_info(self, contact_card: ContactCard) -> Dict[str, str]:
        """Extract key information from contact card"""
        try:
            # Basic key info extraction
            key_lines = contact_card.public_key.strip().split('\n')
            
            info = {
                'name': contact_card.name,
                'irc_nickname': contact_card.irc_nickname,
                'email': contact_card.email,
                'notes': contact_card.notes,
                'created_date': contact_card.created_date,
                'key_type': 'Unknown',
                'key_size': 'Unknown'
            }
            
            # Try to extract key type and size from key data
            for line in key_lines:
                if 'RSA' in line.upper():
                    info['key_type'] = 'RSA'
                    # Try to extract key size
                    import re
                    size_match = re.search(r'(\d{4})', line)
                    if size_match:
                        info['key_size'] = size_match.group(1) + ' bits'
            
            return info
            
        except Exception:
            return {
                'name': contact_card.name,
                'irc_nickname': contact_card.irc_nickname,
                'email': contact_card.email,
                'notes': contact_card.notes,
                'created_date': contact_card.created_date,
                'key_type': 'Unknown',
                'key_size': 'Unknown'
            }

