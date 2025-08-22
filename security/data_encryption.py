"""
Data Encryption Module
Provides comprehensive encryption for all application data
"""

import os
import json
import base64
import secrets
import hashlib
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class DataEncryption:
    """Handles encryption and decryption of all application data"""
    
    def __init__(self, data_dir: str, master_password: str = None):
        """
        Initialize data encryption
        
        Args:
            data_dir: Directory where encrypted data is stored
            master_password: Master password for encryption (if None, will prompt)
        """
        self.data_dir = data_dir
        self.master_password = master_password
        self.encryption_key = None
        self.salt_file = os.path.join(data_dir, ".encryption_salt")
        
        # Ensure directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize encryption key
        if master_password:
            self.encryption_key = self._derive_key(master_password)
    
    def set_master_password(self, password: str):
        """Set the master password and derive encryption key"""
        self.master_password = password
        self.encryption_key = self._derive_key(password)
    
    def _derive_key(self, password: str) -> bytes:
        """Derive encryption key from master password"""
        # Get or create salt
        salt = self._get_or_create_salt()
        
        # Derive key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = kdf.derive(password.encode())
        return base64.urlsafe_b64encode(key)
    
    def _get_or_create_salt(self) -> bytes:
        """Get existing salt or create new one"""
        if os.path.exists(self.salt_file):
            try:
                with open(self.salt_file, 'rb') as f:
                    return f.read()
            except:
                pass
        
        # Create new salt
        salt = secrets.token_bytes(32)
        try:
            with open(self.salt_file, 'wb') as f:
                f.write(salt)
        except:
            pass
        
        return salt
    
    def encrypt_data(self, data: Any) -> str:
        """
        Encrypt any data object
        
        Args:
            data: Data to encrypt (will be JSON serialized)
            
        Returns:
            Base64 encoded encrypted data
        """
        if not self.encryption_key:
            raise ValueError("Encryption key not set. Call set_master_password() first.")
        
        # Serialize data to JSON
        json_data = json.dumps(data, default=str)
        
        # Encrypt data
        fernet = Fernet(self.encryption_key)
        encrypted_data = fernet.encrypt(json_data.encode())
        
        # Return base64 encoded
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt_data(self, encrypted_data: str) -> Any:
        """
        Decrypt data
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            
        Returns:
            Decrypted data object
        """
        if not self.encryption_key:
            raise ValueError("Encryption key not set. Call set_master_password() first.")
        
        try:
            # Decode from base64
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            
            # Decrypt data
            fernet = Fernet(self.encryption_key)
            decrypted_bytes = fernet.decrypt(encrypted_bytes)
            
            # Parse JSON
            json_data = decrypted_bytes.decode()
            return json.loads(json_data)
            
        except Exception as e:
            raise ValueError(f"Failed to decrypt data: {str(e)}")
    
    def encrypt_file(self, file_path: str, data: Any):
        """
        Encrypt data and save to file
        
        Args:
            file_path: Path to save encrypted file
            data: Data to encrypt and save
        """
        encrypted_data = self.encrypt_data(data)
        
        # Add encryption header
        file_data = {
            'version': '2.1',
            'encrypted': True,
            'data': encrypted_data
        }
        
        with open(file_path, 'w') as f:
            json.dump(file_data, f)
    
    def decrypt_file(self, file_path: str) -> Any:
        """
        Load and decrypt data from file
        
        Args:
            file_path: Path to encrypted file
            
        Returns:
            Decrypted data
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r') as f:
            file_data = json.load(f)
        
        # Check if file is encrypted
        if not file_data.get('encrypted', False):
            # Handle legacy unencrypted files
            return file_data.get('data', file_data)
        
        # Decrypt the data
        encrypted_data = file_data['data']
        return self.decrypt_data(encrypted_data)
    
    def is_file_encrypted(self, file_path: str) -> bool:
        """Check if a file is encrypted"""
        if not os.path.exists(file_path):
            return False
        
        try:
            with open(file_path, 'r') as f:
                file_data = json.load(f)
            return file_data.get('encrypted', False)
        except:
            return False
    
    def migrate_unencrypted_file(self, file_path: str):
        """Migrate an unencrypted file to encrypted format"""
        if not os.path.exists(file_path):
            return
        
        try:
            # Read existing data
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Check if already encrypted
            if data.get('encrypted', False):
                return
            
            # Encrypt and save
            self.encrypt_file(file_path, data)
            
        except Exception as e:
            print(f"Warning: Failed to migrate file {file_path}: {e}")
    
    def secure_delete_file(self, file_path: str):
        """Securely delete a file by overwriting it multiple times"""
        if not os.path.exists(file_path):
            return
        
        try:
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Overwrite file multiple times
            with open(file_path, 'r+b') as f:
                for _ in range(3):  # 3 passes
                    f.seek(0)
                    f.write(secrets.token_bytes(file_size))
                    f.flush()
                    os.fsync(f.fileno())
            
            # Remove the file
            os.remove(file_path)
            
        except Exception as e:
            print(f"Warning: Failed to securely delete {file_path}: {e}")
    
    def encrypt_directory(self, directory: str):
        """Encrypt all JSON files in a directory"""
        if not os.path.exists(directory):
            return
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.json') and not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    self.migrate_unencrypted_file(file_path)
    
    def verify_encryption_key(self) -> bool:
        """Verify that the current encryption key is correct"""
        if not self.encryption_key:
            return False
        
        try:
            # Try to encrypt and decrypt test data
            test_data = {"test": "verification", "timestamp": 12345}
            encrypted = self.encrypt_data(test_data)
            decrypted = self.decrypt_data(encrypted)
            
            return decrypted == test_data
            
        except:
            return False
    
    def change_master_password(self, old_password: str, new_password: str):
        """
        Change the master password and re-encrypt all data
        
        Args:
            old_password: Current master password
            new_password: New master password
        """
        # Verify old password
        old_key = self._derive_key(old_password)
        old_encryption = DataEncryption(self.data_dir)
        old_encryption.encryption_key = old_key
        
        if not old_encryption.verify_encryption_key():
            raise ValueError("Old password is incorrect")
        
        # Collect all encrypted files
        encrypted_files = []
        for root, dirs, files in os.walk(self.data_dir):
            for file in files:
                if file.endswith('.json') and not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    if self.is_file_encrypted(file_path):
                        encrypted_files.append(file_path)
        
        # Decrypt all data with old password
        decrypted_data = {}
        for file_path in encrypted_files:
            try:
                decrypted_data[file_path] = old_encryption.decrypt_file(file_path)
            except Exception as e:
                print(f"Warning: Failed to decrypt {file_path}: {e}")
        
        # Set new password and re-encrypt all data
        self.set_master_password(new_password)
        
        for file_path, data in decrypted_data.items():
            try:
                self.encrypt_file(file_path, data)
            except Exception as e:
                print(f"Warning: Failed to re-encrypt {file_path}: {e}")


class SecureDataManager:
    """High-level interface for secure data management"""
    
    def __init__(self, data_dir: str):
        """Initialize secure data manager"""
        self.data_dir = data_dir
        self.encryption = None
        
        # Ensure directory exists
        os.makedirs(data_dir, exist_ok=True)
    
    def initialize_encryption(self, master_password: str):
        """Initialize encryption with master password"""
        self.encryption = DataEncryption(self.data_dir, master_password)
        
        # Migrate any existing unencrypted files
        self.encryption.encrypt_directory(self.data_dir)
    
    def save_data(self, filename: str, data: Any):
        """Save data securely"""
        if not self.encryption:
            raise ValueError("Encryption not initialized")
        
        file_path = os.path.join(self.data_dir, filename)
        self.encryption.encrypt_file(file_path, data)
    
    def load_data(self, filename: str, default=None) -> Any:
        """Load data securely"""
        if not self.encryption:
            raise ValueError("Encryption not initialized")
        
        file_path = os.path.join(self.data_dir, filename)
        
        try:
            return self.encryption.decrypt_file(file_path)
        except FileNotFoundError:
            return default
        except Exception as e:
            print(f"Warning: Failed to load {filename}: {e}")
            return default
    
    def delete_data(self, filename: str):
        """Securely delete data file"""
        if not self.encryption:
            raise ValueError("Encryption not initialized")
        
        file_path = os.path.join(self.data_dir, filename)
        self.encryption.secure_delete_file(file_path)
    
    def file_exists(self, filename: str) -> bool:
        """Check if data file exists"""
        file_path = os.path.join(self.data_dir, filename)
        return os.path.exists(file_path)

