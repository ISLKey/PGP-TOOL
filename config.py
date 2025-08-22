"""
Configuration settings for PGP Encryption Tool
"""

import os
import tempfile

# Application Information
APP_NAME = "PGP Tool"
APP_VERSION = "4.2.5"
APP_AUTHOR = "Jamie Johnson (TriggerHappyMe)"
APP_DESCRIPTION = "Professional PGP Encryption & Secure Communication Platform"

# GUI Settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 750  # Increased from 600 for better button spacing
WINDOW_MIN_WIDTH = 600
WINDOW_MIN_HEIGHT = 500  # Increased minimum height too

# File Paths
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(APP_DIR, "data_storage")
TEMP_DIR = tempfile.gettempdir()

# Database Settings
DB_NAME = "pgp_tool.db"
DB_PATH = os.path.join(DATA_DIR, DB_NAME)

# Security Settings
KEY_SIZE_DEFAULT = 2048
KEY_SIZE_OPTIONS = [2048, 3072, 4096]
ENTROPY_THRESHOLD = 256  # Minimum entropy bits for key generation

# Enhanced Security Settings for v2.1
MAX_LOGIN_ATTEMPTS = 10  # Maximum failed login attempts before data wipe
DATA_ENCRYPTION_ENABLED = True  # Enable comprehensive data encryption
LOGIN_REQUIRED = True  # Require password to access application

# Backup Settings
BACKUP_EXTENSION = ".pgpbackup"
BACKUP_ENCRYPTION_ALGORITHM = "AES256"

# GUI Colors and Styling
COLORS = {
    'primary': '#2E3440',
    'secondary': '#3B4252',
    'accent': '#5E81AC',
    'success': '#28a745',  # Green for encrypt message button
    'warning': '#EBCB8B',
    'error': '#dc3545',    # Red for burn message button
    'text': '#ECEFF4',
    'background': '#ECEFF4'
}

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

