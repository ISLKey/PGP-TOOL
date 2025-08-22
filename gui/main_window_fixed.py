"""
Main Window GUI Module - FIXED VERSION
Creates the main application window with tabbed interface
Fixed chat system integration and profile selector functionality
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import time
import uuid
import random
import string
from typing import Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import *
from crypto.key_generator import SecureKeyGenerator

# Try to import secure chat, but don't fail if it's not available
try:
    from chat.secure_chat import SecureChatHandler
    SECURE_CHAT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Secure chat not available: {e}")
    SECURE_CHAT_AVAILABLE = False
    SecureChatHandler = None

class PGPToolMainWindow:
    """Main application window"""
    
    def __init__(self):
        """Initialize the main window"""
        self.root = tk.Tk()
        
        # Hide the window initially until authentication
        self.root.withdraw()
        
        self.setup_window()
        self.setup_styles()
        self.create_menu()
        self.create_main_interface()
        
        # Initialize crypto backend
        self.key_generator = SecureKeyGenerator(
            gnupg_home=os.path.join(DATA_DIR, "gnupg")
        )
        
        # Initialize message history data
        self.message_history_data = {}
        
        # Application state
        self.current_keys = []
        self.current_messages = []
        
        # Chat system initialization
        self.chat_profiles = []
        self.selected_chat_profile = None
        self.secure_chat = None
        self.group_chat = None
        self.chat_contacts = {}  # nickname -> contact info
        
    def setup_window(self):
        """Configure the main window"""
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        
        # Center the window
        self.center_window()
        
        # Set window icon (if available)
        try:
            # You can add an icon file here
            pass
        except:
            pass
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def setup_styles(self):
        """Configure GUI styles"""
        style = ttk.Style()
        
        # Configure notebook (tab) style
        style.configure('TNotebook', background=COLORS['background'])
        style.configure('TNotebook.Tab', padding=[20, 10])
        
        # Configure button styles with solid backgrounds
        style.configure('Action.TButton', 
                       font=('Arial', 10, 'bold'),
                       padding=(10, 8))  # Added padding for better button size
        
        # Danger button (red) - for burn message
        style.configure('Danger.TButton', 
                       font=('Arial', 10, 'bold'),
                       foreground='white',
                       background='#dc3545',
                       padding=(10, 8))
        
        # Success button (green)
        style.configure('Success.TButton', 
                       font=('Arial', 10, 'bold'),
                       foreground='white', 
                       background='#28a745',
                       padding=(10, 8))
        
        # Warning button (orange)
        style.configure('Warning.TButton', 
                       font=('Arial', 10, 'bold'),
                       foreground='white',
                       background='#fd7e14',
                       padding=(10, 8))
        
        # Configure treeview style
        style.configure('Treeview', font=('Arial', 9))
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
    
    def create_menu(self):
        """Create the application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Generate New Key Pair...", command=self.generate_key_dialog)
        file_menu.add_command(label="Import Key...", command=self.import_key_dialog)
        file_menu.add_command(label="Export Keys...", command=self.export_keys_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Secure Delete Files...", command=self.secure_delete_dialog)
        tools_menu.add_command(label="Key Management...", command=self.key_management_dialog)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about_dialog)
    
    def create_main_interface(self):
        """Create the main tabbed interface"""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create tabs
        self.create_keys_tab()
        self.create_contacts_tab()
        self.create_messages_tab()
        
        # Only create chat tab if secure chat is available
        if SECURE_CHAT_AVAILABLE:
            self.create_chat_tab()
        else:
            print("Secure chat not available - skipping chat tab")
        
        # Status bar
        self.create_status_bar(main_frame)
    
    def create_keys_tab(self):
        """Create the keys management tab"""
        keys_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(keys_frame, text="🔑 Keys")
        
        # Configure grid
        keys_frame.columnconfigure(1, weight=1)
        keys_frame.rowconfigure(1, weight=1)
        
        # Left panel - Key actions
        left_panel = ttk.LabelFrame(keys_frame, text="Key Actions", padding="10")
        left_panel.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Generate new key button
        ttk.Button(
            left_panel, 
            text="Generate New Key Pair", 
            command=self.generate_key_dialog,
            style='Action.TButton'
        ).pack(fill=tk.X, pady=(0, 5))
        
        # Import key button
        ttk.Button(
            left_panel, 
            text="Import Key", 
            command=self.import_key_dialog,
            style='Action.TButton'
        ).pack(fill=tk.X, pady=(0, 5))
        
        # Export keys button
        ttk.Button(
            left_panel, 
            text="Export Keys", 
            command=self.export_keys_dialog,
            style='Action.TButton'
        ).pack(fill=tk.X, pady=(0, 5))
        
        # Export as Contact Card button
        ttk.Button(
            left_panel, 
            text="Export as Contact Card", 
            command=self.export_key_as_contact_card,
            style='Action.TButton'
        ).pack(fill=tk.X, pady=(0, 10))
        
        # Separator
        ttk.Separator(left_panel, orient='horizontal').pack(fill=tk.X, pady=(0, 10))
        
        # Delete key button (danger style)
        ttk.Button(
            left_panel, 
            text="Delete Selected Key", 
            command=self.delete_selected_key,
            style='Danger.TButton'
        ).pack(fill=tk.X, pady=(0, 5))
        
        # Key info frame
        info_frame = ttk.LabelFrame(left_panel, text="Key Information", padding="5")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.key_info_text = tk.Text(info_frame, height=8, wrap=tk.WORD, state=tk.DISABLED, font=('Consolas', 9))
        self.key_info_text.pack(fill=tk.BOTH, expand=True)
        
        # Right panel - Keys list
        right_panel = ttk.LabelFrame(keys_frame, text="Key Management", padding="10")
        right_panel.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)
        
        # Keys list header
        ttk.Label(right_panel, text="Your Keys", font=('Arial', 12, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 10)
        )
        
        # Keys tree
        self.key_tree = ttk.Treeview(
            right_panel,
            columns=('Type', 'Name', 'Email', 'Key ID', 'Created'),
            show='tree headings'
        )
        
        # Configure columns
        self.key_tree.heading('#0', text='')
        self.key_tree.heading('Type', text='Type')
        self.key_tree.heading('Name', text='Name')
        self.key_tree.heading('Email', text='Email')
        self.key_tree.heading('Key ID', text='Key ID')
        self.key_tree.heading('Created', text='Created')
        
        self.key_tree.column('#0', width=30)
        self.key_tree.column('Type', width=80)
        self.key_tree.column('Name', width=150)
        self.key_tree.column('Email', width=200)
        self.key_tree.column('Key ID', width=100)
        self.key_tree.column('Created', width=100)
        
        # Bind selection event
        self.key_tree.bind('<<TreeviewSelect>>', self.on_key_selected)
        
        # Scrollbars
        key_v_scroll = ttk.Scrollbar(right_panel, orient="vertical", command=self.key_tree.yview)
        key_h_scroll = ttk.Scrollbar(right_panel, orient="horizontal", command=self.key_tree.xview)
        self.key_tree.configure(yscrollcommand=key_v_scroll.set, xscrollcommand=key_h_scroll.set)
        
        # Grid keys tree
        self.key_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        key_v_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        key_h_scroll.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        # Key count label
        self.key_count_var = tk.StringVar()
        self.key_count_var.set("Keys: 0")
        ttk.Label(right_panel, textvariable=self.key_count_var, font=('Arial', 9)).grid(
            row=3, column=0, sticky=tk.W, pady=(5, 0)
        )
    
    def create_contacts_tab(self):
        """Create the contacts management tab"""
        contacts_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(contacts_frame, text="👥 Contacts")
        
        # Configure grid
        contacts_frame.columnconfigure(1, weight=1)
        contacts_frame.rowconfigure(1, weight=1)
        
        # Left panel - Contact actions
        left_panel = ttk.LabelFrame(contacts_frame, text="Contact Actions", padding="10")
        left_panel.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Add contact button
        ttk.Button(
            left_panel, 
            text="Add Contact", 
            command=self.add_contact_dialog,
            style='Action.TButton'
        ).pack(fill=tk.X, pady=(0, 5))
        
        # Import contact card button
        ttk.Button(
            left_panel, 
            text="Import Contact Card", 
            command=self.import_contact_card_dialog,
            style='Action.TButton'
        ).pack(fill=tk.X, pady=(0, 5))
        
        # Export contact card button
        ttk.Button(
            left_panel, 
            text="Export Contact Card", 
            command=self.export_contact_card,
            style='Action.TButton'
        ).pack(fill=tk.X, pady=(0, 5))
        
        # Import public key button
        ttk.Button(
            left_panel, 
            text="Import Public Key", 
            command=self.import_contact_key,
            style='Action.TButton'
        ).pack(fill=tk.X, pady=(0, 10))
        
        # Separator
        ttk.Separator(left_panel, orient='horizontal').pack(fill=tk.X, pady=(0, 10))
        
        # Remove contact button
        ttk.Button(
            left_panel, 
            text="Remove Contact", 
            command=self.remove_contact,
            style='Warning.TButton'
        ).pack(fill=tk.X, pady=(0, 5))
        
        # Delete contact and key button (danger style)
        ttk.Button(
            left_panel, 
            text="Delete Contact & Key", 
            command=self.delete_contact_with_key,
            style='Danger.TButton'
        ).pack(fill=tk.X, pady=(0, 5))
        
        # Contact info frame
        info_frame = ttk.LabelFrame(left_panel, text="Contact Information", padding="5")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.contact_info_text = tk.Text(info_frame, height=8, wrap=tk.WORD, state=tk.DISABLED, font=('Consolas', 9))
        self.contact_info_text.pack(fill=tk.BOTH, expand=True)
        
        # Right panel - Contacts list
        right_panel = ttk.LabelFrame(contacts_frame, text="Contact Management", padding="10")
        right_panel.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)
        
        # Contacts list header
        ttk.Label(right_panel, text="Your Contacts", font=('Arial', 12, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 10)
        )
        
        # Contacts tree
        self.contacts_tree = ttk.Treeview(
            right_panel,
            columns=('Name', 'Key ID', 'IRC Nick', 'Added'),
            show='tree headings'
        )
        
        # Configure columns
        self.contacts_tree.heading('#0', text='')
        self.contacts_tree.heading('Name', text='Name')
        self.contacts_tree.heading('Key ID', text='Key ID')
        self.contacts_tree.heading('IRC Nick', text='IRC Nickname')
        self.contacts_tree.heading('Added', text='Added')
        
        self.contacts_tree.column('#0', width=30)
        self.contacts_tree.column('Name', width=150)
        self.contacts_tree.column('Key ID', width=100)
        self.contacts_tree.column('IRC Nick', width=120)
        self.contacts_tree.column('Added', width=100)
        
        # Bind selection event
        self.contacts_tree.bind('<<TreeviewSelect>>', self.on_contact_selected)
        
        # Scrollbars
        contact_v_scroll = ttk.Scrollbar(right_panel, orient="vertical", command=self.contacts_tree.yview)
        contact_h_scroll = ttk.Scrollbar(right_panel, orient="horizontal", command=self.contacts_tree.xview)
        self.contacts_tree.configure(yscrollcommand=contact_v_scroll.set, xscrollcommand=contact_h_scroll.set)
        
        # Grid contacts tree
        self.contacts_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        contact_v_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        contact_h_scroll.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        # Contact count label
        self.contact_count_var = tk.StringVar()
        self.contact_count_var.set("Contacts: 0")
        ttk.Label(right_panel, textvariable=self.contact_count_var, font=('Arial', 9)).grid(
            row=3, column=0, sticky=tk.W, pady=(5, 0)
        )
    
    def create_messages_tab(self):
        """Create the messages tab for encryption/decryption"""
        messages_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(messages_frame, text="📧 Messages")
        
        # Configure grid
        messages_frame.columnconfigure(0, weight=1)
        messages_frame.rowconfigure(0, weight=1)
        
        # Create paned window for message interface and history
        main_paned = ttk.PanedWindow(messages_frame, orient=tk.HORIZONTAL)
        main_paned.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Left frame for message composition/decryption
        message_frame = ttk.Frame(main_paned)
        main_paned.add(message_frame, weight=2)
        
        # Configure grid for message frame
        message_frame.columnconfigure(0, weight=1)
        message_frame.rowconfigure(1, weight=1)
        
        # Message controls
        controls_frame = ttk.Frame(message_frame)
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        controls_frame.columnconfigure(2, weight=1)
        
        # Recipient selection
        ttk.Label(controls_frame, text="Recipient:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.recipient_var = tk.StringVar()
        self.recipient_combo = ttk.Combobox(controls_frame, textvariable=self.recipient_var, 
                                          state="readonly", width=25)
        self.recipient_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        # Burn after reading checkbox
        self.burn_message_var = tk.BooleanVar()
        ttk.Checkbutton(controls_frame, text="🔥 Burn after reading", 
                       variable=self.burn_message_var).grid(row=0, column=2, sticky=tk.E)
        
        # Message interface with tabs
        message_notebook = ttk.Notebook(message_frame)
        message_notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Compose tab
        compose_frame = ttk.Frame(message_notebook, padding="10")
        message_notebook.add(compose_frame, text="📝 Compose")
        compose_frame.columnconfigure(0, weight=1)
        compose_frame.rowconfigure(1, weight=1)
        
        # Message input
        ttk.Label(compose_frame, text="Message:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        self.message_text = tk.Text(compose_frame, height=10, wrap=tk.WORD, font=('Arial', 11))
        self.message_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Message scrollbar
        message_scroll = ttk.Scrollbar(compose_frame, orient="vertical", command=self.message_text.yview)
        message_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.message_text.configure(yscrollcommand=message_scroll.set)
        
        # Compose buttons
        compose_buttons_frame = ttk.Frame(compose_frame)
        compose_buttons_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(compose_buttons_frame, text="Encrypt Message", 
                  command=self.encrypt_message, style='Success.TButton').pack(side=tk.LEFT)
        ttk.Button(compose_buttons_frame, text="Clear", 
                  command=lambda: self.message_text.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=(10, 0))
        
        # Decrypt tab
        decrypt_frame = ttk.Frame(message_notebook, padding="10")
        message_notebook.add(decrypt_frame, text="🔓 Decrypt")
        decrypt_frame.columnconfigure(0, weight=1)
        decrypt_frame.rowconfigure(1, weight=1)
        decrypt_frame.rowconfigure(3, weight=1)
        
        # Encrypted message input
        ttk.Label(decrypt_frame, text="Encrypted Message:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        self.encrypted_text = tk.Text(decrypt_frame, height=8, wrap=tk.WORD, font=('Consolas', 10))
        self.encrypted_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Encrypted message scrollbar
        encrypted_scroll = ttk.Scrollbar(decrypt_frame, orient="vertical", command=self.encrypted_text.yview)
        encrypted_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.encrypted_text.configure(yscrollcommand=encrypted_scroll.set)
        
        # Decrypt buttons
        decrypt_buttons_frame = ttk.Frame(decrypt_frame)
        decrypt_buttons_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(decrypt_buttons_frame, text="Decrypt Message", 
                  command=self.decrypt_message, style='Action.TButton').pack(side=tk.LEFT)
        ttk.Button(decrypt_buttons_frame, text="Paste from Clipboard", 
                  command=self.paste_encrypted_message).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(decrypt_buttons_frame, text="Clear", 
                  command=lambda: self.encrypted_text.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=(10, 0))
        
        # Decrypted message output
        ttk.Label(decrypt_frame, text="Decrypted Message:", font=('Arial', 10, 'bold')).grid(
            row=3, column=0, sticky=tk.W, pady=(10, 5)
        )
        
        self.decrypted_text = tk.Text(decrypt_frame, height=8, wrap=tk.WORD, font=('Arial', 11), 
                                    state=tk.DISABLED, bg='#f8f9fa')
        self.decrypted_text.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Decrypted message scrollbar
        decrypted_scroll = ttk.Scrollbar(decrypt_frame, orient="vertical", command=self.decrypted_text.yview)
        decrypted_scroll.grid(row=4, column=1, sticky=(tk.N, tk.S))
        self.decrypted_text.configure(yscrollcommand=decrypted_scroll.set)
        
        # Right frame for message history
        history_frame = ttk.LabelFrame(main_paned, text="Message History", padding="10")
        main_paned.add(history_frame, weight=1)
        
        # Configure grid for history frame
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        
        # Create paned window for history list and message viewer
        history_paned = ttk.PanedWindow(history_frame, orient=tk.VERTICAL)
        history_paned.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Top frame for history list
        history_list_frame = ttk.Frame(history_paned)
        history_paned.add(history_list_frame, weight=1)
        
        # Configure grid for list frame
        history_list_frame.columnconfigure(0, weight=1)
        history_list_frame.rowconfigure(1, weight=1)
        
        # History list label
        ttk.Label(history_list_frame, text="Message History", font=('Arial', 12, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        # Message history list
        self.history_tree = ttk.Treeview(
            history_list_frame,
            columns=('Type', 'Subject', 'Recipient', 'Date', 'ID'),
            show='tree headings'
        )
        
        # Configure columns
        self.history_tree.heading('#0', text='')
        self.history_tree.heading('Type', text='Type')
        self.history_tree.heading('Subject', text='Subject')
        self.history_tree.heading('Recipient', text='Recipient/Sender')
        self.history_tree.heading('Date', text='Date')
        self.history_tree.heading('ID', text='')  # Hidden column for message ID
        
        self.history_tree.column('#0', width=30)
        self.history_tree.column('Type', width=80)
        self.history_tree.column('Subject', width=200)
        self.history_tree.column('Recipient', width=200)
        self.history_tree.column('Date', width=120)
        self.history_tree.column('ID', width=0, stretch=False)  # Hidden
        
        # Bind selection event
        self.history_tree.bind('<<TreeviewSelect>>', self.on_history_selected)
        self.history_tree.bind('<Double-1>', self.on_history_double_click)
        
        # Scrollbars for history list
        history_v_scroll = ttk.Scrollbar(history_list_frame, orient="vertical", command=self.history_tree.yview)
        history_h_scroll = ttk.Scrollbar(history_list_frame, orient="horizontal", command=self.history_tree.xview)
        self.history_tree.configure(yscrollcommand=history_v_scroll.set, xscrollcommand=history_h_scroll.set)
        
        # Grid history list
        self.history_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        history_v_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        history_h_scroll.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        # Bottom frame for message viewer
        message_viewer_frame = ttk.Frame(history_paned)
        history_paned.add(message_viewer_frame, weight=1)
        
        # Configure grid for viewer frame
        message_viewer_frame.columnconfigure(0, weight=1)
        message_viewer_frame.rowconfigure(1, weight=1)
        
        # Message viewer label
        self.history_message_label = ttk.Label(
            message_viewer_frame, 
            text="Select a message from the history to view its content", 
            font=('Arial', 12, 'bold')
        )
        self.history_message_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Message content viewer
        self.history_message_text = tk.Text(
            message_viewer_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            state=tk.DISABLED,
            bg='#f8f9fa',
            relief=tk.SUNKEN,
            borderwidth=2
        )
        
        # Scrollbars for message viewer
        message_v_scroll = ttk.Scrollbar(message_viewer_frame, orient="vertical", command=self.history_message_text.yview)
        message_h_scroll = ttk.Scrollbar(message_viewer_frame, orient="horizontal", command=self.history_message_text.xview)
        self.history_message_text.configure(yscrollcommand=message_v_scroll.set, xscrollcommand=message_h_scroll.set)
        
        # Grid message viewer
        self.history_message_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        message_v_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        message_h_scroll.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        # Initialize message storage
        self.message_history_data = {}
    
    def create_chat_tab(self):
        """Create the secure chat tab - FIXED VERSION"""
        if not SECURE_CHAT_AVAILABLE:
            print("Secure chat not available - cannot create chat tab")
            return
            
        chat_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(chat_frame, text="💬 Chat")
        
        # Configure grid
        chat_frame.columnconfigure(1, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        # Left panel - Chat controls
        left_panel = ttk.LabelFrame(chat_frame, text="Chat Controls", padding="10")
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_panel.columnconfigure(0, weight=1)
        
        # IRC Connection section
        irc_frame = ttk.LabelFrame(left_panel, text="IRC Connection", padding="5")
        irc_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        irc_frame.columnconfigure(1, weight=1)
        
        # Network selection
        ttk.Label(irc_frame, text="Network:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.chat_network_var = tk.StringVar(value="libera")
        network_combo = ttk.Combobox(irc_frame, textvariable=self.chat_network_var, 
                                   values=["libera", "oftc", "efnet"], state="readonly", width=15)
        network_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        # Connect/Disconnect button
        self.chat_connect_button = ttk.Button(irc_frame, text="Connect", 
                                            command=self.toggle_chat_connection, width=12)
        self.chat_connect_button.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Connection status
        self.chat_status_var = tk.StringVar(value="Disconnected")
        self.chat_status_label = ttk.Label(irc_frame, textvariable=self.chat_status_var, 
                                         foreground="red", font=('Arial', 9))
        self.chat_status_label.grid(row=2, column=0, columnspan=2, pady=2)
        
        # Chat Settings section - FIXED
        settings_frame = ttk.LabelFrame(left_panel, text="Chat Settings", padding="5")
        settings_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)
        
        # Profile selector - FIXED
        ttk.Label(settings_frame, text="Chat Profile:").grid(row=0, column=0, sticky=tk.W)
        self.chat_profile_var = tk.StringVar()
        self.chat_profile_combo = ttk.Combobox(settings_frame, textvariable=self.chat_profile_var, 
                                             state="readonly", width=20)
        self.chat_profile_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        self.chat_profile_combo.bind('<<ComboboxSelected>>', self.on_chat_profile_changed)
        
        # IRC Nickname (auto-populated from selected profile) - FIXED
        ttk.Label(settings_frame, text="IRC Nickname:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.chat_irc_nickname_var = tk.StringVar()
        self.chat_irc_nickname_entry = ttk.Entry(settings_frame, textvariable=self.chat_irc_nickname_var, width=20)
        self.chat_irc_nickname_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=(5, 0))
        
        # Save history checkbox
        self.chat_save_history_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Save chat history", 
                       variable=self.chat_save_history_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Chat Contacts section - FIXED
        contacts_frame = ttk.LabelFrame(left_panel, text="Chat Contacts", padding="5")
        contacts_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        contacts_frame.columnconfigure(0, weight=1)
        contacts_frame.rowconfigure(2, weight=1)
        
        # Add contact button
        ttk.Button(contacts_frame, text="Add Contact", 
                  command=self.add_chat_contact_dialog, width=15).grid(row=0, column=0, pady=(0, 5))
        
        # Refresh contacts button
        ttk.Button(contacts_frame, text="Refresh Contacts", 
                  command=self.refresh_chat_contacts, width=15).grid(row=1, column=0, pady=(0, 5))
        
        # Contacts list
        self.chat_contacts_listbox = tk.Listbox(contacts_frame, height=8)
        self.chat_contacts_listbox.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.chat_contacts_listbox.bind('<Double-Button-1>', self.start_chat_with_contact)
        
        # Right panel - Chat interface with tabs
        right_panel = ttk.LabelFrame(chat_frame, text="Secure Chat", padding="10")
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)
        
        # Create notebook for private and group chat
        self.chat_notebook = ttk.Notebook(right_panel)
        self.chat_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Private Chat Tab
        private_chat_frame = ttk.Frame(self.chat_notebook, padding="10")
        self.chat_notebook.add(private_chat_frame, text="💬 Private Chat")
        private_chat_frame.columnconfigure(0, weight=1)
        private_chat_frame.rowconfigure(1, weight=1)
        
        # Chat target selection
        target_frame = ttk.Frame(private_chat_frame)
        target_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        target_frame.columnconfigure(1, weight=1)
        
        ttk.Label(target_frame, text="Chat with:").grid(row=0, column=0, sticky=tk.W)
        self.chat_target_var = tk.StringVar()
        self.chat_target_combo = ttk.Combobox(target_frame, textvariable=self.chat_target_var, 
                                            state="readonly", width=20)
        self.chat_target_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        # Chat log
        chat_log_frame = ttk.Frame(private_chat_frame)
        chat_log_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        chat_log_frame.columnconfigure(0, weight=1)
        chat_log_frame.rowconfigure(0, weight=1)
        
        self.chat_log_text = tk.Text(chat_log_frame, height=15, wrap=tk.WORD, state=tk.DISABLED)
        self.chat_log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Chat log scrollbar
        chat_scroll = ttk.Scrollbar(chat_log_frame, orient="vertical", command=self.chat_log_text.yview)
        chat_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.chat_log_text.configure(yscrollcommand=chat_scroll.set)
        
        # Message input
        input_frame = ttk.Frame(private_chat_frame)
        input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        input_frame.columnconfigure(0, weight=1)
        
        self.chat_message_var = tk.StringVar()
        self.chat_message_entry = ttk.Entry(input_frame, textvariable=self.chat_message_var)
        self.chat_message_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        self.chat_message_entry.bind('<Return>', self.send_chat_message)
        
        self.chat_send_button = ttk.Button(input_frame, text="Send Encrypted", 
                                         command=self.send_chat_message, state="disabled")
        self.chat_send_button.grid(row=0, column=1)
        
        # Group Chat Tab
        self.create_group_chat_tab()
        
        # Initialize chat system variables
        self.secure_chat = None
        self.group_chat = None
        self.chat_contacts = {}  # nickname -> contact info
    
    def create_group_chat_tab(self):
        """Create the group chat tab - FIXED VERSION"""
        group_chat_frame = ttk.Frame(self.chat_notebook, padding="10")
        self.chat_notebook.add(group_chat_frame, text="👥 Group Chat")
        group_chat_frame.columnconfigure(1, weight=1)
        group_chat_frame.rowconfigure(1, weight=1)
        
        # Left panel - Group management
        group_left_panel = ttk.LabelFrame(group_chat_frame, text="Groups", padding="5")
        group_left_panel.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        group_left_panel.columnconfigure(0, weight=1)
        group_left_panel.rowconfigure(2, weight=1)
        
        # Group controls
        group_controls_frame = ttk.Frame(group_left_panel)
        group_controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        group_controls_frame.columnconfigure(0, weight=1)
        
        ttk.Button(group_controls_frame, text="Create Group", 
                  command=self.create_group_dialog, width=15).grid(row=0, column=0, pady=2)
        ttk.Button(group_controls_frame, text="Join Group", 
                  command=self.join_group_dialog, width=15).grid(row=1, column=0, pady=2)
        ttk.Button(group_controls_frame, text="Leave Group", 
                  command=self.leave_current_group, width=15).grid(row=2, column=0, pady=2)
        
        # Current group info - FIXED with creator display
        current_group_frame = ttk.LabelFrame(group_left_panel, text="Current Group", padding="5")
        current_group_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        current_group_frame.columnconfigure(0, weight=1)
        
        self.current_group_var = tk.StringVar(value="None")
        ttk.Label(current_group_frame, textvariable=self.current_group_var, 
                 font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W)
        
        self.group_member_count_var = tk.StringVar(value="0 members")
        ttk.Label(current_group_frame, textvariable=self.group_member_count_var).grid(row=1, column=0, sticky=tk.W)
        
        # Group creator display - FIXED
        self.group_creator_var = tk.StringVar(value="")
        ttk.Label(current_group_frame, textvariable=self.group_creator_var, 
                 font=('Arial', 8), foreground='gray').grid(row=2, column=0, sticky=tk.W)
        
        # Groups list
        groups_list_frame = ttk.LabelFrame(group_left_panel, text="My Groups", padding="5")
        groups_list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        groups_list_frame.columnconfigure(0, weight=1)
        groups_list_frame.rowconfigure(0, weight=1)
        
        self.groups_listbox = tk.Listbox(groups_list_frame, height=8)
        self.groups_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.groups_listbox.bind('<Double-Button-1>', self.switch_to_group)
        self.groups_listbox.bind('<Button-3>', self.show_group_context_menu)  # Right-click
        
        # Right panel - Group chat interface
        group_right_panel = ttk.Frame(group_chat_frame)
        group_right_panel.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        group_right_panel.columnconfigure(0, weight=1)
        group_right_panel.rowconfigure(1, weight=1)
        
        # Group chat header
        group_header_frame = ttk.Frame(group_right_panel)
        group_header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        group_header_frame.columnconfigure(0, weight=1)
        
        self.group_chat_title_var = tk.StringVar(value="Select a group to start chatting")
        ttk.Label(group_header_frame, textvariable=self.group_chat_title_var, 
                 font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky=tk.W)
        
        ttk.Button(group_header_frame, text="Manage Members", 
                  command=self.manage_group_members_dialog, width=15).grid(row=0, column=1)
        
        # Group chat log
        group_chat_log_frame = ttk.Frame(group_right_panel)
        group_chat_log_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        group_chat_log_frame.columnconfigure(0, weight=1)
        group_chat_log_frame.rowconfigure(0, weight=1)
        
        self.group_chat_log_text = tk.Text(group_chat_log_frame, height=15, wrap=tk.WORD, state=tk.DISABLED)
        self.group_chat_log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Group chat log scrollbar
        group_chat_scroll = ttk.Scrollbar(group_chat_log_frame, orient="vertical", command=self.group_chat_log_text.yview)
        group_chat_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.group_chat_log_text.configure(yscrollcommand=group_chat_scroll.set)
        
        # Group message input
        group_input_frame = ttk.Frame(group_right_panel)
        group_input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        group_input_frame.columnconfigure(0, weight=1)
        
        self.group_message_var = tk.StringVar()
        self.group_message_entry = ttk.Entry(group_input_frame, textvariable=self.group_message_var)
        self.group_message_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        self.group_message_entry.bind('<Return>', self.send_group_message)
        
        self.group_send_button = ttk.Button(group_input_frame, text="Send to Group", 
                                          command=self.send_group_message, state="disabled")
        self.group_send_button.grid(row=0, column=1)
    
    def create_status_bar(self, parent):
        """Create the status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(1, weight=1)
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        ttk.Label(status_frame, textvariable=self.status_var).grid(row=0, column=0, sticky=tk.W)
        
        # Emergency Kill Switch button (prominent)
        kill_button = tk.Button(
            status_frame, 
            text="🚨 EMERGENCY KILL", 
            command=self.emergency_kill_switch,
            bg="#dc3545",  # Red background
            fg="white",    # White text
            font=("Arial", 9, "bold"),
            relief=tk.RAISED,
            bd=2,
            padx=10,
            pady=2
        )
        kill_button.grid(row=0, column=1, padx=10)
        
        # Key count label
        self.key_count_var = tk.StringVar()
        self.key_count_var.set("Keys: 0")
        ttk.Label(status_frame, textvariable=self.key_count_var).grid(row=0, column=2, sticky=tk.E)
    
    # ===== CORE METHODS =====
    
    def run(self):
        """Start the application - FIXED VERSION"""
        print("Debug: Starting application")
        
        # Show login dialog first (before showing main window)
        from .login_dialog import LoginDialog
        
        login_dialog = LoginDialog()  # Don't pass self.root as parent since it's hidden
        login_result = login_dialog.show()
        
        print(f"Debug: Login dialog returned: {login_result}")
        
        if not login_result:
            # User cancelled login or failed authentication
            print("Debug: Login failed or cancelled, destroying main window")
            self.root.destroy()
            return
        
        print("Debug: Login successful, showing main window")
        
        # Authentication successful - now show the main window
        self.root.deiconify()  # Show the hidden window
        self.root.lift()       # Bring to front
        self.root.focus_force() # Give focus
        
        print("Debug: Main window should now be visible")
        
        # Get the master password from the login dialog
        # Note: For security, we should get the actual password from the login dialog
        # For now, we'll initialize the data manager properly
        try:
            if hasattr(self.key_generator, 'pgp_handler') and hasattr(self.key_generator.pgp_handler, 'handler'):
                # The data manager should already be initialized with encryption from the login process
                # We just need to ensure it's properly set up
                pass
        except Exception as e:
            print(f"Warning: Failed to initialize encryption: {e}")
        
        # Load message history
        self.load_message_history()
        
        # Initial setup
        self.refresh_key_list()
        self.refresh_contacts_list()
        
        # FIXED: Initialize chat profiles dropdown properly
        if SECURE_CHAT_AVAILABLE:
            self.refresh_chat_profiles()  # Load available key pairs into profile selector
            self.refresh_chat_contacts()  # Load contacts into chat contacts list
        
        print("Debug: Starting main window mainloop")
        
        # Start the main loop
        self.root.mainloop()
    
    # ===== CHAT SYSTEM METHODS - FIXED =====
    
    def refresh_chat_profiles(self):
        """Refresh the chat profiles dropdown with available key pairs - FIXED"""
        try:
            # Get private keys (key pairs that can be used for chat)
            private_keys = self.key_generator.list_keys(secret=True)
            
            profiles = []
            for key in private_keys:
                # Extract name from user ID
                user_id = key.get('uids', ['Unknown'])[0] if key.get('uids') else 'Unknown'
                name = user_id.split('<')[0].strip() if '<' in user_id else user_id
                fingerprint = key.get('fingerprint', '')
                
                # Create profile entry
                profile_display = f"{name} ({fingerprint[-8:]})"
                profiles.append({
                    'display': profile_display,
                    'name': name,
                    'fingerprint': fingerprint,
                    'key_info': key
                })
            
            # Update combo box
            profile_displays = [p['display'] for p in profiles]
            self.chat_profile_combo['values'] = profile_displays
            
            # Store profile data for lookup
            self.chat_profiles = profiles
            
            # Auto-select first profile if none selected and profiles exist
            if profiles and not self.chat_profile_var.get():
                self.chat_profile_combo.current(0)
                self.on_chat_profile_changed()
            
            print(f"DEBUG: Loaded {len(profiles)} chat profiles")
                
        except Exception as e:
            print(f"Warning: Failed to refresh chat profiles: {e}")
    
    def on_chat_profile_changed(self, event=None):
        """Handle chat profile selection change - FIXED"""
        try:
            selected_display = self.chat_profile_var.get()
            if not selected_display or not hasattr(self, 'chat_profiles'):
                return
            
            # Find the selected profile
            selected_profile = None
            for profile in self.chat_profiles:
                if profile['display'] == selected_display:
                    selected_profile = profile
                    break
            
            if selected_profile:
                # Auto-populate IRC nickname with the name from the key
                name = selected_profile['name']
                # Convert to IRC-friendly nickname (remove spaces, special chars)
                irc_nick = ''.join(c for c in name if c.isalnum() or c in '_-').lower()
                self.chat_irc_nickname_var.set(irc_nick)
                
                # Store selected profile info
                self.selected_chat_profile = selected_profile
                
                print(f"DEBUG: Selected profile {selected_profile['name']}, IRC nick: {irc_nick}")
                
        except Exception as e:
            print(f"Warning: Failed to handle profile change: {e}")
    
    def refresh_chat_contacts(self):
        """Refresh the chat contacts list - FIXED"""
        try:
            self.chat_contacts_listbox.delete(0, tk.END)
            self.chat_target_combo['values'] = []
            
            contact_names = []
            
            # Add contacts from unified contacts system (with IRC nicknames)
            unified_contacts = self.load_contacts()
            print(f"DEBUG: Found {len(unified_contacts)} unified contacts")
            
            for fingerprint, contact_info in unified_contacts.items():
                irc_nick = contact_info.get('irc_nickname', '').strip()
                print(f"DEBUG: Contact {contact_info.get('name', 'Unknown')} has IRC nick: '{irc_nick}'")
                
                if irc_nick:  # Only show contacts with IRC nicknames
                    display_name = f"{contact_info['name']} ({irc_nick})"
                    self.chat_contacts_listbox.insert(tk.END, display_name)
                    contact_names.append(irc_nick)
                    print(f"DEBUG: Added to chat contacts: {display_name}")
                    
                    # Add to secure chat if connected
                    if self.secure_chat and irc_nick not in self.secure_chat.contacts:
                        # Use public key if available, otherwise fall back to fingerprint
                        public_key = contact_info.get('public_key')
                        if public_key:
                            self.secure_chat.add_contact(contact_info['name'], irc_nick, public_key=public_key)
                        else:
                            self.secure_chat.add_contact(contact_info['name'], irc_nick, pgp_fingerprint=fingerprint)
            
            # Add contacts from secure chat (legacy)
            if self.secure_chat:
                for nickname, contact in self.secure_chat.contacts.items():
                    if nickname not in contact_names:  # Avoid duplicates
                        display_name = f"{contact.name} ({nickname})"
                        self.chat_contacts_listbox.insert(tk.END, display_name)
                        contact_names.append(nickname)
            
            # Add stored contacts (not yet added to secure chat)
            for nickname, contact_info in self.chat_contacts.items():
                if nickname not in contact_names:  # Avoid duplicates
                    display_name = f"{contact_info['name']} ({nickname})"
                    self.chat_contacts_listbox.insert(tk.END, display_name)
                    contact_names.append(nickname)
            
            # Update target combo
            self.chat_target_combo['values'] = contact_names
            
            print(f"DEBUG: Total chat contacts loaded: {len(contact_names)}")
            
        except Exception as e:
            print(f"Warning: Failed to refresh chat contacts: {e}")
    
    def add_chat_contact_to_unified_system(self, name, irc_nickname, public_key=None, pgp_fingerprint=None):
        """Add a chat contact to the unified contacts system - FIXED"""
        try:
            # Load existing contacts
            contacts = self.load_contacts()
            
            # Use fingerprint as key, or generate one if using public key
            if pgp_fingerprint:
                fingerprint = pgp_fingerprint
            elif public_key:
                # Extract fingerprint from public key if possible
                # For now, use a hash of the public key as fingerprint
                import hashlib
                fingerprint = hashlib.sha256(public_key.encode()).hexdigest()[:40].upper()
            else:
                print("Warning: No fingerprint or public key provided for contact")
                return
            
            # Create contact entry with proper field names
            contact_entry = {
                'name': name,
                'irc_nickname': irc_nickname,
                'date_added': time.strftime("%Y-%m-%d %H:%M:%S"),  # Use consistent field name
                'source': 'chat_contact'
            }
            
            # Add public key if available
            if public_key:
                contact_entry['public_key'] = public_key
            
            # Save to contacts database
            contacts[fingerprint] = contact_entry
            
            # Save using encrypted storage
            if hasattr(self.key_generator, 'data_manager') and self.key_generator.data_manager:
                self.key_generator.data_manager.save_data("contacts.json", contacts)
            else:
                # Fallback to unencrypted storage if data manager not available
                import json
                contacts_file = os.path.join(self.key_generator.gnupg_home, "contacts.json")
                with open(contacts_file, 'w') as f:
                    json.dump(contacts, f, indent=2)
            
            # Refresh contacts lists
            self.refresh_contacts_list()
            self.refresh_chat_contacts()
            
            print(f"DEBUG: Added chat contact {name} ({irc_nickname}) to unified system")
            
        except Exception as e:
            print(f"Warning: Failed to add chat contact to unified system: {e}")
    
    def get_current_chat_identity(self):
        """Get current chat identity (profile + IRC nickname) - FIXED"""
        if hasattr(self, 'selected_chat_profile') and self.selected_chat_profile:
            return {
                'profile': self.selected_chat_profile,
                'irc_nickname': self.chat_irc_nickname_var.get(),
                'fingerprint': self.selected_chat_profile['fingerprint']
            }
        return None
    
    # ===== PLACEHOLDER METHODS =====
    # These methods need to be implemented based on the original file
    
    def generate_key_dialog(self):
        """Show key generation dialog"""
        # TODO: Implement from original file
        pass
    
    def import_key_dialog(self):
        """Show import key dialog"""
        # TODO: Implement from original file
        pass
    
    def export_keys_dialog(self):
        """Show export keys dialog"""
        # TODO: Implement from original file
        pass
    
    def export_key_as_contact_card(self):
        """Export selected key as contact card"""
        # TODO: Implement from original file
        pass
    
    def delete_selected_key(self):
        """Delete the selected key"""
        # TODO: Implement from original file
        pass
    
    def on_key_selected(self, event):
        """Handle key selection"""
        # TODO: Implement from original file
        pass
    
    def refresh_key_list(self):
        """Refresh the keys list"""
        # TODO: Implement from original file
        pass
    
    def add_contact_dialog(self):
        """Show add contact dialog"""
        # TODO: Implement from original file
        pass
    
    def import_contact_card_dialog(self):
        """Show import contact card dialog"""
        # TODO: Implement from original file
        pass
    
    def export_contact_card(self):
        """Export contact card"""
        # TODO: Implement from original file
        pass
    
    def import_contact_key(self):
        """Import contact key"""
        # TODO: Implement from original file
        pass
    
    def remove_contact(self):
        """Remove selected contact"""
        # TODO: Implement from original file
        pass
    
    def delete_contact_with_key(self):
        """Delete contact with key"""
        # TODO: Implement from original file
        pass
    
    def on_contact_selected(self, event):
        """Handle contact selection"""
        # TODO: Implement from original file
        pass
    
    def refresh_contacts_list(self):
        """Refresh the contacts list"""
        # TODO: Implement from original file
        pass
    
    def load_contacts(self):
        """Load contacts from storage"""
        # TODO: Implement from original file
        return {}
    
    def encrypt_message(self):
        """Encrypt message"""
        # TODO: Implement from original file
        pass
    
    def decrypt_message(self):
        """Decrypt message"""
        # TODO: Implement from original file
        pass
    
    def paste_encrypted_message(self):
        """Paste encrypted message"""
        # TODO: Implement from original file
        pass
    
    def on_history_selected(self, event):
        """Handle history selection"""
        # TODO: Implement from original file
        pass
    
    def on_history_double_click(self, event):
        """Handle history double click"""
        # TODO: Implement from original file
        pass
    
    def load_message_history(self):
        """Load message history"""
        # TODO: Implement from original file
        pass
    
    def add_to_message_history(self, msg_type, subject, recipient, date, full_content=""):
        """Add to message history"""
        # TODO: Implement from original file
        pass
    
    def toggle_chat_connection(self):
        """Toggle chat connection"""
        # TODO: Implement from original file
        pass
    
    def add_chat_contact_dialog(self):
        """Show add chat contact dialog"""
        # TODO: Implement from original file
        pass
    
    def start_chat_with_contact(self, event):
        """Start chat with contact"""
        # TODO: Implement from original file
        pass
    
    def send_chat_message(self, event=None):
        """Send chat message"""
        # TODO: Implement from original file
        pass
    
    def create_group_dialog(self):
        """Show create group dialog"""
        # TODO: Implement from original file
        pass
    
    def join_group_dialog(self):
        """Show join group dialog"""
        # TODO: Implement from original file
        pass
    
    def leave_current_group(self):
        """Leave current group"""
        # TODO: Implement from original file
        pass
    
    def switch_to_group(self, event):
        """Switch to group"""
        # TODO: Implement from original file
        pass
    
    def show_group_context_menu(self, event):
        """Show group context menu"""
        # TODO: Implement from original file
        pass
    
    def manage_group_members_dialog(self):
        """Show manage group members dialog"""
        # TODO: Implement from original file
        pass
    
    def send_group_message(self, event=None):
        """Send group message"""
        # TODO: Implement from original file
        pass
    
    def secure_delete_dialog(self):
        """Show secure delete dialog"""
        # TODO: Implement from original file
        pass
    
    def key_management_dialog(self):
        """Show key management dialog"""
        # TODO: Implement from original file
        pass
    
    def show_about_dialog(self):
        """Show about dialog"""
        # TODO: Implement from original file
        pass
    
    def emergency_kill_switch(self):
        """Emergency kill switch"""
        # TODO: Implement from original file
        pass
    
    def on_closing(self):
        """Handle window closing"""
        # TODO: Implement from original file
        self.root.destroy()


def main():
    """Main entry point"""
    app = PGPToolMainWindow()
    app.run()


if __name__ == "__main__":
    main()

