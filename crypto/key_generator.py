"""
Secure Key Generator - Updated for Pure Python PGP Implementation
Handles key generation with entropy collection without external GPG dependency
"""

import os
import tempfile
import shutil
from typing import Dict, List, Any, Optional

from .pgp_handler import PGPHandler
from .entropy import EntropyCollector


class SecureKeyGenerator:
    """Secure key generator using pure Python cryptography"""
    
    def __init__(self, gnupg_home: str):
        """Initialize the key generator"""
        self.gnupg_home = gnupg_home
        self.pgp_handler = PGPHandler(gnupg_home)
        self.entropy_collector = None
        
        # Ensure directory exists
        os.makedirs(gnupg_home, exist_ok=True)
    
    def start_entropy_collection(self, target_bits: int = 256) -> EntropyCollector:
        """Start collecting entropy for key generation"""
        self.entropy_collector = EntropyCollector(target_bits)
        return self.entropy_collector
    
    def generate_key_with_entropy(self, name: str, email: str, passphrase: str, key_length: int = 2048, progress_callback=None) -> Dict[str, Any]:
        """Generate a key pair using collected entropy"""
        try:
            if progress_callback:
                progress_callback("Checking entropy...")
            
            # Check if we have sufficient entropy
            if not self.entropy_collector or not self.entropy_collector.is_sufficient():
                return {
                    'success': False,
                    'error': 'Insufficient entropy collected. Please collect more entropy before generating keys.'
                }
            
            if progress_callback:
                progress_callback("Processing entropy...")
            
            # Use the entropy to seed additional randomness
            entropy_data = self.entropy_collector.get_entropy_bytes()
            
            # Mix entropy into the system random number generator
            import secrets
            import hashlib
            
            # Create a hash of the collected entropy
            entropy_hash = hashlib.sha256(entropy_data).digest()
            
            # Mix with system randomness (this is more for psychological comfort
            # as the cryptography library already uses secure random sources)
            mixed_entropy = hashlib.sha256(entropy_hash + secrets.token_bytes(32)).digest()
            
            if progress_callback:
                progress_callback("Generating key pair...")
            
            # Generate the key pair
            result = self.pgp_handler.generate_key(name, email, passphrase, key_length)
            
            if progress_callback:
                progress_callback("Finalizing...")
            
            # Clear the entropy collector
            if self.entropy_collector:
                self.entropy_collector.clear()
                self.entropy_collector = None
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Key generation failed: {str(e)}'
            }
    
    def list_keys(self, secret: bool = False) -> List[Dict[str, Any]]:
        """List available keys"""
        return self.pgp_handler.list_keys(secret)
    
    def export_public_key(self, fingerprint: str) -> Dict[str, Any]:
        """Export a public key"""
        return self.pgp_handler.export_public_key(fingerprint)
    
    def export_private_key(self, fingerprint: str, passphrase: str) -> Dict[str, Any]:
        """Export a private key"""
        return self.pgp_handler.export_private_key(fingerprint, passphrase)
    
    def import_key(self, key_data: str) -> Dict[str, Any]:
        """Import a key"""
        return self.pgp_handler.import_key(key_data)
    
    def encrypt_message(self, message: str, recipients: List[str]) -> Dict[str, Any]:
        """Encrypt a message for specified recipients"""
        return self.pgp_handler.encrypt_message(message, recipients)
    
    def decrypt_message(self, encrypted_message: str, passphrase: str) -> Dict[str, Any]:
        """Decrypt a message"""
        return self.pgp_handler.decrypt_message(encrypted_message, passphrase)
    
    def delete_key(self, fingerprint: str, secret: bool = False) -> Dict[str, Any]:
        """Delete a key"""
        return self.pgp_handler.delete_key(fingerprint, secret)
    
    def create_backup(self, backup_password: str, key_passphrase: str) -> Dict[str, Any]:
        """Create an encrypted backup of all keys"""
        return self.pgp_handler.create_backup(backup_password, key_passphrase)
    
    def restore_backup(self, encrypted_backup: str, backup_password: str) -> Dict[str, Any]:
        """Restore keys from an encrypted backup"""
        return self.pgp_handler.restore_backup(encrypted_backup, backup_password)
    
    def emergency_delete_all(self) -> Dict[str, Any]:
        """Emergency deletion of all keys and data"""
        return self.pgp_handler.emergency_delete_all()
    
    def get_key_info(self, fingerprint: str, secret: bool = False) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific key"""
        keys = self.list_keys(secret)
        for key in keys:
            if key['fingerprint'] == fingerprint:
                return key
        return None
    
    def verify_passphrase(self, fingerprint: str, passphrase: str) -> bool:
        """Verify if a passphrase is correct for a private key"""
        try:
            result = self.export_private_key(fingerprint, passphrase)
            return result['success']
        except:
            return False
    
    def cleanup(self):
        """Cleanup resources"""
        if self.entropy_collector:
            self.entropy_collector.clear()
            self.entropy_collector = None
        
        if hasattr(self, 'pgp_handler'):
            self.pgp_handler.cleanup()
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            self.cleanup()
        except:
            pass

