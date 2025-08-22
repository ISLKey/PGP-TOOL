"""
Login Dialog Module
Handles application password protection and security features
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import hashlib
import json
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import *


class LoginDialog:
    """Login dialog for application password protection"""
    
    def __init__(self, parent=None):
        """Initialize the login dialog"""
        self.parent = parent
        self.result = False  # Initialize to False instead of None
        
        # Use the correct data directory from config
        data_dir = DATA_DIR
        os.makedirs(data_dir, exist_ok=True)
        
        self.login_attempts_file = os.path.join(data_dir, "login_attempts.json")
        self.password_hash_file = os.path.join(data_dir, "app_password.json")
        
        self.create_dialog()
    
    def create_dialog(self):
        """Create the login dialog"""
        self.dialog = tk.Tk() if self.parent is None else tk.Toplevel(self.parent)
        self.dialog.title(f"{APP_NAME} - Login")
        self.dialog.geometry("500x450")  # Increased from 450x350 to show all fields
        self.dialog.resizable(True, True)  # Allow resizing in case user needs more space
        
        # Make it modal
        if self.parent:
            self.dialog.transient(self.parent)
            self.dialog.grab_set()
        
        # Center the dialog
        self.center_dialog()
        
        # Handle window closing
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
        # Create main frame
        main_frame = ttk.Frame(self.dialog, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text=f"{APP_NAME} v{APP_VERSION}", 
            font=('Arial', 18, 'bold')
        )
        title_label.pack(pady=(0, 5))
        
        # Developer info
        dev_label = ttk.Label(
            main_frame, 
            text=f"Developed by {APP_AUTHOR}", 
            font=('Arial', 10)
        )
        dev_label.pack(pady=(0, 20))
        
        # Check if this is first run
        if not self.has_password():
            self.create_setup_interface(main_frame)
        else:
            self.create_login_interface(main_frame)
    
    def center_dialog(self):
        """Center the dialog on screen"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        
        # Ensure minimum size for visibility
        if width < 500:
            width = 500
        if height < 450:
            height = 450
            
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        
        # Ensure dialog doesn't go off screen
        if x < 0:
            x = 0
        if y < 0:
            y = 0
            
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def has_password(self):
        """Check if application password is already set"""
        return os.path.exists(self.password_hash_file)
    
    def create_setup_interface(self, parent):
        """Create the initial password setup interface"""
        # Setup instructions
        setup_label = ttk.Label(
            parent, 
            text="First Time Setup", 
            font=('Arial', 14, 'bold')
        )
        setup_label.pack(pady=(0, 10))
        
        instructions = tk.Text(parent, height=4, wrap=tk.WORD, font=('Arial', 9))
        instructions.pack(fill=tk.X, pady=(0, 20))
        instructions.insert(tk.END, 
            "Welcome to PGP Encryption Tool! For security, you need to set a master password. "
            "This password will protect access to the application and encrypt all your data. "
            "Choose a strong password - you'll need it every time you use the application."
        )
        instructions.config(state=tk.DISABLED)
        
        # Password fields
        ttk.Label(parent, text="Choose Master Password:").pack(anchor=tk.W, pady=5)
        self.setup_password_var = tk.StringVar()
        self.setup_password_entry = ttk.Entry(
            parent, 
            textvariable=self.setup_password_var, 
            show="*", 
            width=40,
            font=('Arial', 10)
        )
        self.setup_password_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(parent, text="Confirm Master Password:").pack(anchor=tk.W, pady=5)
        self.confirm_password_var = tk.StringVar()
        self.confirm_password_entry = ttk.Entry(
            parent, 
            textvariable=self.confirm_password_var, 
            show="*", 
            width=40,
            font=('Arial', 10)
        )
        self.confirm_password_entry.pack(fill=tk.X, pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame, 
            text="Exit", 
            command=self.on_cancel
        ).pack(side=tk.RIGHT)
        
        ttk.Button(
            button_frame, 
            text="Set Password", 
            command=self.setup_password
        ).pack(side=tk.RIGHT, padx=(0, 10))
        
        # Focus on first entry
        self.setup_password_entry.focus()
        
        # Bind Enter key
        self.setup_password_entry.bind('<Return>', lambda e: self.confirm_password_entry.focus())
        self.confirm_password_entry.bind('<Return>', lambda e: self.setup_password())
    
    def create_login_interface(self, parent):
        """Create the login interface"""
        # Login instructions
        login_label = ttk.Label(
            parent, 
            text="Enter Master Password", 
            font=('Arial', 14, 'bold')
        )
        login_label.pack(pady=(0, 20))
        
        # Show remaining attempts
        attempts_info = self.get_login_attempts_info()
        remaining = MAX_LOGIN_ATTEMPTS - attempts_info['failed_attempts']
        
        if attempts_info['failed_attempts'] > 0:
            warning_text = f"⚠️ Warning: {attempts_info['failed_attempts']} failed attempt(s). "
            warning_text += f"{remaining} attempts remaining before data wipe!"
            
            warning_label = ttk.Label(
                parent, 
                text=warning_text, 
                font=('Arial', 10, 'bold'),
                foreground='red'
            )
            warning_label.pack(pady=(0, 15))
        
        # Security warning
        security_warning = tk.Text(parent, height=3, wrap=tk.WORD, font=('Arial', 9))
        security_warning.pack(fill=tk.X, pady=(0, 20))
        security_warning.insert(tk.END, 
            f"🔒 Security Notice: After {MAX_LOGIN_ATTEMPTS} failed login attempts, "
            "all application data will be permanently deleted for security. "
            "Make sure you remember your master password!"
        )
        security_warning.config(state=tk.DISABLED)
        
        # Password field
        ttk.Label(parent, text="Master Password:").pack(anchor=tk.W, pady=5)
        self.login_password_var = tk.StringVar()
        self.login_password_entry = ttk.Entry(
            parent, 
            textvariable=self.login_password_var, 
            show="*", 
            width=40,
            font=('Arial', 10)
        )
        self.login_password_entry.pack(fill=tk.X, pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame, 
            text="Exit", 
            command=self.on_cancel
        ).pack(side=tk.RIGHT)
        
        ttk.Button(
            button_frame, 
            text="Login", 
            command=self.login
        ).pack(side=tk.RIGHT, padx=(0, 10))
        
        # Focus on password entry
        self.login_password_entry.focus()
        
        # Bind Enter key
        self.login_password_entry.bind('<Return>', lambda e: self.login())
    
    def setup_password(self):
        """Set up the initial password"""
        # Get password directly from Entry widgets instead of StringVar
        password = self.setup_password_entry.get().strip()
        confirm = self.confirm_password_entry.get().strip()
        
        if len(password) < 8:
            messagebox.showerror("Error", f"Password must be at least 8 characters long. Current length: {len(password)}")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        # Hash and save the password
        try:
            password_hash = self.hash_password(password)
            self.save_password_hash(password_hash)
            
            # Initialize login attempts
            self.reset_login_attempts()
            
            # CRITICAL FIX: Store the password for encryption initialization
            self.master_password = password
            
            messagebox.showinfo("Success", "Master password set successfully!")
            self.result = True
            print("Debug: Password setup successful, result set to True")
            print("Debug: Master password stored for encryption initialization")
            self.dialog.quit()  # Use quit() instead of destroy() to return control
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set password: {str(e)}")
    
    def login(self):
        """Handle login attempt"""
        # Get password directly from Entry widget instead of StringVar
        password = self.login_password_entry.get().strip()
        
        if not password:
            messagebox.showerror("Error", "Please enter your password")
            return
        
        try:
            # Check password
            if self.verify_password(password):
                # Reset failed attempts on successful login
                self.reset_login_attempts()
                
                # CRITICAL FIX: Store the password for encryption initialization
                self.master_password = password
                
                self.result = True
                print("Debug: Login successful, result set to True")
                print("Debug: Master password stored for encryption initialization")
                self.dialog.quit()  # Use quit() instead of destroy() to return control
            else:
                # Increment failed attempts
                attempts_info = self.increment_failed_attempts()
                remaining = MAX_LOGIN_ATTEMPTS - attempts_info['failed_attempts']
                
                if remaining <= 0:
                    # Maximum attempts reached - wipe data
                    self.wipe_all_data()
                else:
                    messagebox.showerror(
                        "Login Failed", 
                        f"Incorrect password!\n\n"
                        f"Attempts remaining: {remaining}\n"
                        f"All data will be wiped after {MAX_LOGIN_ATTEMPTS} failed attempts!"
                    )
                    
                    # Clear password field
                    self.login_password_entry.delete(0, tk.END)  # Clear Entry widget directly
                    self.login_password_entry.focus()
        
        except Exception as e:
            messagebox.showerror("Error", f"Login failed: {str(e)}")
    
    def hash_password(self, password):
        """Hash a password using PBKDF2"""
        salt = secrets.token_bytes(32)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(password.encode())
        return {
            'salt': base64.b64encode(salt).decode(),
            'hash': base64.b64encode(key).decode()
        }
    
    def verify_password(self, password):
        """Verify a password against stored hash"""
        try:
            with open(self.password_hash_file, 'r') as f:
                stored_data = json.load(f)
            
            salt = base64.b64decode(stored_data['salt'])
            stored_hash = base64.b64decode(stored_data['hash'])
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            try:
                kdf.verify(password.encode(), stored_hash)
                return True
            except:
                return False
                
        except Exception:
            return False
    
    def save_password_hash(self, password_hash):
        """Save password hash to file"""
        with open(self.password_hash_file, 'w') as f:
            json.dump(password_hash, f)
    
    def get_login_attempts_info(self):
        """Get current login attempts information"""
        if os.path.exists(self.login_attempts_file):
            try:
                with open(self.login_attempts_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {'failed_attempts': 0, 'last_attempt': None}
    
    def increment_failed_attempts(self):
        """Increment failed login attempts"""
        attempts_info = self.get_login_attempts_info()
        attempts_info['failed_attempts'] += 1
        attempts_info['last_attempt'] = int(__import__('time').time())
        
        with open(self.login_attempts_file, 'w') as f:
            json.dump(attempts_info, f)
        
        return attempts_info
    
    def reset_login_attempts(self):
        """Reset failed login attempts"""
        attempts_info = {'failed_attempts': 0, 'last_attempt': None}
        with open(self.login_attempts_file, 'w') as f:
            json.dump(attempts_info, f)
    
    def wipe_all_data(self):
        """Wipe all application data after too many failed attempts"""
        messagebox.showerror(
            "SECURITY BREACH DETECTED", 
            f"Maximum login attempts ({MAX_LOGIN_ATTEMPTS}) exceeded!\n\n"
            "All application data will now be permanently deleted for security.\n\n"
            "The application will exit."
        )
        
        try:
            # Import the emergency deletion function
            from crypto.key_generator import SecureKeyGenerator
            
            # Perform emergency deletion
            generator = SecureKeyGenerator(os.path.join(DATA_DIR, "gnupg"))
            generator.emergency_delete_all()
            
            # Delete all files in data directory
            import shutil
            if os.path.exists(DATA_DIR):
                # Secure deletion - overwrite files multiple times
                for root, dirs, files in os.walk(DATA_DIR):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            # Overwrite file with random data 3 times
                            if os.path.exists(file_path):
                                file_size = os.path.getsize(file_path)
                                with open(file_path, 'wb') as f:
                                    for _ in range(3):
                                        f.seek(0)
                                        f.write(secrets.token_bytes(file_size))
                                        f.flush()
                                        os.fsync(f.fileno())
                        except:
                            pass
                
                # Remove directory
                shutil.rmtree(DATA_DIR, ignore_errors=True)
            
            messagebox.showinfo("Security Wipe Complete", "All data has been permanently deleted.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Data wipe encountered an error: {str(e)}")
        
        # Exit application
        sys.exit(0)
    
    def on_cancel(self):
        """Handle dialog cancellation"""
        self.result = False
        print("Debug: Dialog cancelled, result set to False")
        self.dialog.quit()  # Use quit() instead of destroy()
    
    def show(self):
        """Show the dialog and return result"""
        print("Debug: Showing login dialog")
        self.dialog.mainloop()
        print(f"Debug: Dialog mainloop ended, result = {self.result}")
        
        # Destroy the dialog after mainloop ends
        try:
            self.dialog.destroy()
        except:
            pass  # Dialog might already be destroyed
            
        return self.result


def main():
    """Test the login dialog"""
    dialog = LoginDialog()
    result = dialog.show()
    print(f"Login result: {result}")


if __name__ == "__main__":
    main()

