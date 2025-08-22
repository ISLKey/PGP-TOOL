# PGP Tool v4.2.0

## Professional PGP Encryption & Secure Communication Platform

**Developed by Jamie Johnson (TriggerHappyMe)**

---

## 🚀 **Overview**

PGP Tool is a comprehensive, professional-grade PGP encryption and secure communication platform that combines military-grade encryption with real-time communication capabilities. Built with pure Python cryptography, it provides enterprise-level security without requiring external GPG installations.

### **Key Highlights:**
- 🔒 **Military-Grade Encryption** - RSA 2048/3072/4096-bit keys with AES encryption
- 💬 **Real-Time Communication** - IRC-based private and group chat with PGP encryption
- 👥 **Group Management** - Create, join, and manage encrypted group conversations
- 📱 **Professional Interface** - Modern tabbed GUI with intuitive design
- 🔐 **Master Password Protection** - All data encrypted at rest
- 🌐 **Cross-Platform** - Windows, Linux, and macOS support
- 📊 **Message History** - Encrypted storage of all communications
- 👤 **Contact Management** - Unified contact system across all features

---

## 📋 **Table of Contents**

1. [Features](#features)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Core PGP Features](#core-pgp-features)
5. [Communication Features](#communication-features)
6. [Group Chat](#group-chat)
7. [Contact Management](#contact-management)
8. [Security Features](#security-features)
9. [Advanced Usage](#advanced-usage)
10. [Troubleshooting](#troubleshooting)
11. [Technical Details](#technical-details)
12. [License](#license)

---



## 🎯 **Features**

### **Core PGP Encryption**
- **Key Generation** - Generate RSA keys (2048, 3072, 4096 bits) with customizable passphrases
- **Message Encryption/Decryption** - Full PGP message encryption with digital signatures
- **Key Management** - Import, export, delete, and backup PGP keys
- **Digital Signatures** - Sign and verify message authenticity
- **Key Information** - Detailed key information with passphrase verification
- **Backup & Restore** - Secure encrypted backup of all keys and data

### **Real-Time Communication**
- **Private Chat** - Secure IRC-based private messaging with PGP encryption
- **Group Chat** - Multi-user group conversations with real-time messaging
- **Message History** - Encrypted storage of all chat conversations
- **Contact Integration** - Unified contact system across all communication features
- **Cross-Platform Messaging** - Connect to any IRC network for global communication

### **Group Management**
- **Create Groups** - Set up private or public groups with member limits
- **Join Groups** - Join existing groups with password validation
- **Delete Groups** - Remove groups with proper permission checks
- **Member Management** - View members, assign admin roles, manage permissions
- **IRC Integration** - Automatic IRC channel creation and management

### **Contact Management**
- **Unified Contacts** - Single contact database for entire application
- **Contact Encryption** - All contact data encrypted with master password
- **Cross-Tab Sync** - Contacts available in Keys, Messages, Chat, and Contacts tabs
- **Advanced Deletion** - Choose to delete contact only or contact + associated key
- **IRC Integration** - Link contacts with IRC nicknames for seamless communication

### **Security & Privacy**
- **Master Password** - Protects all application data with strong encryption
- **Encrypted Storage** - All data encrypted at rest using AES encryption
- **Secure Key Storage** - Protected PGP key management
- **Login Protection** - Password-based access control
- **Data Integrity** - Comprehensive data validation and error handling

### **Professional Interface**
- **Tabbed Design** - Organized workflow with Keys, Messages, Contacts, and Chat tabs
- **Context Menus** - Right-click operations for advanced management
- **Confirmation Dialogs** - Safe operation confirmation for destructive actions
- **Error Handling** - Comprehensive error management with user-friendly messages
- **Responsive Design** - Optimized for different screen sizes and resolutions

---

## 💻 **Installation**

### **System Requirements**
- **Operating System**: Windows 10+, Linux (Ubuntu 18.04+), macOS 10.14+
- **Python**: 3.7 or later
- **Memory**: 512MB RAM minimum, 1GB recommended
- **Storage**: 100MB free space
- **Network**: Internet connection for IRC communication (optional)

### **Quick Installation (Windows)**
1. **Download** the latest release zip file
2. **Extract** to your desired location
3. **Run** `run_pgp_tool.bat`
4. **Follow** the automatic setup process

### **Manual Installation**
```bash
# Clone or download the repository
git clone https://github.com/your-repo/pgp-tool.git
cd pgp-tool

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### **Dependencies**
- `cryptography` - Core encryption functionality
- `pillow` - Image processing for GUI
- `tkinter` - GUI framework (usually included with Python)
- `irc` - IRC client functionality (optional, for chat features)

---

## 🚀 **Quick Start**

### **First Launch**
1. **Run** the application using `run_pgp_tool.bat` (Windows) or `python main.py`
2. **Set Master Password** - Create a strong password to protect your data
3. **Generate Your First Key** - Go to Keys tab → "Generate Key Pair"
4. **Start Encrypting** - Go to Messages tab → Compose encrypted messages

### **Basic Workflow**
```
1. Generate Key Pair → 2. Add Contacts → 3. Exchange Public Keys → 4. Start Communicating
```

### **5-Minute Setup**
1. **Launch Application** (30 seconds)
2. **Create Master Password** (1 minute)
3. **Generate Key Pair** (2 minutes)
4. **Add First Contact** (1 minute)
5. **Send First Encrypted Message** (30 seconds)

---


## 🔐 **Core PGP Features**

### **Key Generation**
- **Multiple Key Sizes**: Choose from 2048, 3072, or 4096-bit RSA keys
- **Custom Passphrases**: Protect private keys with strong passphrases
- **Entropy Collection**: Secure random number generation for key creation
- **Key Validation**: Automatic validation of generated keys

```
Keys Tab → Generate Key Pair → Choose size → Set passphrase → Generate
```

### **Message Encryption**
- **Full PGP Compatibility**: Standard PGP message format
- **Digital Signatures**: Sign messages for authenticity verification
- **Recipient Selection**: Choose from your contact list
- **Clipboard Integration**: Easy copy/paste of encrypted messages

```
Messages Tab → Compose → Select recipient → Write message → Encrypt & Sign
```

### **Message Decryption**
- **Automatic Detection**: Recognizes PGP message format
- **Signature Verification**: Validates message authenticity
- **Passphrase Prompt**: Secure private key access
- **Clear Display**: Decrypted message with verification status

```
Messages Tab → Decrypt → Paste encrypted message → Enter passphrase → View decrypted
```

### **Key Management**
- **Import Keys**: Support for .asc, .gpg, and text format keys
- **Export Keys**: Save public keys for sharing
- **Key Information**: Detailed key properties and fingerprints
- **Key Deletion**: Secure removal of keys with confirmation

### **Backup & Restore**
- **Encrypted Backups**: Password-protected backup of all keys
- **Complete Restore**: Restore all keys from backup
- **Emergency Deletion**: Secure wipe of all data
- **Data Migration**: Move data between installations

---

## 💬 **Communication Features**

### **Private Chat**
Real-time encrypted communication with individual contacts via IRC.

**Features:**
- **PGP Encryption**: All messages encrypted end-to-end
- **Digital Signatures**: Message authenticity verification
- **Message History**: Encrypted storage of conversations
- **Contact Status**: Online/offline status tracking
- **Multiple Networks**: Connect to any IRC network

**Usage:**
```
Chat Tab → Private Chat → Connect to IRC → Select contact → Start chatting
```

### **Message Chunking**
- **Large Message Support**: Automatically splits large messages
- **Reliable Delivery**: Ensures complete message transmission
- **Automatic Assembly**: Reconstructs messages on recipient side
- **Timeout Handling**: Manages incomplete message chunks

### **Network Support**
- **Popular Networks**: Freenode, Libera.Chat, OFTC, and more
- **Custom Servers**: Add your own IRC servers
- **SSL/TLS Support**: Secure connections to IRC networks
- **Auto-Reconnection**: Automatic reconnection on network issues

---

## 👥 **Group Chat**

### **Group Creation**
Create secure group conversations with multiple participants.

**Features:**
- **Privacy Settings**: Public or private groups
- **Password Protection**: Optional password for group access
- **Member Limits**: Set maximum number of participants (1-1000)
- **Admin Controls**: Assign admin roles for group management
- **IRC Integration**: Automatic IRC channel creation

**Creating a Group:**
```
Chat Tab → Group Chat → Create Group → Set name/description → Configure privacy → Create
```

### **Group Management**
- **Join Groups**: Join existing groups with validation
- **Leave Groups**: Clean departure from groups
- **Delete Groups**: Remove groups (creator/admin only)
- **Member Management**: View participants and their roles
- **Permission System**: Creator and admin role management

### **Group Features**
- **Real-Time Messaging**: Instant message delivery to all members
- **Message History**: Complete conversation history
- **Member Notifications**: Join/leave notifications
- **IRC Channel Validation**: Verifies channel existence and passwords
- **Cross-Platform**: Works across different IRC clients

**Group Operations:**
```
Right-click Group → [Join/Leave/Delete/Manage Members]
```

---

## 👤 **Contact Management**

### **Unified Contact System**
Single contact database accessible across all application features.

**Features:**
- **Encrypted Storage**: All contacts protected with master password
- **Cross-Tab Availability**: Contacts visible in Keys, Messages, Chat tabs
- **IRC Integration**: Link contacts with IRC nicknames
- **Key Association**: Automatic linking with PGP keys
- **Real-Time Sync**: Changes reflect immediately across all tabs

### **Contact Operations**
- **Add Contacts**: Manual entry or import from key files
- **Edit Contacts**: Update contact information and IRC nicknames
- **Delete Contacts**: Choose contact-only or contact+key deletion
- **Import Keys**: Add contacts directly from public key files
- **Export Information**: Share contact details securely

### **Contact Information**
- **Name**: Display name for the contact
- **Key ID**: Associated PGP key identifier
- **IRC Nickname**: Username for chat communication
- **Date Added**: When contact was created
- **Key Fingerprint**: Unique key identifier

**Adding Contacts:**
```
Contacts Tab → Add Contact → Enter details → Save
Messages Tab → Import Contact Key → Select file → Add contact info
```

### **Advanced Deletion**
Choose between different deletion options:
- **Contact Only**: Remove from contact list, keep PGP key
- **Contact + Key**: Remove contact and associated PGP key
- **Warning System**: Clear warnings about key deletion consequences

---


## 🛡️ **Security Features**

### **Master Password Protection**
- **Application Lock**: Protects access to all features
- **Data Encryption**: All stored data encrypted with master password
- **Session Management**: Automatic logout on inactivity
- **Password Strength**: Enforced strong password requirements

### **Encryption Standards**
- **RSA Encryption**: Industry-standard RSA key pairs
- **AES Encryption**: AES-256 for data storage encryption
- **PBKDF2**: Key derivation for password-based encryption
- **Secure Random**: Cryptographically secure random number generation

### **Data Protection**
- **Encrypted Storage**: All files encrypted at rest
- **Secure Deletion**: Multiple-pass secure file deletion
- **Memory Protection**: Sensitive data cleared from memory
- **Backup Encryption**: Encrypted backups with separate passwords

### **Network Security**
- **SSL/TLS**: Encrypted connections to IRC networks
- **Certificate Validation**: Proper SSL certificate checking
- **No Plain Text**: All sensitive data transmitted encrypted
- **Connection Verification**: Network connection validation

---

## 🔧 **Advanced Usage**

### **Custom IRC Networks**
Add your own IRC servers for private communication:

```
Chat Tab → Settings → Add Custom Server → Enter details → Save
```

### **Key Import/Export**
- **Bulk Import**: Import multiple keys from files
- **Selective Export**: Export specific keys
- **Format Support**: .asc, .gpg, and plain text formats
- **Verification**: Automatic key validation on import

### **Message History Management**
- **Automatic Saving**: Optional message history storage
- **Encrypted Storage**: All history encrypted with master password
- **Search Functionality**: Find specific messages or conversations
- **Export Options**: Export message history for backup

### **Backup Strategies**
- **Regular Backups**: Schedule automatic backups
- **Multiple Locations**: Store backups in different locations
- **Verification**: Test backup restoration regularly
- **Emergency Procedures**: Quick data recovery processes

### **Performance Optimization**
- **Memory Management**: Efficient memory usage
- **Network Optimization**: Optimized IRC connections
- **Storage Efficiency**: Compressed encrypted storage
- **Startup Speed**: Fast application initialization

---

## 🔍 **Troubleshooting**

### **Common Issues**

**Application Won't Start**
- Verify Python 3.7+ is installed
- Check all dependencies are installed: `pip install -r requirements.txt`
- Run from command line to see error messages

**Can't See Messages from Other Users**
- Ensure you're connected to IRC network
- Verify you're in the same channel/group
- Check network connectivity
- Restart the application if needed

**Contact Deletion Errors**
- Ensure contact is selected before deletion
- Check if contact has associated keys
- Verify master password is correct
- Try contact-only deletion first

**IRC Connection Issues**
- Verify network connectivity
- Check IRC server settings
- Try different IRC networks
- Disable firewall/antivirus temporarily

**Key Generation Problems**
- Ensure sufficient entropy (move mouse, type randomly)
- Check available disk space
- Verify write permissions in application directory
- Try different key sizes

### **Error Messages**

**"Master password incorrect"**
- Re-enter your master password carefully
- Check caps lock status
- Reset application if password forgotten (data will be lost)

**"Key not found"**
- Refresh key list
- Re-import missing keys
- Check key fingerprint matches

**"IRC connection failed"**
- Check internet connectivity
- Verify IRC server details
- Try different network/port
- Check firewall settings

### **Performance Issues**
- **Slow Startup**: Clear application cache, restart
- **High Memory Usage**: Restart application, check for memory leaks
- **Network Lag**: Check internet connection, try different IRC server
- **UI Freezing**: Close and restart application

---

## 🔬 **Technical Details**

### **Architecture**
- **Language**: Python 3.7+
- **GUI Framework**: Tkinter (cross-platform)
- **Encryption**: Cryptography library (pure Python)
- **IRC Client**: Custom IRC implementation
- **Storage**: Encrypted JSON files

### **File Structure**
```
pgp_tool_fixed/
├── main.py                 # Application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── run_pgp_tool.bat      # Windows launcher
├── crypto/               # Encryption modules
│   ├── key_generator.py  # Key generation
│   ├── pgp_handler.py    # PGP operations
│   └── pure_python_pgp.py # Core PGP implementation
├── gui/                  # User interface
│   ├── main_window.py    # Main application window
│   ├── dialogs.py        # Dialog windows
│   └── login_dialog.py   # Login interface
├── chat/                 # Communication modules
│   ├── irc_client.py     # IRC client
│   ├── secure_chat.py    # Secure messaging
│   └── group_chat.py     # Group chat functionality
├── security/             # Security modules
│   └── data_encryption.py # Data encryption
└── data_storage/         # Encrypted data files
```

### **Data Storage**
- **Keys**: Encrypted PGP keys in JSON format
- **Contacts**: Encrypted contact database
- **Messages**: Encrypted message history
- **Settings**: Application configuration
- **Backups**: Encrypted backup files

### **Network Protocols**
- **IRC**: Internet Relay Chat for real-time communication
- **SSL/TLS**: Secure connections to IRC networks
- **PGP**: Pretty Good Privacy for message encryption
- **JSON**: Data serialization format

### **Security Implementation**
- **AES-256**: Symmetric encryption for data storage
- **RSA**: Asymmetric encryption for PGP operations
- **PBKDF2**: Password-based key derivation
- **HMAC**: Message authentication codes
- **Secure Random**: Cryptographically secure randomness

---

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

### **Third-Party Libraries**
- **Cryptography**: BSD License
- **Pillow**: PIL Software License
- **IRC Library**: MIT License

---

## 👨‍💻 **Developer**

**Jamie Johnson (TriggerHappyMe)**
- Professional PGP encryption and secure communication platform
- Enterprise-grade security with user-friendly interface
- Cross-platform compatibility and modern design

---

## 📞 **Support**

For support, bug reports, or feature requests:
1. Check the troubleshooting section above
2. Review the documentation thoroughly
3. Test with minimal configuration
4. Provide detailed error messages and steps to reproduce

---

## 🎯 **Version History**

### **v4.2.0** (Latest)
- 🔧 Fixed key ID truncation bug in profile display
- 🔑 Enhanced key coordination and mismatch resolution
- 🔄 Improved chat system with automatic profile refresh
- 📡 Complete IRC connection and messaging fixes
- 🛡️ Enhanced encryption initialization and error handling

### **v4.1.x** (Previous Releases)
- Chat system implementation and comprehensive fixes
- Profile selector enhancements and encryption integration
- Message decryption improvements and error diagnostics
- IRC connection stability and fallback mechanisms

### **v4.0.x** (Foundation)
- ✅ Fixed message receiving in group chat
- ✅ Fixed contact deletion errors
- ✅ Improved IRC channel validation
- ✅ Enhanced error handling
- 🎉 Complete group chat system
- 🎉 Unified contact management
- 🎉 Professional branding and versioning

---

**PGP Tool v4.2.0 - Professional PGP Encryption & Secure Communication Platform**

*Secure communication made simple, professional, and reliable.*

