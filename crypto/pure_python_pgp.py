"""
Pure Python PGP Implementation
Replaces python-gnupg dependency with cryptography library for Windows compatibility
Enhanced with comprehensive data encryption for v2.1
"""

import os
import base64
import json
import hashlib
import secrets
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Import secure data management
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from security.data_encryption import SecureDataManager


class PurePythonPGPHandler:
    """Pure Python PGP implementation using cryptography library with secure data storage"""
    
    def __init__(self, gnupg_home: str, master_password: str = None):
        """
        Initialize PGP handler with secure data management
        
        Args:
            gnupg_home: Directory for storing keys and data
            master_password: Master password for data encryption
        """
        self.gnupg_home = gnupg_home
        self.keys_dir = os.path.join(gnupg_home, "keys")
        self.messages_dir = os.path.join(gnupg_home, "messages")
        
        # Initialize cryptography backend
        self.backend = default_backend()
        
        # Create directories
        os.makedirs(self.keys_dir, exist_ok=True)
        os.makedirs(self.messages_dir, exist_ok=True)
        
        # Initialize secure data manager
        self.data_manager = SecureDataManager(gnupg_home)
        if master_password:
            self.data_manager.initialize_encryption(master_password)
        
        # Key storage files
        self.public_keys_file = "public_keys.json"
        self.private_keys_file = "private_keys.json"
        self.message_history_file = "message_history.json"
        self.contacts_file = "contacts.json"
        
        # Initialize keys structure
        self.keys = {
            "public_keys": {},
            "private_keys": {}
        }
        
        # Load existing keys if available
        self._load_keys()
    
    def set_master_password(self, master_password: str):
        """Set master password for data encryption"""
        self.data_manager.initialize_encryption(master_password)
        # Reload keys with encryption
        self._load_keys()
    
    def _load_keys(self):
        """Load keys from storage"""
        try:
            if self.data_manager.encryption:
                # Load from encrypted storage
                public_keys_data = self.data_manager.load_data(self.public_keys_file, default={})
                private_keys_data = self.data_manager.load_data(self.private_keys_file, default={})
                
                self.keys = {
                    "public_keys": public_keys_data,
                    "private_keys": private_keys_data
                }
            else:
                # Load from legacy storage if no encryption
                legacy_data = self._load_keys_legacy("keys.json")
                self.keys = legacy_data if legacy_data else {
                    "public_keys": {},
                    "private_keys": {}
                }
        except Exception as e:
            print(f"Warning: Failed to load keys: {e}")
            self.keys = {
                "public_keys": {},
                "private_keys": {}
            }
    
    def _load_keys_data(self, filename: str) -> Dict:
        """Load keys data using secure data manager"""
        if not self.data_manager.encryption:
            # Fallback to legacy loading if encryption not initialized
            return self._load_keys_legacy(filename)
        
        return self.data_manager.load_data(filename, default={})
    
    def _save_keys_data(self, filename: str, data: Dict):
        """Save keys data using secure data manager"""
        if not self.data_manager.encryption:
            raise ValueError("Data encryption not initialized")
        
        self.data_manager.save_data(filename, data)
    
    def _load_keys_legacy(self, filename: str) -> Dict:
        """Legacy key loading for backward compatibility"""
        file_path = os.path.join(self.keys_dir, filename)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {"public_keys": {}, "private_keys": {}}
    
    def _save_keys(self):
        """Save keys to storage"""
        try:
            if self.data_manager.encryption:
                # Save to encrypted storage
                self.data_manager.save_data(self.public_keys_file, self.keys["public_keys"])
                self.data_manager.save_data(self.private_keys_file, self.keys["private_keys"])
            else:
                # Fallback to legacy storage
                keys_file = os.path.join(self.keys_dir, "keys.json")
                with open(keys_file, 'w') as f:
                    json.dump(self.keys, f, indent=2)
        except Exception as e:
            raise Exception(f"Failed to save keys: {e}")
    
    def _generate_fingerprint(self, public_key_pem: str) -> str:
        """Generate a fingerprint for a public key"""
        # Create a hash of the public key
        key_hash = hashlib.sha256(public_key_pem.encode()).hexdigest()
        # Format as PGP-style fingerprint
        return ' '.join([key_hash[i:i+4] for i in range(0, 40, 4)]).upper()
    
    def _generate_key_id(self, fingerprint: str) -> str:
        """Generate a key ID from fingerprint"""
        # Use last 16 characters of fingerprint (8 bytes)
        return fingerprint.replace(' ', '')[-16:]
    
    def _encrypt_private_key(self, private_key_pem: str, passphrase: str) -> str:
        """Encrypt a private key with a passphrase"""
        # Generate salt
        salt = secrets.token_bytes(16)
        
        # Derive key from passphrase
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=self.backend
        )
        key = kdf.derive(passphrase.encode())
        
        # Generate IV
        iv = secrets.token_bytes(16)
        
        # Encrypt private key
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=self.backend)
        encryptor = cipher.encryptor()
        
        # Pad the private key data
        padded_data = self._pad_data(private_key_pem.encode())
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        # Combine salt, iv, and encrypted data
        encrypted_key = base64.b64encode(salt + iv + encrypted_data).decode()
        return encrypted_key
    
    def _decrypt_private_key(self, encrypted_key: str, passphrase: str) -> str:
        """Decrypt a private key with a passphrase"""
        try:
            # Decode the encrypted data
            encrypted_data = base64.b64decode(encrypted_key.encode())
            
            # Extract salt, iv, and encrypted content
            salt = encrypted_data[:16]
            iv = encrypted_data[16:32]
            encrypted_content = encrypted_data[32:]
            
            # Derive key from passphrase
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=self.backend
            )
            key = kdf.derive(passphrase.encode())
            
            # Decrypt
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=self.backend)
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(encrypted_content) + decryptor.finalize()
            
            # Remove padding
            private_key_pem = self._unpad_data(decrypted_data).decode()
            return private_key_pem
            
        except Exception as e:
            raise Exception(f"Failed to decrypt private key: {e}")
    
    def _pad_data(self, data: bytes) -> bytes:
        """Add PKCS7 padding to data"""
        block_size = 16
        padding_length = block_size - (len(data) % block_size)
        padding = bytes([padding_length] * padding_length)
        return data + padding
    
    def _unpad_data(self, data: bytes) -> bytes:
        """Remove PKCS7 padding from data"""
        padding_length = data[-1]
        return data[:-padding_length]
    
    def _create_ascii_armor(self, data: str, armor_type: str) -> str:
        """Create ASCII armor format for PGP data"""
        header = f"-----BEGIN PGP {armor_type}-----"
        footer = f"-----END PGP {armor_type}-----"
        
        # Add line breaks every 64 characters
        lines = []
        for i in range(0, len(data), 64):
            lines.append(data[i:i+64])
        
        return f"{header}\n\n" + "\n".join(lines) + f"\n{footer}"
    
    def _parse_ascii_armor(self, armored_data: str) -> Tuple[str, str]:
        """Parse ASCII armor format and return type and data"""
        lines = armored_data.strip().split('\n')
        
        # Find header and footer
        header_line = None
        footer_line = None
        
        for i, line in enumerate(lines):
            if line.startswith("-----BEGIN PGP "):
                header_line = i
                armor_type = line.replace("-----BEGIN PGP ", "").replace("-----", "")
            elif line.startswith("-----END PGP "):
                footer_line = i
                break
        
        if header_line is None or footer_line is None:
            raise Exception("Invalid ASCII armor format")
        
        # Extract data between header and footer
        data_lines = []
        for i in range(header_line + 1, footer_line):
            line = lines[i].strip()
            if line:  # Skip empty lines
                data_lines.append(line)
        
        data = "".join(data_lines)
        return armor_type, data
    
    def generate_key(self, name: str, email: str, passphrase: str, key_length: int = 2048) -> Dict[str, Any]:
        """Generate a new RSA key pair"""
        try:
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_length,
                backend=self.backend
            )
            
            # Get public key
            public_key = private_key.public_key()
            
            # Serialize keys
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode()
            
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode()
            
            # Generate fingerprint and key ID
            fingerprint = self._generate_fingerprint(public_pem)
            key_id = self._generate_key_id(fingerprint)
            
            # Create key metadata
            timestamp = int(time.time())
            uid = f"{name} <{email}>"
            
            # Encrypt private key
            encrypted_private_key = self._encrypt_private_key(private_pem, passphrase)
            
            # Store public key
            self.keys["public_keys"][fingerprint] = {
                "fingerprint": fingerprint,
                "keyid": key_id,
                "uids": [uid],
                "length": str(key_length),
                "algo": "RSA",
                "created": timestamp,
                "expires": "",
                "trust": "ultimate",
                "public_key": public_pem
            }
            
            # Store private key
            self.keys["private_keys"][fingerprint] = {
                "fingerprint": fingerprint,
                "keyid": key_id,
                "uids": [uid],
                "length": str(key_length),
                "algo": "RSA",
                "created": timestamp,
                "expires": "",
                "trust": "ultimate",
                "private_key": encrypted_private_key
            }
            
            # Save keys
            self._save_keys()
            
            return {
                "success": True,
                "fingerprint": fingerprint,
                "key_id": key_id,
                "message": "Key pair generated successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_keys(self, secret: bool = False) -> List[Dict[str, Any]]:
        """List public or private keys"""
        key_store = self.keys["private_keys"] if secret else self.keys["public_keys"]
        
        keys = []
        for fingerprint, key_data in key_store.items():
            keys.append({
                "fingerprint": key_data["fingerprint"],
                "keyid": key_data["keyid"],
                "uids": key_data["uids"],
                "length": key_data["length"],
                "algo": key_data["algo"],
                "created": key_data["created"],
                "date": key_data["created"],  # Add date field for compatibility
                "expires": key_data["expires"],
                "trust": key_data["trust"]
            })
        
        return keys
    
    def export_public_key(self, fingerprint: str) -> Dict[str, Any]:
        """Export a public key in ASCII armor format"""
        try:
            if fingerprint not in self.keys["public_keys"]:
                return {"success": False, "error": "Public key not found"}
            
            key_data = self.keys["public_keys"][fingerprint]
            public_key_pem = key_data["public_key"]
            
            # Encode as base64 for ASCII armor
            encoded_key = base64.b64encode(public_key_pem.encode()).decode()
            armored_key = self._create_ascii_armor(encoded_key, "PUBLIC KEY BLOCK")
            
            return {
                "success": True,
                "public_key": armored_key
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def export_private_key(self, fingerprint: str, passphrase: str) -> Dict[str, Any]:
        """Export a private key in ASCII armor format"""
        try:
            if fingerprint not in self.keys["private_keys"]:
                return {"success": False, "error": "Private key not found"}
            
            key_data = self.keys["private_keys"][fingerprint]
            encrypted_private_key = key_data["private_key"]
            
            # Decrypt private key
            private_key_pem = self._decrypt_private_key(encrypted_private_key, passphrase)
            
            # Encode as base64 for ASCII armor
            encoded_key = base64.b64encode(private_key_pem.encode()).decode()
            armored_key = self._create_ascii_armor(encoded_key, "PRIVATE KEY BLOCK")
            
            return {
                "success": True,
                "private_key": armored_key
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def import_key(self, key_data: str) -> Dict[str, Any]:
        """Import a key from ASCII armor format"""
        try:
            # Parse ASCII armor
            armor_type, encoded_data = self._parse_ascii_armor(key_data)
            
            # Decode the key
            key_pem = base64.b64decode(encoded_data).decode()
            
            # Determine if it's a public or private key
            is_private = "PRIVATE KEY" in armor_type
            
            if is_private:
                # Load private key to validate
                private_key = serialization.load_pem_private_key(
                    key_pem.encode(),
                    password=None,
                    backend=self.backend
                )
                public_key = private_key.public_key()
                public_pem = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ).decode()
            else:
                # Load public key to validate
                public_key = serialization.load_pem_public_key(
                    key_pem.encode(),
                    backend=self.backend
                )
                public_pem = key_pem
            
            # Generate fingerprint and key ID
            fingerprint = self._generate_fingerprint(public_pem)
            key_id = self._generate_key_id(fingerprint)
            
            # Create key metadata
            timestamp = int(time.time())
            uid = "Imported Key"
            
            # Store public key
            self.keys["public_keys"][fingerprint] = {
                "fingerprint": fingerprint,
                "keyid": key_id,
                "uids": [uid],
                "length": "2048",  # Default, could be detected
                "algo": "RSA",
                "created": timestamp,
                "expires": "",
                "trust": "unknown",
                "public_key": public_pem
            }
            
            # Store private key if available
            if is_private:
                # For imported private keys, we'll store them unencrypted
                # In a real implementation, you'd want to re-encrypt with user's passphrase
                self.keys["private_keys"][fingerprint] = {
                    "fingerprint": fingerprint,
                    "keyid": key_id,
                    "uids": [uid],
                    "length": "2048",
                    "algo": "RSA",
                    "created": timestamp,
                    "expires": "",
                    "trust": "unknown",
                    "private_key": base64.b64encode(key_pem.encode()).decode()  # Store as base64
                }
            
            # Save keys
            self._save_keys()
            
            return {
                "success": True,
                "imported_count": 1,
                "fingerprint": fingerprint
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def encrypt_message(self, message: str, recipients: List[str]) -> Dict[str, Any]:
        """Encrypt a message for specified recipients"""
        try:
            if not recipients:
                return {"success": False, "error": "No recipients specified"}
            
            # Get recipient public keys
            recipient_keys = []
            for fingerprint in recipients:
                if fingerprint not in self.keys["public_keys"]:
                    return {"success": False, "error": f"Public key not found for {fingerprint}"}
                
                key_data = self.keys["public_keys"][fingerprint]
                public_key_pem = key_data["public_key"]
                
                # Load public key
                public_key = serialization.load_pem_public_key(
                    public_key_pem.encode(),
                    backend=self.backend
                )
                recipient_keys.append(public_key)
            
            # Generate a random symmetric key for the message
            symmetric_key = secrets.token_bytes(32)  # 256-bit key
            
            # Encrypt the message with the symmetric key
            iv = secrets.token_bytes(16)
            cipher = Cipher(algorithms.AES(symmetric_key), modes.CBC(iv), backend=self.backend)
            encryptor = cipher.encryptor()
            
            padded_message = self._pad_data(message.encode())
            encrypted_message = encryptor.update(padded_message) + encryptor.finalize()
            
            # Encrypt the symmetric key for each recipient
            encrypted_keys = []
            for public_key in recipient_keys:
                encrypted_key = public_key.encrypt(
                    symmetric_key,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                encrypted_keys.append(base64.b64encode(encrypted_key).decode())
            
            # Create the encrypted message structure
            message_data = {
                "version": "1.0",
                "encrypted_keys": encrypted_keys,
                "iv": base64.b64encode(iv).decode(),
                "encrypted_message": base64.b64encode(encrypted_message).decode()
            }
            
            # Encode as JSON and then base64
            json_data = json.dumps(message_data)
            encoded_data = base64.b64encode(json_data.encode()).decode()
            
            # Create ASCII armor
            armored_message = self._create_ascii_armor(encoded_data, "MESSAGE")
            
            return {
                "success": True,
                "encrypted_message": armored_message
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def decrypt_message(self, encrypted_message: str, passphrase: str) -> Dict[str, Any]:
        """Decrypt a message using private key - ENHANCED DEBUG VERSION"""
        try:
            print(f"DEBUG: Starting decryption with passphrase: {'<empty>' if not passphrase else '<provided>'}")
            
            # Parse ASCII armor
            armor_type, encoded_data = self._parse_ascii_armor(encrypted_message)
            print(f"DEBUG: Parsed armor type: {armor_type}")
            
            if "MESSAGE" not in armor_type:
                return {"success": False, "error": "Invalid message format"}
            
            # Decode the message data
            json_data = base64.b64decode(encoded_data).decode()
            message_data = json.loads(json_data)
            print(f"DEBUG: Message data keys: {list(message_data.keys())}")
            print(f"DEBUG: Number of encrypted keys: {len(message_data.get('encrypted_keys', []))}")
            
            # Try to decrypt with each private key
            decrypted_key = None
            print(f"DEBUG: Available private keys: {len(self.keys['private_keys'])}")
            
            for fingerprint, key_data in self.keys["private_keys"].items():
                print(f"DEBUG: Trying private key: {fingerprint}")
                try:
                    # Decrypt private key
                    if "private_key" in key_data and isinstance(key_data["private_key"], str):
                        # Check if it's encrypted or base64 encoded
                        if key_data["private_key"].startswith("-----"):
                            # It's a PEM key
                            print("DEBUG: Private key is in PEM format")
                            private_key_pem = key_data["private_key"]
                        else:
                            try:
                                # Try to decrypt as encrypted key
                                print("DEBUG: Attempting to decrypt private key with passphrase")
                                private_key_pem = self._decrypt_private_key(key_data["private_key"], passphrase)
                                print("DEBUG: Private key decryption successful")
                            except Exception as e:
                                print(f"DEBUG: Private key decryption failed: {e}")
                                # Try to decode as base64 (for imported keys)
                                try:
                                    print("DEBUG: Trying base64 decode of private key")
                                    decoded_data = base64.b64decode(key_data["private_key"])
                                    # Try to decode as UTF-8 (for PEM keys stored as base64)
                                    try:
                                        private_key_pem = decoded_data.decode('utf-8')
                                        print("DEBUG: Base64 decode successful (UTF-8)")
                                    except UnicodeDecodeError:
                                        # If UTF-8 decode fails, it might be binary encrypted data
                                        print("DEBUG: Base64 decoded to binary data, not PEM")
                                        continue
                                except Exception as e2:
                                    print(f"DEBUG: Base64 decode failed: {e2}")
                                    continue
                    else:
                        print("DEBUG: No private_key field or invalid format")
                        continue
                    
                    # Load private key
                    print("DEBUG: Loading private key from PEM")
                    private_key = serialization.load_pem_private_key(
                        private_key_pem.encode(),
                        password=None,
                        backend=self.backend
                    )
                    print("DEBUG: Private key loaded successfully")
                    
                    # Try to decrypt each encrypted key
                    for i, encrypted_key_b64 in enumerate(message_data["encrypted_keys"]):
                        print(f"DEBUG: Trying encrypted key {i+1}/{len(message_data['encrypted_keys'])}")
                        try:
                            encrypted_key = base64.b64decode(encrypted_key_b64)
                            symmetric_key = private_key.decrypt(
                                encrypted_key,
                                padding.OAEP(
                                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                    algorithm=hashes.SHA256(),
                                    label=None
                                )
                            )
                            decrypted_key = symmetric_key
                            print(f"DEBUG: Successfully decrypted symmetric key with encrypted key {i+1}")
                            break
                        except Exception as e:
                            print(f"DEBUG: Failed to decrypt with encrypted key {i+1}: {e}")
                            continue
                    
                    if decrypted_key:
                        print("DEBUG: Found working decryption key")
                        break
                        
                except Exception as e:
                    print(f"DEBUG: Error processing private key {fingerprint}: {e}")
                    continue
            
            if not decrypted_key:
                print("DEBUG: No private key could decrypt the message")
                # Provide more specific error information
                available_keys = len(self.keys["private_keys"])
                if available_keys == 0:
                    return {"success": False, "error": "No private keys available for decryption"}
                else:
                    return {"success": False, "error": f"Could not decrypt message with any of the {available_keys} available private keys. This may be due to:\n1. Message was encrypted for a different key\n2. Incorrect passphrase for private key\n3. Corrupted key data or message"}
            
            # Decrypt the message
            print("DEBUG: Decrypting message content with symmetric key")
            iv = base64.b64decode(message_data["iv"])
            encrypted_content = base64.b64decode(message_data["encrypted_message"])
            
            cipher = Cipher(algorithms.AES(decrypted_key), modes.CBC(iv), backend=self.backend)
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(encrypted_content) + decryptor.finalize()
            
            # Remove padding
            message = self._unpad_data(decrypted_data).decode()
            print(f"DEBUG: Successfully decrypted message: {message[:50]}...")
            
            return {
                "success": True,
                "decrypted_message": message
            }
            
        except Exception as e:
            print(f"DEBUG: Exception during decryption: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    def delete_key(self, fingerprint: str, secret: bool = False) -> Dict[str, Any]:
        """Delete a key from the keyring"""
        try:
            key_store = "private_keys" if secret else "public_keys"
            
            if fingerprint not in self.keys[key_store]:
                return {"success": False, "error": "Key not found"}
            
            # Delete the key
            del self.keys[key_store][fingerprint]
            
            # Save keys
            self._save_keys()
            
            return {"success": True, "message": "Key deleted successfully"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def cleanup(self):
        """Cleanup resources"""
        # Save any pending changes
        try:
            self._save_keys()
        except:
            pass

