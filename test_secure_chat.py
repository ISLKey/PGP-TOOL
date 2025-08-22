"""
Secure Chat Test Interface
Test PGP+IRC integration before full UI integration
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chat.secure_chat import SecureChatHandler, SecureChatMessage, SecureChatContact
from crypto.pgp_handler import PGPHandler


class SecureChatTestWindow:
    """Test window for secure IRC+PGP chat"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Secure Chat Test - PGP Tool v4.2.0")
        self.root.geometry("900x700")
        
        # Initialize PGP handler (simplified for testing)
        self.pgp_handler = None
        self.secure_chat = None
        
        self.create_interface()
        
    def create_interface(self):
        """Create the test interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # PGP Setup section
        self.create_pgp_setup_section(main_frame)
        
        # IRC Connection section
        self.create_connection_section(main_frame)
        
        # Contacts section
        self.create_contacts_section(main_frame)
        
        # Message section
        self.create_message_section(main_frame)
        
        # Chat section
        self.create_chat_section(main_frame)
        
    def create_pgp_setup_section(self, parent):
        """Create PGP setup controls"""
        pgp_frame = ttk.LabelFrame(parent, text="PGP Setup", padding="5")
        pgp_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        pgp_frame.columnconfigure(1, weight=1)
        
        # PGP directory
        ttk.Label(pgp_frame, text="PGP Directory:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.pgp_dir_var = tk.StringVar(value="./test_pgp_data")
        self.pgp_dir_entry = ttk.Entry(pgp_frame, textvariable=self.pgp_dir_var)
        self.pgp_dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Initialize PGP button
        self.init_pgp_button = ttk.Button(
            pgp_frame, 
            text="Initialize PGP", 
            command=self.initialize_pgp
        )
        self.init_pgp_button.grid(row=0, column=2)
        
        # PGP status
        self.pgp_status_label = ttk.Label(pgp_frame, text="PGP: Not initialized", foreground="red")
        self.pgp_status_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
    def create_connection_section(self, parent):
        """Create IRC connection controls"""
        conn_frame = ttk.LabelFrame(parent, text="IRC Connection", padding="5")
        conn_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        conn_frame.columnconfigure(1, weight=1)
        
        # Network and nickname
        ttk.Label(conn_frame, text="Network:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.network_var = tk.StringVar(value="libera")
        self.network_combo = ttk.Combobox(
            conn_frame, 
            textvariable=self.network_var,
            values=["libera", "oftc", "efnet"],
            state="readonly",
            width=15
        )
        self.network_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        ttk.Label(conn_frame, text="Nickname:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        self.nickname_var = tk.StringVar()
        self.nickname_entry = ttk.Entry(conn_frame, textvariable=self.nickname_var, width=15)
        self.nickname_entry.grid(row=0, column=3, sticky=tk.W, padx=(0, 10))
        
        # Connect button
        self.connect_button = ttk.Button(
            conn_frame, 
            text="Connect", 
            command=self.toggle_connection,
            state="disabled"
        )
        self.connect_button.grid(row=0, column=4)
        
        # Status
        self.irc_status_label = ttk.Label(conn_frame, text="IRC: Disconnected", foreground="red")
        self.irc_status_label.grid(row=1, column=0, columnspan=5, sticky=tk.W, pady=(5, 0))
        
    def create_contacts_section(self, parent):
        """Create contacts management"""
        contacts_frame = ttk.LabelFrame(parent, text="Secure Contacts", padding="5")
        contacts_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        contacts_frame.columnconfigure(1, weight=1)
        
        # Add contact controls - Row 1
        ttk.Label(contacts_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.contact_name_var = tk.StringVar()
        ttk.Entry(contacts_frame, textvariable=self.contact_name_var, width=15).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Label(contacts_frame, text="IRC Nickname:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        self.contact_nick_var = tk.StringVar()
        ttk.Entry(contacts_frame, textvariable=self.contact_nick_var, width=15).grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Method selection - Row 2
        method_frame = ttk.Frame(contacts_frame)
        method_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.contact_method_var = tk.StringVar(value="fingerprint")
        ttk.Radiobutton(
            method_frame, 
            text="Use Fingerprint", 
            variable=self.contact_method_var, 
            value="fingerprint",
            command=self.toggle_contact_method
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Radiobutton(
            method_frame, 
            text="Import Public Key", 
            variable=self.contact_method_var, 
            value="public_key",
            command=self.toggle_contact_method
        ).pack(side=tk.LEFT)
        
        # Fingerprint input - Row 3
        self.fingerprint_frame = ttk.Frame(contacts_frame)
        self.fingerprint_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Label(self.fingerprint_frame, text="PGP Fingerprint:").pack(side=tk.LEFT, padx=(0, 5))
        self.contact_fingerprint_var = tk.StringVar()
        fingerprint_entry = ttk.Entry(self.fingerprint_frame, textvariable=self.contact_fingerprint_var, width=40)
        fingerprint_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Public key input - Row 3 (alternative)
        self.public_key_frame = ttk.Frame(contacts_frame)
        self.public_key_frame.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Label(self.public_key_frame, text="Public Key:").grid(row=0, column=0, sticky=(tk.W, tk.N), padx=(0, 5))
        self.contact_public_key_text = scrolledtext.ScrolledText(
            self.public_key_frame, 
            height=6, 
            width=60,
            wrap=tk.WORD
        )
        self.contact_public_key_text.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.public_key_frame.columnconfigure(1, weight=1)
        
        # Paste button for public key
        ttk.Button(
            self.public_key_frame, 
            text="Paste from Clipboard", 
            command=self.paste_public_key
        ).grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
        
        # Add contact button - Row 4
        button_frame = ttk.Frame(contacts_frame)
        button_frame.grid(row=4, column=0, columnspan=4, pady=(10, 0))
        
        ttk.Button(button_frame, text="Add Contact", command=self.add_contact).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Clear Fields", command=self.clear_contact_fields).pack(side=tk.LEFT)
        
        # Contacts list - Row 5
        ttk.Label(contacts_frame, text="Added Contacts:").grid(row=5, column=0, columnspan=4, sticky=tk.W, pady=(10, 5))
        self.contacts_listbox = tk.Listbox(contacts_frame, height=4)
        self.contacts_listbox.grid(row=6, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Initially hide public key frame
        self.toggle_contact_method()
        
    def toggle_contact_method(self):
        """Toggle between fingerprint and public key input methods"""
        if self.contact_method_var.get() == "fingerprint":
            self.fingerprint_frame.grid()
            self.public_key_frame.grid_remove()
        else:
            self.fingerprint_frame.grid_remove()
            self.public_key_frame.grid()
            
    def paste_public_key(self):
        """Paste public key from clipboard"""
        try:
            clipboard_content = self.root.clipboard_get()
            if clipboard_content:
                self.contact_public_key_text.delete(1.0, tk.END)
                self.contact_public_key_text.insert(tk.END, clipboard_content)
                messagebox.showinfo("Success", f"Pasted {len(clipboard_content)} characters from clipboard")
            else:
                messagebox.showwarning("Warning", "Clipboard is empty")
        except tk.TclError:
            messagebox.showerror("Error", "Failed to access clipboard")
            
    def clear_contact_fields(self):
        """Clear all contact input fields"""
        self.contact_name_var.set("")
        self.contact_nick_var.set("")
        self.contact_fingerprint_var.set("")
        self.contact_public_key_text.delete(1.0, tk.END)
        
    def create_message_section(self, parent):
        """Create message sending controls"""
        msg_frame = ttk.LabelFrame(parent, text="Send Secure Message", padding="5")
        msg_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        msg_frame.columnconfigure(1, weight=1)
        
        # Target and message
        ttk.Label(msg_frame, text="To:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.target_var = tk.StringVar()
        self.target_combo = ttk.Combobox(msg_frame, textvariable=self.target_var, width=20)
        self.target_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        ttk.Label(msg_frame, text="Message:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        self.message_var = tk.StringVar()
        self.message_entry = ttk.Entry(msg_frame, textvariable=self.message_var)
        self.message_entry.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(0, 10))
        self.message_entry.bind('<Return>', lambda e: self.send_secure_message())
        
        # Send button
        self.send_button = ttk.Button(
            msg_frame, 
            text="Send Encrypted", 
            command=self.send_secure_message,
            state="disabled"
        )
        self.send_button.grid(row=0, column=4)
        
    def create_chat_section(self, parent):
        """Create chat display"""
        chat_frame = ttk.LabelFrame(parent, text="Secure Chat Log", padding="5")
        chat_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        # Chat text area
        self.chat_text = scrolledtext.ScrolledText(
            chat_frame, 
            wrap=tk.WORD, 
            height=15,
            state=tk.DISABLED
        )
        self.chat_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Controls
        controls_frame = ttk.Frame(chat_frame)
        controls_frame.grid(row=1, column=0, pady=(5, 0))
        
        ttk.Button(controls_frame, text="Clear Log", command=self.clear_chat).pack(side=tk.LEFT, padx=(0, 10))
        
        # History saving checkbox
        self.save_history_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            controls_frame, 
            text="Save Chat History", 
            variable=self.save_history_var,
            command=self.toggle_history_saving
        ).pack(side=tk.LEFT)
        
    def initialize_pgp(self):
        """Initialize PGP handler"""
        try:
            pgp_dir = self.pgp_dir_var.get()
            if not pgp_dir:
                messagebox.showerror("Error", "Please enter PGP directory")
                return
                
            # Create directory if it doesn't exist
            os.makedirs(pgp_dir, exist_ok=True)
            
            # Initialize PGP handler
            self.pgp_handler = PGPHandler(pgp_dir)
            
            # Initialize secure chat
            self.secure_chat = SecureChatHandler(self.pgp_handler)
            self.setup_secure_chat_callbacks()
            
            # Update UI
            self.pgp_status_label.config(text="PGP: Initialized", foreground="green")
            self.connect_button.config(state="normal")
            
            self.log_message("SYSTEM", "PGP handler initialized successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize PGP: {str(e)}")
            
    def setup_secure_chat_callbacks(self):
        """Setup secure chat callbacks"""
        self.secure_chat.set_message_callback(self.on_secure_message)
        self.secure_chat.set_error_callback(self.on_secure_error)
        
    def toggle_connection(self):
        """Connect or disconnect from IRC"""
        if not self.secure_chat:
            messagebox.showerror("Error", "Please initialize PGP first")
            return
            
        if self.secure_chat.is_connected():
            self.disconnect_irc()
        else:
            self.connect_irc()
            
    def connect_irc(self):
        """Connect to IRC"""
        network = self.network_var.get()
        nickname = self.nickname_var.get().strip()
        
        if not nickname:
            nickname = f"PGPTest_{os.urandom(3).hex().upper()}"
            self.nickname_var.set(nickname)
            
        self.log_message("SYSTEM", f"Connecting to {network} as {nickname}...")
        
        try:
            success = self.secure_chat.connect_to_irc(network, nickname)
            if success:
                self.irc_status_label.config(text=f"IRC: Connected to {network}", foreground="green")
                self.connect_button.config(text="Disconnect")
                self.send_button.config(state="normal")
            else:
                self.log_message("ERROR", "Failed to connect to IRC")
        except Exception as e:
            self.log_message("ERROR", f"Connection error: {str(e)}")
            
    def disconnect_irc(self):
        """Disconnect from IRC"""
        self.log_message("SYSTEM", "Disconnecting...")
        self.secure_chat.disconnect_from_irc()
        self.irc_status_label.config(text="IRC: Disconnected", foreground="red")
        self.connect_button.config(text="Connect")
        self.send_button.config(state="disabled")
        
    def add_contact(self):
        """Add a secure contact"""
        if not self.secure_chat:
            messagebox.showerror("Error", "Please initialize PGP first")
            return
            
        name = self.contact_name_var.get().strip()
        nick = self.contact_nick_var.get().strip()
        
        if not all([name, nick]):
            messagebox.showerror("Error", "Please enter name and IRC nickname")
            return
            
        try:
            if self.contact_method_var.get() == "fingerprint":
                # Use fingerprint method
                fingerprint = self.contact_fingerprint_var.get().strip()
                if not fingerprint:
                    messagebox.showerror("Error", "Please enter PGP fingerprint")
                    return
                    
                contact = self.secure_chat.add_contact(name, nick, pgp_fingerprint=fingerprint)
                method_info = f"Fingerprint: {fingerprint[:16]}..."
                
            else:
                # Use public key method
                public_key = self.contact_public_key_text.get(1.0, tk.END).strip()
                if not public_key:
                    messagebox.showerror("Error", "Please enter public key")
                    return
                    
                if "-----BEGIN PGP PUBLIC KEY BLOCK-----" not in public_key:
                    messagebox.showerror("Error", "Invalid public key format")
                    return
                    
                contact = self.secure_chat.add_contact(name, nick, public_key=public_key)
                method_info = f"Key imported: {contact.pgp_fingerprint[:16]}..."
            
            # Update UI
            self.contacts_listbox.insert(tk.END, f"{name} ({nick}) - {method_info}")
            self.target_combo['values'] = [contact.irc_nickname for contact in self.secure_chat.get_contacts_list()]
            
            # Clear fields
            self.clear_contact_fields()
            
            self.log_message("SYSTEM", f"Added contact: {name} ({nick}) - {method_info}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add contact: {str(e)}")
            
    def send_secure_message(self):
        """Send a secure message"""
        if not self.secure_chat or not self.secure_chat.is_connected():
            messagebox.showerror("Error", "Not connected to IRC")
            return
            
        target = self.target_var.get().strip()
        message = self.message_var.get().strip()
        
        if not target or not message:
            messagebox.showerror("Error", "Please enter target and message")
            return
            
        try:
            chat_message = self.secure_chat.send_secure_message(target, message)
            self.log_secure_message("SENT", chat_message)
            self.message_var.set("")  # Clear message field
        except Exception as e:
            self.log_message("ERROR", f"Failed to send message: {str(e)}")
            
    def toggle_history_saving(self):
        """Toggle chat history saving"""
        if self.secure_chat:
            self.secure_chat.set_history_saving(self.save_history_var.get())
            
    def clear_chat(self):
        """Clear chat log"""
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.delete(1.0, tk.END)
        self.chat_text.config(state=tk.DISABLED)
        
    def log_message(self, sender, message):
        """Add message to chat log"""
        self.chat_text.config(state=tk.NORMAL)
        timestamp = tk.datetime.datetime.now().strftime("%H:%M:%S")
        self.chat_text.insert(tk.END, f"[{timestamp}] {sender}: {message}\n")
        self.chat_text.see(tk.END)
        self.chat_text.config(state=tk.DISABLED)
        
    def log_secure_message(self, direction, chat_message: SecureChatMessage):
        """Log a secure chat message"""
        self.chat_text.config(state=tk.NORMAL)
        timestamp = tk.datetime.datetime.fromtimestamp(chat_message.timestamp).strftime("%H:%M:%S")
        
        if direction == "SENT":
            prefix = f"🔒 TO {chat_message.recipient}"
        else:
            prefix = f"🔒 FROM {chat_message.sender}"
            
        if chat_message.verified:
            prefix += " ✅"
        elif chat_message.encrypted:
            prefix += " 🔐"
            
        self.chat_text.insert(tk.END, f"[{timestamp}] {prefix}: {chat_message.content}\n")
        self.chat_text.see(tk.END)
        self.chat_text.config(state=tk.DISABLED)
        
    # Secure chat callbacks
    def on_secure_message(self, chat_message: SecureChatMessage):
        """Handle incoming secure message"""
        self.log_secure_message("RECEIVED", chat_message)
        
    def on_secure_error(self, error: str):
        """Handle secure chat error"""
        self.log_message("ERROR", error)
        
    def run(self):
        """Start the test interface"""
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start GUI
        self.root.mainloop()
        
    def on_closing(self):
        """Handle window closing"""
        if self.secure_chat and self.secure_chat.is_connected():
            self.secure_chat.disconnect_from_irc()
        self.root.destroy()


def main():
    """Run secure chat test"""
    import datetime
    
    # Fix datetime import for log_message
    tk.datetime = datetime
    
    print("Starting Secure Chat Test...")
    app = SecureChatTestWindow()
    app.run()


if __name__ == "__main__":
    main()

