"""
PGP Handler - Updated to use Pure Python implementation
Provides a compatibility layer that works without external GPG dependency
"""

import os
import json
import shutil
from typing import Dict, List, Any, Optional
from .pure_python_pgp import PurePythonPGPHandler


class PGPHandler:
    """
    PGP Handler that uses pure Python cryptography instead of external GPG
    Maintains the same API as the original for compatibility
    """
    
    def __init__(self, gnupg_home: str):
        """Initialize the PGP handler with pure Python implementation"""
        self.gnupg_home = gnupg_home
        self.handler = PurePythonPGPHandler(gnupg_home)
        self._master_password = None  # Store master password for key decryption
        
        # Ensure directory exists
        os.makedirs(gnupg_home, exist_ok=True)
    
    def set_master_password(self, password: str):
        """Set the master password for key decryption"""
        self._master_password = password
        
    def get_master_password(self) -> Optional[str]:
        """Get the stored master password"""
        return self._master_password
    
    def generate_key(self, name: str, email: str, passphrase: str, key_length: int = 2048) -> Dict[str, Any]:
        """Generate a new key pair"""
        return self.handler.generate_key(name, email, passphrase, key_length)
    
    def list_keys(self, secret: bool = False) -> List[Dict[str, Any]]:
        """List public or private keys"""
        return self.handler.list_keys(secret)
    
    def export_public_key(self, fingerprint: str) -> Dict[str, Any]:
        """Export a public key"""
        return self.handler.export_public_key(fingerprint)
    
    def export_private_key(self, fingerprint: str, passphrase: str) -> Dict[str, Any]:
        """Export a private key"""
        return self.handler.export_private_key(fingerprint, passphrase)
    
    def import_key(self, key_data: str) -> Dict[str, Any]:
        """Import a key"""
        return self.handler.import_key(key_data)
    
    def encrypt_message(self, message: str, recipients: List[str]) -> Dict[str, Any]:
        """Encrypt a message for specified recipients"""
        return self.handler.encrypt_message(message, recipients)
    
    def decrypt_message(self, encrypted_message: str, passphrase: str) -> Dict[str, Any]:
        """Decrypt a message"""
        return self.handler.decrypt_message(encrypted_message, passphrase)
    
    def delete_key(self, fingerprint: str, secret: bool = False) -> Dict[str, Any]:
        """Delete a key"""
        return self.handler.delete_key(fingerprint, secret)
    
    def create_backup(self, backup_password: str, key_passphrase: str) -> Dict[str, Any]:
        """Create an encrypted backup of all keys"""
        try:
            # Get all keys
            public_keys = self.list_keys(secret=False)
            private_keys = self.list_keys(secret=True)
            
            backup_data = {
                "version": "1.0",
                "created": int(__import__('time').time()),
                "public_keys": [],
                "private_keys": []
            }
            
            # Export all public keys
            for key in public_keys:
                export_result = self.export_public_key(key['fingerprint'])
                if export_result['success']:
                    backup_data['public_keys'].append({
                        'fingerprint': key['fingerprint'],
                        'key_data': export_result['public_key'],
                        'metadata': key
                    })
            
            # Export all private keys
            for key in private_keys:
                export_result = self.export_private_key(key['fingerprint'], key_passphrase)
                if export_result['success']:
                    backup_data['private_keys'].append({
                        'fingerprint': key['fingerprint'],
                        'key_data': export_result['private_key'],
                        'metadata': key
                    })
            
            # Encrypt the backup data
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            import base64
            import secrets
            
            # Generate salt
            salt = secrets.token_bytes(16)
            
            # Derive key from backup password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(backup_password.encode()))
            
            # Encrypt backup data
            f = Fernet(key)
            backup_json = json.dumps(backup_data)
            encrypted_backup = f.encrypt(backup_json.encode())
            
            # Combine salt and encrypted data
            final_backup = base64.b64encode(salt + encrypted_backup).decode()
            
            return {
                'success': True,
                'encrypted_backup': final_backup,
                'message': f'Backup created with {len(backup_data["public_keys"])} public keys and {len(backup_data["private_keys"])} private keys'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def restore_backup(self, encrypted_backup: str, backup_password: str) -> Dict[str, Any]:
        """Restore keys from an encrypted backup"""
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            import base64
            
            # Decode the backup
            backup_data = base64.b64decode(encrypted_backup.encode())
            
            # Extract salt and encrypted content
            salt = backup_data[:16]
            encrypted_content = backup_data[16:]
            
            # Derive key from backup password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(backup_password.encode()))
            
            # Decrypt backup data
            f = Fernet(key)
            decrypted_data = f.decrypt(encrypted_content)
            backup_json = json.loads(decrypted_data.decode())
            
            # Import keys
            imported_public = 0
            imported_private = 0
            
            # Import public keys
            for key_info in backup_json.get('public_keys', []):
                result = self.import_key(key_info['key_data'])
                if result['success']:
                    imported_public += 1
            
            # Import private keys
            for key_info in backup_json.get('private_keys', []):
                result = self.import_key(key_info['key_data'])
                if result['success']:
                    imported_private += 1
            
            return {
                'success': True,
                'imported_public': imported_public,
                'imported_private': imported_private,
                'message': f'Restored {imported_public} public keys and {imported_private} private keys'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def emergency_delete_all(self) -> Dict[str, Any]:
        """Emergency deletion of all keys and data"""
        try:
            # Clear the keys data
            self.handler.keys = {"public_keys": {}, "private_keys": {}}
            
            # Save empty keys
            self.handler._save_keys()
            
            # Try to securely delete the gnupg directory
            if os.path.exists(self.gnupg_home):
                # Multiple pass deletion for security
                for root, dirs, files in os.walk(self.gnupg_home):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            # Overwrite file multiple times
                            file_size = os.path.getsize(file_path)
                            with open(file_path, 'r+b') as f:
                                for _ in range(3):  # 3 passes
                                    f.seek(0)
                                    f.write(secrets.token_bytes(file_size))
                                    f.flush()
                                    os.fsync(f.fileno())
                        except:
                            pass
                
                # Remove the directory
                shutil.rmtree(self.gnupg_home, ignore_errors=True)
            
            return {
                'success': True,
                'message': 'All keys and data have been securely deleted'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def cleanup(self):
        """Cleanup resources"""
        self.handler.cleanup()

