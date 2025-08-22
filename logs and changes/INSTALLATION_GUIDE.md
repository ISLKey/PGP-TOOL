# PGP Encryption Tool - Installation Guide

## Overview

This package contains a complete PGP encryption and decryption tool with a graphical user interface. The tool works completely offline and provides secure key generation, message encryption/decryption, and key management features.

## Package Contents

```
PGP_Tool/
├── main.py                    # Main application entry point
├── run_pgp_tool.bat          # Windows launcher with dependency checking
├── config.py                 # Application configuration
├── requirements.txt          # Python dependencies
├── README.md                 # Complete user documentation
├── INSTALLATION_GUIDE.md     # This installation guide
├── pgp_tool_architecture.md  # Technical architecture documentation
├── gui/                      # GUI components
│   ├── __init__.py
│   ├── main_window.py        # Main application window
│   └── dialogs.py            # Dialog boxes for key generation, etc.
├── crypto/                   # Cryptographic components
│   ├── __init__.py
│   ├── pgp_handler.py        # PGP operations
│   ├── entropy.py            # Entropy collection for secure key generation
│   └── key_generator.py      # Key generation and management
├── test_*.py                 # Test scripts
├── build_windows_exe.py      # Build script for Windows executable
└── pgp_tool.spec            # PyInstaller specification
```

## Installation Options

### Option 1: Run from Source (Recommended for Development)

**Requirements:**
- Python 3.7 or later
- Windows 7 or later

**Steps:**
1. Extract the package to your desired location
2. Open Command Prompt or PowerShell in the extracted folder
3. Run the dependency checker: `run_pgp_tool.bat`
4. The script will automatically install required dependencies and launch the application

**Manual Installation:**
If the batch file doesn't work, install dependencies manually:
```bash
pip install cryptography python-gnupg pillow
python main.py
```

### Option 2: Build Windows Executable

**Requirements:**
- Python 3.7+ with development headers
- PyInstaller

**Steps:**
1. Install build dependencies:
   ```bash
   pip install pyinstaller
   ```
2. Run the build script:
   ```bash
   python build_windows_exe.py
   ```
3. The executable will be created in the `dist/` folder

### Option 3: Portable Executable (When Available)

If a pre-built executable is provided:
1. Extract `PGP_Tool_Portable.zip`
2. Double-click `PGP_Tool.exe` to run
3. No installation or dependencies required

## First Run Setup

### 1. Application Launch
- The application will create a `data/` folder for storing keys and settings
- No internet connection is required or used

### 2. Generate Your First Key Pair
1. Click **"Generate New Key"** in the Keys tab
2. Fill in your information:
   - **Name**: Your full name
   - **Email**: Your email address
   - **Passphrase**: A strong, memorable passphrase (at least 8 characters)
   - **Key Size**: 2048 bits (standard), 3072 bits (enhanced), or 4096 bits (maximum security)

3. **Entropy Collection**:
   - Move your mouse around the collection area
   - Type random text in the input field
   - Wait for sufficient entropy to be collected (progress bar will show 100%)

4. Click **"Generate Key Pair"** and wait for completion

### 3. Import Friend's Public Keys
1. Click **"Import Key"** in the Keys tab
2. Paste the public key or load from file
3. The key will be added to your contact list for encryption

## Usage Examples

### Encrypting a Message
1. Go to the **Messages** tab → **Compose** section
2. Select recipient from the dropdown
3. Enter subject and message
4. Click **"Encrypt Message"**
5. Copy or save the encrypted message to send

### Decrypting a Message
1. Go to the **Messages** tab → **Decrypt** section
2. Paste the encrypted message
3. Click **"Decrypt Message"**
4. Enter your passphrase when prompted
5. The decrypted message will appear below

### Creating Backups
1. Go to **File** → **Create Backup**
2. Enter your key passphrase
3. Choose a strong backup password
4. Save the backup file (.pgpbackup) to a secure location

### Emergency Data Deletion
If your computer is compromised:
1. Go to **File** → **Emergency Kill Switch**
2. Confirm the action (this cannot be undone)
3. Type "DELETE" to confirm
4. All keys and data will be permanently deleted

## Security Recommendations

### Passphrase Security
- Use unique, strong passphrases for each key
- Include uppercase, lowercase, numbers, and symbols
- Make passphrases at least 12 characters long
- Don't reuse passphrases from other accounts

### Key Management
- Create regular backups of your keys
- Store backups in secure, separate locations
- Never share your private key or passphrase
- Verify public keys before encrypting sensitive messages

### Operational Security
- Use the "Burn Message" feature for sensitive communications
- Don't leave decrypted messages visible on screen
- Clear clipboard after copying encrypted messages
- Use the emergency kill switch if compromised

## Troubleshooting

### Common Issues

**Application won't start:**
- Ensure Python 3.7+ is installed
- Run `run_pgp_tool.bat` to check dependencies
- Install missing packages manually if needed

**Key generation fails:**
- Ensure sufficient entropy is collected (move mouse, type text)
- Try generating with a smaller key size first
- Check that you have write permissions in the application folder

**Encryption/Decryption fails:**
- Verify recipient's public key is imported correctly
- Check that your passphrase is correct
- Ensure the message format is valid PGP

**Import/Export issues:**
- Verify the key format is ASCII armor (.asc)
- Check that the complete key data is copied
- Ensure file permissions allow reading/writing

### Getting Support

1. Check this installation guide for solutions
2. Review the main README.md for detailed usage instructions
3. Verify all requirements are met
4. Test with the included test scripts

## System Requirements

### Minimum Requirements
- **OS**: Windows 7 or later
- **RAM**: 512 MB
- **Storage**: 100 MB free space
- **Python**: 3.7+ (for source installation)

### Recommended Requirements
- **OS**: Windows 10 or later
- **RAM**: 1 GB
- **Storage**: 500 MB free space
- **Python**: 3.9+ (for source installation)

## File Locations

### Application Data
- **Keys**: `data/gnupg/` folder
- **Settings**: `data/settings.json`
- **Logs**: `data/logs/` (if enabled)

### Backup Files
- **Extension**: `.pgpbackup`
- **Format**: AES-256 encrypted JSON
- **Location**: User-specified during backup creation

## Security Notes

### Data Protection
- All private keys are encrypted with your passphrase
- No data is transmitted over the internet
- Sensitive data is securely deleted when requested
- Entropy collection ensures cryptographically secure key generation

### Privacy
- No telemetry or analytics are collected
- No network connections are made
- All operations are performed locally
- User data never leaves the local machine

## Version Information

- **Version**: 2.0
- **Build Date**: 2025-01-20
- **Python Version**: 3.7+
- **Supported Platforms**: Windows 7+

## License and Disclaimer

This software is provided as-is for educational and personal use. The developers are not responsible for any data loss or security breaches. Users are responsible for maintaining the security of their passphrases and backup files.

---

For complete usage instructions, see README.md
For technical details, see pgp_tool_architecture.md

