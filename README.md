# PGP Encryption Tool
By Jamie Johnson (TriggerHappyMe).
Intercom Services London

A secure, offline PGP encryption and decryption tool with a user-friendly GUI interface for Windows.


## Features

### 🔐 Core Security Features
- **Complete Offline Operation**: No internet connection required or used #(coming soon)#
- **Secure Key Generation**: Uses entropy collection from mouse movements and keyboard input
- **PGP Encryption/Decryption**: Industry-standard OpenPGP implementation
- **Emergency Kill Switch**: Instantly delete all keys and data when needed
- **Burn Message**: Securely delete messages after reading
<img width="492" height="474" alt="Screenshot 2025-08-22 225620" src="https://github.com/user-attachments/assets/b7d72afe-02a0-4a3d-9fe6-de132f55f29d" />

### 🔑 Key Management
- **Generate Key Pairs**: Create RSA keys with customizable key sizes (2048, 3072, 4096 bits)
- **Import/Export Keys**: Support for ASCII armor format (.asc, .pgp files)
- **Contact Management**: Store and manage friends' public keys
- **Key Backup/Restore**: Create encrypted backups of your keys

<img width="797" height="773" alt="Screenshot 2025-08-22 225656" src="https://github.com/user-attachments/assets/648abe9f-9e34-419e-8f90-abda2a230514" />


### 💬 Message Handling
- **Compose Messages**: User-friendly interface for writing encrypted messages
- **Encrypt Messages**: Encrypt messages for specific recipients
- **Decrypt Messages**: Decrypt received messages with your private key
- **Message History**: Keep track of sent and received messages
<img width="800" height="778" alt="Screenshot 2025-08-22 225743" src="https://github.com/user-attachments/assets/f162b951-b9d5-4a7c-88bf-8f62f5ee07d1" />

### 🛡️ Security Features
- **Entropy Collection**: Secure random number generation using mouse and keyboard input
- **Passphrase Protection**: All private keys are protected with strong passphrases
- **Secure Deletion**: Multiple overwrite passes for sensitive data deletion
- **No Data Leakage**: All operations performed locally, no cloud or network access
<img width="946" height="783" alt="Screenshot 2025-08-22 230201" src="https://github.com/user-attachments/assets/07e6e477-b398-4f76-8835-a6e52a83b208" />
<img width="954" height="784" alt="Screenshot 2025-08-22 230310" src="https://github.com/user-attachments/assets/ea8a660c-1710-468c-ad5a-fd4f6db2b301" />
<img width="944" height="773" alt="Screenshot 2025-08-22 230421" src="https://github.com/user-attachments/assets/6519cec3-b189-4386-992a-1337cb1a3778" />


## Installation

### Option 1: Portable Version (Recommended)
1. Download `PGP_Tool_Portable.zip`
2. Extract to any folder
3. Double-click `PGP_Tool.exe` to run

### Option 2: Installer Version
1. Download `PGP_Tool_Installer.zip`
2. Extract to your desired installation folder
3. Run `PGP_Tool.exe` from the extracted folder

### Option 3: Run from Source
1. Install Python 3.7+ and required dependencies:
   ```bash
   pip install cryptography python-gnupg pillow
   ```
2. Run the batch file: `run_pgp_tool.bat`
3. Or run directly: `python main.py`

## Quick Start Guide

### 1. First Launch
- The application will create a `data` folder to store your keys and settings
- No setup or configuration required

### 2. Generate Your First Key Pair
1. Click **"Generate New Key"** in the Keys tab
2. Enter your name, email, and a strong passphrase
3. Follow the entropy collection process:
   - Move your mouse around the collection area
   - Type random text in the input field
   - Wait for sufficient entropy to be collected
4. Click **"Generate Key Pair"** and wait for completion

### 3. Encrypt Your First Message
1. Switch to the **Messages** tab
2. In the **Compose** section:
   - Select a recipient (must have their public key)
   - Enter a subject and message
   - Click **"Encrypt Message"**
3. Copy or save the encrypted message to send to your recipient

### 4. Decrypt a Message
1. In the **Decrypt** section:
   - Paste the encrypted message
   - Click **"Decrypt Message"**
   - Enter your passphrase when prompted
2. The decrypted message will appear below

## User Interface Guide

### Keys Tab
- **Key List**: Shows all your public and private keys
- **Generate New Key**: Create a new PGP key pair
- **Import Key**: Import keys from files or clipboard
- **Export Keys**: Export keys to files
- **Delete Key**: Remove keys from your keyring

### Messages Tab
- **Compose**: Write and encrypt new messages
- **Decrypt**: Decrypt received messages
- **History**: View message history
- **Burn Message**: Securely delete current message

### Menu Options
- **File Menu**:
  - Create Backup: Create encrypted backup of all keys
  - Restore Backup: Restore keys from backup file
  - Emergency Kill Switch: Delete all data permanently
  - Exit: Close the application

## Security Best Practices

### Passphrase Security
- Use a strong, unique passphrase for each key
- Include uppercase, lowercase, numbers, and special characters
- Make it at least 12 characters long
- Don't reuse passphrases from other accounts

### Key Management
- Create regular backups of your keys
- Store backups in a secure, separate location
- Never share your private key or passphrase
- Verify recipient public keys before encrypting

### Message Security
- Use the "Burn Message" feature for sensitive communications
- Don't leave decrypted messages visible on screen
- Clear clipboard after copying encrypted messages
- Use the emergency kill switch if your computer is compromised

## Backup and Recovery

### Creating Backups
1. Go to **File → Create Backup**
2. Enter your key passphrase
3. Choose a strong backup password
4. Save the backup file (.pgpbackup) to a secure location

### Restoring from Backup
1. Go to **File → Restore Backup**
2. Select your backup file
3. Enter the backup password
4. Your keys will be imported into the current keyring

## Emergency Procedures

### Emergency Kill Switch
If your computer is compromised or you need to quickly delete all data:
1. Go to **File → Emergency Kill Switch**
2. Confirm the action (this cannot be undone)
3. Type "DELETE" to confirm
4. All keys, messages, and application data will be permanently deleted

### Burn Message Feature
To securely delete a message after reading:
1. Click the **"Burn Message Now"** button
2. Confirm the action
3. The message will be cleared from all fields and clipboard

## Technical Details

### Encryption Standards
- **Algorithm**: RSA with OAEP padding
- **Key Sizes**: 2048, 3072, or 4096 bits
- **Hash Function**: SHA-256
- **Format**: OpenPGP standard (RFC 4880)

### Entropy Collection
- **Mouse Movement**: X/Y coordinates and timing
- **Keyboard Input**: Key press timing and patterns
- **Random Text**: User-provided random text
- **Minimum Entropy**: 256 bits for key generation

### Data Storage
- **Location**: `data/` folder in application directory
- **Key Storage**: GnuPG keyring format
- **Encryption**: All private keys encrypted with user passphrase
- **Backup Format**: AES-256 encrypted JSON

## Troubleshooting

### Common Issues

**Application won't start**
- Ensure all files are in the same folder
- Run `run_pgp_tool.bat` to check dependencies
- Check Windows compatibility (Windows 7+)

**Key generation fails**
- Ensure sufficient entropy is collected
- Try moving mouse more actively
- Type more random text

**Encryption/Decryption fails**
- Verify recipient's public key is imported
- Check passphrase is correct
- Ensure message format is valid PGP

**Import/Export issues**
- Verify file format is ASCII armor (.asc)
- Check file permissions
- Ensure complete key data is copied

### Getting Help
- Check this README for common solutions
- Verify all steps are followed correctly
- Ensure system requirements are met

## System Requirements

- **Operating System**: Windows 7 or later
- **Memory**: 512 MB RAM minimum
- **Storage**: 100 MB free space
- **Dependencies**: Included in portable version

## File Structure

```
PGP_Tool/
├── PGP_Tool.exe           # Main application
├── run_pgp_tool.bat       # Dependency checker and launcher
├── README.md              # This documentation
├── requirements.txt       # Python dependencies
├── data/                  # Created on first run
│   ├── gnupg/            # Key storage
│   └── settings.json     # Application settings
└── [Additional files for installer version]
```

## Version History

### Version 2.5
- **Entropy Collection Fix**: Reverted to original working entropy system
- **Simplified Requirements**: Removed complex character/time requirements that were causing issues
- **Window Size Fix**: Increased login dialog size to ensure all fields are visible
- **Resizable Dialog**: Login dialog now resizable for different screen sizes
- **Login Dialog Fix**: Fixed missing confirmation password field and create button
- **Enhanced Security**: Master password protection with 10-attempt limit
- **Data Encryption**: All application data encrypted with AES-256
- **Key Information**: Detailed key information display when selected
- **Message History**: Full message viewing with click-to-view functionality
- **Technical Documentation**: "How We Built This" accessible from Help menu
- **Emergency Features**: Data wipe on security breach
- **Pure Python implementation** (no external GPG required)

## License

This software is provided as-is for educational and personal use. Use at your own risk.

## Security Notice

This tool is designed for privacy and security, but no software is 100% secure. Always follow security best practices and keep your system updated. The developers are not responsible for any data loss or security breaches.

---

**Remember**: Your security depends on keeping your passphrases secret and your private keys secure. Never share your private key or passphrase with anyone.


