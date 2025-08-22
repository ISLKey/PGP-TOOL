# How We Built This - PGP Encryption Tool v2.2

**Developer:** Jamie Johnson (TriggerHappyMe)  
**Version:** 2.2  
**Date:** January 2025

---

## 🎯 Project Overview

The PGP Encryption Tool is a comprehensive, offline-first encryption application built with security and usability in mind. This document details the technical decisions, architecture, and development process behind version 2.1.

## 🏗️ Architecture & Design Philosophy

### Core Principles

1. **Security First**: Every component designed with security as the primary concern
2. **Offline Operation**: No internet connectivity required or used
3. **User Privacy**: All data remains on the user's machine
4. **Cross-Platform**: Built with Python for maximum compatibility
5. **Pure Implementation**: No external dependencies on system tools like GPG

### Technology Stack

- **Language**: Python 3.7+
- **GUI Framework**: tkinter (built into Python)
- **Cryptography**: `cryptography` library (industry standard)
- **Data Storage**: Encrypted JSON files
- **Packaging**: PyInstaller for Windows executables

## 🔧 Technical Implementation

### 1. Cryptographic Foundation

**File**: `crypto/pure_python_pgp.py`

We implemented a pure Python PGP system using the `cryptography` library instead of relying on external GPG installations. This decision was made for:

- **Windows Compatibility**: Eliminates GPG installation requirements
- **Security Control**: Full control over cryptographic operations
- **Portability**: Self-contained application
- **Reliability**: No external dependencies to break

**Key Features:**
- RSA key generation (2048, 3072, 4096 bits)
- OAEP padding for encryption
- SHA-256 hashing
- ASCII armor formatting for compatibility

### 2. Enhanced Security Layer (v2.1)

**File**: `security/data_encryption.py`

Version 2.1 introduced comprehensive data encryption:

```python
# All application data is encrypted using AES-256
class DataEncryption:
    def __init__(self, data_dir: str, master_password: str):
        self.encryption_key = self._derive_key(master_password)
    
    def _derive_key(self, password: str) -> bytes:
        # PBKDF2 with 100,000 iterations
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), ...)
        return kdf.derive(password.encode())
```

**Security Features:**
- Master password protection
- PBKDF2 key derivation (100,000 iterations)
- AES-256 encryption for all stored data
- Secure file deletion (multiple overwrite passes)
- Login attempt limiting (10 attempts max)
- Automatic data wipe on breach

### 3. Advanced Entropy Collection

**File**: `crypto/entropy.py`

Enhanced entropy collection ensures cryptographically secure key generation:

**Requirements (v2.1):**
- Minimum 100 characters of text input
- Minimum 10 seconds of mouse movement
- 256 bits of entropy from multiple sources

**Sources:**
- Mouse movement coordinates and timing
- Keyboard input timing patterns
- User-provided random text
- System entropy (secrets module)

```python
def add_mouse_movement(self, x: int, y: int):
    # Track continuous mouse movement time
    if time_diff < 0.1:  # Continuous movement
        self.mouse_movement_time = current_time - self.mouse_start_time
    
    # Generate entropy from coordinates + timing
    entropy_bytes = hashlib.sha256(
        x.to_bytes(4, 'big') + y.to_bytes(4, 'big') + timestamp
    ).digest()
```

### 4. User Interface Design

**File**: `gui/main_window.py`

The GUI is built with tkinter for maximum compatibility and follows these principles:

- **Tabbed Interface**: Separate concerns (Keys, Contacts, Messages)
- **Progressive Disclosure**: Show details only when needed
- **Visual Feedback**: Clear status indicators and progress bars
- **Accessibility**: Keyboard navigation and screen reader friendly

**Key Components:**
- Key management with detailed information display
- Message composition with recipient selection
- History viewer with full message content
- Emergency features (kill switch, burn message)

### 5. Login and Authentication System

**File**: `gui/login_dialog.py`

Version 2.1 introduced mandatory authentication:

**Features:**
- First-time setup with password confirmation
- Secure password hashing (PBKDF2)
- Failed attempt tracking
- Automatic data wipe after 10 failed attempts
- Visual warnings and security notices

```python
def verify_password(self, password):
    # Verify against stored PBKDF2 hash
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), ...)
    try:
        kdf.verify(password.encode(), stored_hash)
        return True
    except:
        return False
```

## 🔄 Development Process

### Version Evolution

**v1.0**: Initial release with basic PGP functionality
- GPG dependency (Windows compatibility issues)
- Basic key generation and message encryption
- Simple GUI interface

**v1.1**: Windows compatibility fix
- Replaced GPG with pure Python implementation
- Maintained feature parity
- Improved error handling

**v1.1.1**: Navigation improvements
- Fixed dialog button layouts
- Enhanced user experience
- Better visual feedback

**v1.1.2**: UI polish
- Color-coded buttons (red for burn, green for encrypt)
- Improved button visibility
- Enhanced status indicators

**v2.0**: Version consistency
- Unified version numbering
- Developer attribution
- Documentation updates

**v2.2**: Login dialog fix
- Fixed missing confirmation password field in first-time setup
- Corrected data directory path resolution
- Enhanced error handling for login dialog
- Improved user experience for initial password setup

**v2.1**: Security and usability overhaul
- Master password protection
- Comprehensive data encryption
- Enhanced entropy requirements
- Detailed key information display
- Full message history viewing
- Advanced security features

### Development Methodology

1. **Security-First Design**: Every feature evaluated for security implications
2. **Iterative Development**: Incremental improvements with user feedback
3. **Comprehensive Testing**: Manual testing of all features
4. **Documentation**: Detailed documentation for users and developers
5. **Backward Compatibility**: Smooth migration between versions

## 🛡️ Security Considerations

### Threat Model

**Protected Against:**
- Unauthorized access to application
- Data theft from storage files
- Weak key generation
- Brute force attacks on stored data
- Memory dumps (limited exposure)

**Assumptions:**
- User's operating system is secure
- Physical access to machine is controlled
- User follows security best practices

### Security Measures

1. **Encryption at Rest**: All data encrypted with user's master password
2. **Secure Key Generation**: Multiple entropy sources with strict requirements
3. **Access Control**: Master password required for all operations
4. **Audit Trail**: Failed login attempts tracked
5. **Emergency Procedures**: Kill switch and burn message features
6. **Secure Deletion**: Multiple overwrite passes for sensitive data

## 📊 Performance Considerations

### Optimization Strategies

1. **Lazy Loading**: GUI components loaded on demand
2. **Efficient Storage**: JSON with compression for large datasets
3. **Memory Management**: Secure clearing of sensitive variables
4. **Responsive UI**: Background processing for crypto operations

### Scalability

- Designed for personal use (hundreds of keys/messages)
- Efficient search and filtering for large datasets
- Minimal memory footprint
- Fast startup time

## 🧪 Testing Strategy

### Manual Testing Procedures

1. **Functional Testing**: All features tested end-to-end
2. **Security Testing**: Attack scenarios simulated
3. **Usability Testing**: User workflow validation
4. **Compatibility Testing**: Multiple Windows versions
5. **Error Handling**: Edge cases and error conditions

### Test Coverage

- Key generation with various parameters
- Message encryption/decryption workflows
- Import/export functionality
- Backup and restore procedures
- Emergency features (kill switch, burn message)
- Login system with attack simulation

## 🚀 Deployment & Distribution

### Packaging Strategy

**Portable Version**: Self-contained executable
- PyInstaller for Windows compilation
- All dependencies bundled
- No installation required
- Registry-free operation

**Development Version**: Python source
- Requirements.txt for dependencies
- Batch file launcher with dependency checking
- Full source code access

### File Structure

```
PGP_Tool_v2.1/
├── main.py                 # Application entry point
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── run_pgp_tool.bat       # Windows launcher
├── crypto/                 # Cryptographic modules
│   ├── pure_python_pgp.py # PGP implementation
│   ├── key_generator.py   # Key management
│   └── entropy.py         # Entropy collection
├── gui/                   # User interface
│   ├── main_window.py     # Main application window
│   ├── dialogs.py         # Dialog windows
│   └── login_dialog.py    # Authentication
├── security/              # Security modules
│   └── data_encryption.py # Data protection
└── docs/                  # Documentation
    ├── README.md
    ├── INSTALLATION_GUIDE.md
    └── HOW_WE_BUILT_THIS.md
```

## 🔮 Future Enhancements

### Planned Features

1. **Multi-User Support**: Separate user profiles
2. **Key Server Integration**: Optional key distribution
3. **Mobile Companion**: QR code key exchange
4. **Advanced Algorithms**: Post-quantum cryptography
5. **Plugin System**: Extensible architecture

### Technical Debt

1. **Code Refactoring**: Modularize large functions
2. **Unit Testing**: Automated test suite
3. **Performance Profiling**: Optimize bottlenecks
4. **Documentation**: API documentation
5. **Internationalization**: Multi-language support

## 📚 Learning Resources

### Cryptography References

- RFC 4880: OpenPGP Message Format
- NIST SP 800-57: Key Management Guidelines
- Cryptography Engineering by Ferguson, Schneier, and Kohno

### Python Security

- Python Cryptographic Authority documentation
- OWASP Python Security Guidelines
- Secure Coding in Python best practices

### GUI Development

- tkinter documentation and tutorials
- Python GUI programming patterns
- Accessibility guidelines for desktop applications

## 🤝 Contributing

### Development Environment Setup

1. Install Python 3.7+
2. Install dependencies: `pip install -r requirements.txt`
3. Run from source: `python main.py`
4. Test thoroughly before submitting changes

### Code Standards

- PEP 8 style guidelines
- Comprehensive docstrings
- Security-focused code reviews
- Error handling for all operations

### Security Guidelines

- Never log sensitive data
- Use secure random number generation
- Validate all user inputs
- Follow principle of least privilege

---

## 📞 Contact & Support

**Developer**: Jamie Johnson (TriggerHappyMe)  
**Version**: 2.1  
**License**: Educational and personal use  

This tool represents a commitment to user privacy and security through open, auditable code and strong cryptographic practices. Every line of code has been written with the user's security and privacy as the top priority.

**Remember**: Your security depends on keeping your master password secret and following security best practices. This tool provides the foundation, but security is a shared responsibility between the software and the user.

---

*"Privacy is not something that I'm merely entitled to, it's an absolute prerequisite." - Marlon Brando*

