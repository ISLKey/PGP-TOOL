"""
Main Window GUI Module
Creates the main application window with tabbed interface
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
                       background=COLORS['error'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(15, 10))  # More padding for important button
        style.map('Danger.TButton',
                 background=[('active', '#c82333'),  # Darker red on hover
                            ('pressed', '#bd2130')])   # Even darker when pressed
        
        # Success button (green) - for encrypt message
        style.configure('Success.TButton', 
                       font=('Arial', 10, 'bold'),
                       foreground='white',
                       background=COLORS['success'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(15, 10))  # More padding for important button
        style.map('Success.TButton',
                 background=[('active', '#218838'),  # Darker green on hover
                            ('pressed', '#1e7e34')])   # Even darker when pressed
        
    def create_menu(self):
        """Create the application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Import Key...", command=self.import_key_dialog)
        file_menu.add_command(label="Export Keys...", command=self.export_keys_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Create Backup...", command=self.create_backup_dialog)
        file_menu.add_command(label="Restore Backup...", command=self.restore_backup_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Security menu
        security_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Security", menu=security_menu)
        security_menu.add_command(label="Emergency Kill Switch", command=self.emergency_kill_switch)
        security_menu.add_command(label="Clear All Data", command=self.clear_all_data)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="How We Built This", command=self.show_how_we_built_this)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)
    
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
        ).pack(fill=tk.X, pady=5)
        
        # Import key button
        ttk.Button(
            left_panel, 
            text="Import Key", 
            command=self.import_key_dialog
        ).pack(fill=tk.X, pady=5)
        
        # Export selected key
        ttk.Button(
            left_panel, 
            text="Export Selected Key", 
            command=self.export_selected_key
        ).pack(fill=tk.X, pady=5)
        
        # Export as contact card
        ttk.Button(
            left_panel, 
            text="Export as Contact Card", 
            command=self.export_key_as_contact_card
        ).pack(fill=tk.X, pady=5)
        
        # Delete selected key (using same style as Emergency Kill button)
        delete_button = tk.Button(
            left_panel, 
            text="Delete Selected Key", 
            command=self.delete_selected_key,
            bg="#dc3545",  # Same red as Emergency Kill
            fg="white",    # White text
            font=("Arial", 9, "bold"),
            relief=tk.RAISED,
            bd=2,
            padx=10,
            pady=5
        )
        delete_button.pack(fill=tk.X, pady=5)
        
        # Separator
        ttk.Separator(left_panel, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Key info label
        ttk.Label(left_panel, text="Key Information:").pack(anchor=tk.W)
        
        # Key info text
        self.key_info_text = tk.Text(left_panel, height=8, width=30, wrap=tk.WORD)
        key_info_scroll = ttk.Scrollbar(left_panel, orient="vertical", command=self.key_info_text.yview)
        self.key_info_text.configure(yscrollcommand=key_info_scroll.set)
        self.key_info_text.pack(fill=tk.BOTH, expand=True, pady=5)
        key_info_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Right panel - Key list
        right_panel = ttk.LabelFrame(keys_frame, text="Your Keys", padding="10")
        right_panel.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)
        
        # Key list with scrollbar
        key_list_frame = ttk.Frame(right_panel)
        key_list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        key_list_frame.columnconfigure(0, weight=1)
        key_list_frame.rowconfigure(0, weight=1)
        
        # Treeview for key list
        self.key_tree = ttk.Treeview(
            key_list_frame, 
            columns=('Type', 'Name', 'Email', 'KeyID', 'Created'),
            show='tree headings'
        )
        
        # Configure columns
        self.key_tree.heading('#0', text='')
        self.key_tree.heading('Type', text='Type')
        self.key_tree.heading('Name', text='Name')
        self.key_tree.heading('Email', text='Email')
        self.key_tree.heading('KeyID', text='Key ID')
        self.key_tree.heading('Created', text='Created')
        
        self.key_tree.column('#0', width=30)
        self.key_tree.column('Type', width=80)
        self.key_tree.column('Name', width=150)
        self.key_tree.column('Email', width=200)
        self.key_tree.column('KeyID', width=120)
        self.key_tree.column('Created', width=100)
        
        # Scrollbars for key tree
        key_v_scroll = ttk.Scrollbar(key_list_frame, orient="vertical", command=self.key_tree.yview)
        key_h_scroll = ttk.Scrollbar(key_list_frame, orient="horizontal", command=self.key_tree.xview)
        self.key_tree.configure(yscrollcommand=key_v_scroll.set, xscrollcommand=key_h_scroll.set)
        
        # Grid the treeview and scrollbars
        self.key_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        key_v_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        key_h_scroll.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Bind selection event
        self.key_tree.bind('<<TreeviewSelect>>', self.on_key_selected)
        
        # Refresh keys button
        ttk.Button(
            right_panel, 
            text="Refresh Key List", 
            command=self.refresh_key_list
        ).grid(row=1, column=0, pady=10)
    
    def create_contacts_tab(self):
        """Create the contacts tab"""
        contacts_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(contacts_frame, text="👥 Contacts")
        
        # Configure grid
        contacts_frame.columnconfigure(0, weight=1)
        contacts_frame.rowconfigure(1, weight=1)
        
        # Top panel - Contact actions
        top_panel = ttk.Frame(contacts_frame)
        top_panel.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        top_panel.columnconfigure(2, weight=1)
        
        # Action buttons
        ttk.Button(
            top_panel, 
            text="Add Contact", 
            command=self.add_contact_dialog
        ).grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(
            top_panel, 
            text="Delete Contact", 
            command=self.delete_contact_with_key
        ).grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(
            top_panel, 
            text="Import Public Key", 
            command=self.import_contact_key
        ).grid(row=0, column=2, padx=(0, 10))
        
        ttk.Button(
            top_panel, 
            text="Export Contact Card", 
            command=self.export_contact_card
        ).grid(row=0, column=3, padx=(0, 10))
        
        ttk.Button(
            top_panel, 
            text="Import Contact Card", 
            command=self.import_contact_card
        ).grid(row=0, column=4, padx=(0, 10))
        
        # Contacts list
        list_frame = ttk.Frame(contacts_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview for contacts
        columns = ("Name", "Key ID", "IRC Nick", "Added Date")
        self.contacts_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.contacts_tree.heading("Name", text="Contact Name")
        self.contacts_tree.heading("Key ID", text="Key ID")
        self.contacts_tree.heading("IRC Nick", text="IRC Nickname")
        self.contacts_tree.heading("Added Date", text="Date Added")
        
        self.contacts_tree.column("Name", width=200)
        self.contacts_tree.column("Key ID", width=120)
        self.contacts_tree.column("IRC Nick", width=120)
        self.contacts_tree.column("Added Date", width=150)
        
        # Scrollbar for contacts
        contacts_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.contacts_tree.yview)
        self.contacts_tree.configure(yscrollcommand=contacts_scroll.set)
        
        self.contacts_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        contacts_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Contact info panel
        info_frame = ttk.LabelFrame(contacts_frame, text="Contact Information", padding="10")
        info_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        info_frame.columnconfigure(0, weight=1)
        
        self.contact_info_text = tk.Text(info_frame, height=4, wrap=tk.WORD)
        contact_info_scroll = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.contact_info_text.yview)
        self.contact_info_text.configure(yscrollcommand=contact_info_scroll.set)
        
        self.contact_info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        contact_info_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind selection event
        self.contacts_tree.bind('<<TreeviewSelect>>', self.on_contact_selected)
        
        # Status
        status_frame = ttk.Frame(contacts_frame)
        status_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.contact_count_var = tk.StringVar(value="Contacts: 0")
        ttk.Label(status_frame, textvariable=self.contact_count_var).pack(side=tk.LEFT)
        
        # Refresh contacts button
        ttk.Button(
            status_frame, 
            text="Refresh", 
            command=self.refresh_contacts_list
        ).pack(side=tk.RIGHT)
    
    def create_messages_tab(self):
        """Create the messages tab"""
        messages_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(messages_frame, text="💬 Messages")
        
        # Configure grid
        messages_frame.columnconfigure(0, weight=1)
        messages_frame.rowconfigure(1, weight=1)
        
        # Top panel - Message actions
        top_panel = ttk.Frame(messages_frame)
        top_panel.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        top_panel.columnconfigure(2, weight=1)
        
        # Action buttons
        ttk.Button(
            top_panel, 
            text="Compose New Message", 
            command=self.compose_message_dialog,
            style='Action.TButton'
        ).grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(
            top_panel, 
            text="Decrypt Message", 
            command=self.decrypt_message_dialog
        ).grid(row=0, column=1, padx=(0, 10))
        
        # Burn message button (prominent) - Using tkinter button for better color control
        burn_button = tk.Button(
            top_panel, 
            text="🔥 BURN MESSAGE NOW", 
            command=self.burn_message_now,
            bg='#dc3545',  # Red background
            fg='white',    # White text
            font=('Arial', 10, 'bold'),
            relief='flat',
            borderwidth=0,
            padx=15,
            pady=8,
            activebackground='#c82333',  # Darker red when clicked
            activeforeground='white'
        )
        burn_button.grid(row=0, column=3, padx=(10, 0))
        
        # Main message area
        main_panel = ttk.Frame(messages_frame)
        main_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_panel.columnconfigure(0, weight=1)
        main_panel.rowconfigure(0, weight=1)
        
        # Notebook for message types
        self.message_notebook = ttk.Notebook(main_panel)
        self.message_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create message sub-tabs
        self.create_compose_tab()
        self.create_decrypt_tab()
        self.create_history_tab()
    
    def create_compose_tab(self):
        """Create the compose message tab"""
        compose_frame = ttk.Frame(self.message_notebook, padding="10")
        self.message_notebook.add(compose_frame, text="Compose")
        
        # Configure grid
        compose_frame.columnconfigure(1, weight=1)
        compose_frame.rowconfigure(2, weight=1)
        
        # Recipient selection
        ttk.Label(compose_frame, text="Recipient:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.recipient_var = tk.StringVar()
        self.recipient_combo = ttk.Combobox(
            compose_frame, 
            textvariable=self.recipient_var,
            state="readonly"
        )
        self.recipient_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Subject
        ttk.Label(compose_frame, text="Subject:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.subject_var = tk.StringVar()
        ttk.Entry(
            compose_frame, 
            textvariable=self.subject_var
        ).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Message text
        ttk.Label(compose_frame, text="Message:").grid(row=2, column=0, sticky=(tk.W, tk.N), pady=5)
        
        message_frame = ttk.Frame(compose_frame)
        message_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(10, 0))
        message_frame.columnconfigure(0, weight=1)
        message_frame.rowconfigure(0, weight=1)
        
        self.compose_text = tk.Text(message_frame, wrap=tk.WORD, height=15)
        compose_scroll = ttk.Scrollbar(message_frame, orient="vertical", command=self.compose_text.yview)
        self.compose_text.configure(yscrollcommand=compose_scroll.set)
        
        self.compose_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        compose_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Encrypt button - Using tkinter button for better color control
        encrypt_button = tk.Button(
            compose_frame, 
            text="Encrypt Message", 
            command=self.encrypt_message,
            bg='#28a745',  # Green background
            fg='white',    # White text
            font=('Arial', 10, 'bold'),
            relief='flat',
            borderwidth=0,
            padx=15,
            pady=8,
            activebackground='#218838',  # Darker green when clicked
            activeforeground='white'
        )
        encrypt_button.grid(row=3, column=1, sticky=tk.E, pady=10)
    
    def create_decrypt_tab(self):
        """Create the decrypt message tab"""
        decrypt_frame = ttk.Frame(self.message_notebook, padding="10")
        self.message_notebook.add(decrypt_frame, text="Decrypt")
        
        # Configure grid
        decrypt_frame.columnconfigure(0, weight=1)
        decrypt_frame.rowconfigure(1, weight=1)
        decrypt_frame.rowconfigure(5, weight=1)
        
        # Encrypted message input
        ttk.Label(decrypt_frame, text="Encrypted Message:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        encrypted_frame = ttk.Frame(decrypt_frame)
        encrypted_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        encrypted_frame.columnconfigure(0, weight=1)
        encrypted_frame.rowconfigure(0, weight=1)
        
        self.encrypted_text = tk.Text(encrypted_frame, wrap=tk.WORD, height=8)
        encrypted_scroll = ttk.Scrollbar(encrypted_frame, orient="vertical", command=self.encrypted_text.yview)
        self.encrypted_text.configure(yscrollcommand=encrypted_scroll.set)
        
        self.encrypted_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        encrypted_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Copy and Paste buttons for encrypted text
        button_frame = ttk.Frame(decrypt_frame)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(
            button_frame,
            text="Paste Encrypted Message",
            command=self.paste_encrypted_message
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            button_frame,
            text="Copy Encrypted Message",
            command=self.copy_encrypted_message
        ).pack(side=tk.RIGHT)
        
        # Decrypt button
        ttk.Button(
            decrypt_frame, 
            text="Decrypt Message", 
            command=self.decrypt_message,
            style='Action.TButton'
        ).grid(row=3, column=0, pady=10)
        
        # Decrypted message output
        ttk.Label(decrypt_frame, text="Decrypted Message:").grid(row=4, column=0, sticky=tk.W, pady=5)
        
        decrypted_frame = ttk.Frame(decrypt_frame)
        decrypted_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        decrypted_frame.columnconfigure(0, weight=1)
        decrypted_frame.rowconfigure(0, weight=1)
        
        self.decrypted_text = tk.Text(decrypted_frame, wrap=tk.WORD, height=8)
        decrypted_scroll = ttk.Scrollbar(decrypted_frame, orient="vertical", command=self.decrypted_text.yview)
        self.decrypted_text.configure(yscrollcommand=decrypted_scroll.set)
        
        self.decrypted_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        decrypted_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
    
    def create_history_tab(self):
        """Create the enhanced message history tab"""
        history_frame = ttk.Frame(self.message_notebook, padding="10")
        self.message_notebook.add(history_frame, text="History")
        
        # Configure grid
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        
        # Create main paned window for history list and message viewer
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
        """Create the secure chat tab"""
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
        
        # Nickname
        ttk.Label(irc_frame, text="Nickname:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.chat_nickname_var = tk.StringVar()
        nickname_entry = ttk.Entry(irc_frame, textvariable=self.chat_nickname_var, width=15)
        nickname_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        # Generate random nickname button
        ttk.Button(irc_frame, text="Random", command=self.generate_chat_nickname, 
                  width=8).grid(row=2, column=0, pady=5)
        
        # Connect/Disconnect button
        self.chat_connect_button = ttk.Button(irc_frame, text="Connect", 
                                            command=self.toggle_chat_connection, width=12)
        self.chat_connect_button.grid(row=2, column=1, pady=5, padx=(5, 0))
        
        # Connection status
        self.chat_status_var = tk.StringVar(value="Disconnected")
        self.chat_status_label = ttk.Label(irc_frame, textvariable=self.chat_status_var, 
                                         foreground="red", font=('Arial', 9))
        self.chat_status_label.grid(row=3, column=0, columnspan=2, pady=2)
        
        # Chat Contacts section
        contacts_frame = ttk.LabelFrame(left_panel, text="Chat Contacts", padding="5")
        contacts_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        contacts_frame.columnconfigure(0, weight=1)
        contacts_frame.rowconfigure(1, weight=1)
        
        # Add contact button
        ttk.Button(contacts_frame, text="Add Contact", 
                  command=self.add_chat_contact_dialog, width=15).grid(row=0, column=0, pady=(0, 5))
        
        # Contacts list
        self.chat_contacts_listbox = tk.Listbox(contacts_frame, height=8)
        self.chat_contacts_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.chat_contacts_listbox.bind('<Double-Button-1>', self.start_chat_with_contact)
        
        # Chat controls
        chat_controls_frame = ttk.LabelFrame(left_panel, text="Chat Settings", padding="5")
        chat_controls_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        chat_controls_frame.columnconfigure(1, weight=1)
        
        # Profile selector
        ttk.Label(chat_controls_frame, text="Chat Profile:").grid(row=0, column=0, sticky=tk.W)
        self.chat_profile_var = tk.StringVar()
        self.chat_profile_combo = ttk.Combobox(chat_controls_frame, textvariable=self.chat_profile_var, 
                                             state="readonly", width=20)
        self.chat_profile_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        self.chat_profile_combo.bind('<<ComboboxSelected>>', self.on_chat_profile_changed)
        
        # ENHANCEMENT: Add refresh button for profiles
        ttk.Button(chat_controls_frame, text="🔄", command=self.refresh_chat_profiles, 
                  width=3).grid(row=0, column=2, padx=(5, 0))
        
        # ENHANCEMENT: Add key coordination button
        ttk.Button(chat_controls_frame, text="🔑 Fix Keys", command=self.show_key_coordination_dialog, 
                  width=12).grid(row=0, column=3, padx=(5, 0))
        
        # IRC Nickname (auto-populated from selected profile)
        ttk.Label(chat_controls_frame, text="IRC Nickname:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.chat_irc_nickname_var = tk.StringVar()
        self.chat_irc_nickname_entry = ttk.Entry(chat_controls_frame, textvariable=self.chat_irc_nickname_var, width=20)
        self.chat_irc_nickname_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=(5, 0))
        
        # Add callback for nickname changes
        self.chat_irc_nickname_var.trace('w', self.on_irc_nickname_changed)
        
        # Add Enter key binding to apply nickname change
        self.chat_irc_nickname_entry.bind('<Return>', lambda e: self.apply_nickname_change())
        
        # Add button to apply nickname change immediately
        ttk.Button(chat_controls_frame, text="Apply", command=self.apply_nickname_change, 
                  width=8).grid(row=1, column=2, padx=(5, 0), pady=(5, 0))
        
        # Save history checkbox
        self.chat_save_history_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(chat_controls_frame, text="Save chat history", 
                       variable=self.chat_save_history_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
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
        
        # Initialize chat system
        self.secure_chat = None
        self.group_chat = None
        self.chat_contacts = {}  # nickname -> contact info
        
        # Generate initial nickname
        self.generate_chat_nickname()
    
    def create_group_chat_tab(self):
        """Create the group chat tab"""
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
        
        # Current group info
        current_group_frame = ttk.LabelFrame(group_left_panel, text="Current Group", padding="5")
        current_group_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        current_group_frame.columnconfigure(0, weight=1)
        
        self.current_group_var = tk.StringVar(value="None")
        ttk.Label(current_group_frame, textvariable=self.current_group_var, 
                 font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W)
        
        self.group_member_count_var = tk.StringVar(value="0 members")
        ttk.Label(current_group_frame, textvariable=self.group_member_count_var).grid(row=1, column=0, sticky=tk.W)
        
        # Group creator display
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
    
    # Event handlers and dialog methods
    def generate_key_dialog(self):
        """Show key generation dialog"""
        from .dialogs import KeyGenerationDialog
        
        dialog = KeyGenerationDialog(self.root, self.key_generator)
        result = dialog.show()
        
        if result and result['success']:
            self.refresh_key_list()
            self.status_var.set("New key pair generated successfully")
            
            # CRITICAL FIX: Refresh chat profiles after key generation
            if SECURE_CHAT_AVAILABLE:
                print("Debug: Refreshing chat profiles after key generation...")
                self.refresh_chat_profiles()
                print("Debug: Chat profiles refreshed")
    
    def import_key_dialog(self):
        """Show import key dialog"""
        from .dialogs import ImportKeyDialog
        
        dialog = ImportKeyDialog(self.root, self.key_generator)
        result = dialog.show()
        
        if result and result['success']:
            self.refresh_key_list()
            self.status_var.set(f"Imported {result['imported_count']} key(s)")
            
            # CRITICAL FIX: Refresh chat profiles after key import
            if SECURE_CHAT_AVAILABLE:
                print("Debug: Refreshing chat profiles after key import...")
                self.refresh_chat_profiles()
                print("Debug: Chat profiles refreshed")
    
    def export_keys_dialog(self):
        """Show export keys dialog"""
        # Get all keys
        public_keys = self.key_generator.list_keys(secret=False)
        private_keys = self.key_generator.list_keys(secret=True)
        
        if not public_keys and not private_keys:
            messagebox.showinfo("Info", "No keys available to export")
            return
        
        # Ask user what to export
        export_choice = messagebox.askyesnocancel(
            "Export Keys",
            "What would you like to export?\n\n"
            "Yes = All Public Keys\n"
            "No = All Private Keys\n"
            "Cancel = Selected Key Only"
        )
        
        if export_choice is None:  # Cancel - export selected key
            self.export_selected_key()
            return
        
        # Choose file location
        filename = filedialog.asksaveasfilename(
            title="Save Keys As",
            defaultextension=".asc",
            filetypes=[
                ("ASCII Armor", "*.asc"),
                ("PGP Key", "*.pgp"),
                ("Text File", "*.txt"),
                ("All Files", "*.*")
            ]
        )
        
        if not filename:
            return
        
        try:
            if export_choice:  # Export public keys
                keys_data = ""
                for key in public_keys:
                    result = self.key_generator.export_public_key(key['fingerprint'])
                    if result['success']:
                        keys_data += result['public_key'] + "\n\n"
                
                if keys_data:
                    with open(filename, 'w') as f:
                        f.write(keys_data)
                    messagebox.showinfo("Success", f"Exported {len(public_keys)} public key(s)")
                else:
                    messagebox.showerror("Error", "No keys could be exported")
            
            else:  # Export private keys
                passphrase = self.get_passphrase("Enter passphrase for private key export:")
                if not passphrase:
                    return
                
                keys_data = ""
                exported_count = 0
                
                for key in private_keys:
                    result = self.key_generator.export_private_key(key['fingerprint'], passphrase)
                    if result['success']:
                        keys_data += result['private_key'] + "\n\n"
                        exported_count += 1
                
                if keys_data:
                    with open(filename, 'w') as f:
                        f.write(keys_data)
                    messagebox.showinfo("Success", f"Exported {exported_count} private key(s)")
                else:
                    messagebox.showerror("Error", "No private keys could be exported")
        
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def export_selected_key(self):
        """Export the selected key"""
        selection = self.key_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a key to export")
            return
        
        # Get selected key info
        item = self.key_tree.item(selection[0])
        values = item['values']
        key_type = values[0]  # Public or Private
        key_id = values[3]    # Key ID
        
        # Find the full key info
        if key_type == "Public":
            keys = self.key_generator.list_keys(secret=False)
        else:
            keys = self.key_generator.list_keys(secret=True)
        
        selected_key = None
        for key in keys:
            if key['keyid'].endswith(key_id):
                selected_key = key
                break
        
        if not selected_key:
            messagebox.showerror("Error", "Could not find selected key")
            return
        
        # Choose file location
        filename = filedialog.asksaveasfilename(
            title="Export Key As",
            defaultextension=".asc",
            filetypes=[
                ("ASCII Armor", "*.asc"),
                ("PGP Key", "*.pgp"),
                ("Text File", "*.txt"),
                ("All Files", "*.*")
            ]
        )
        
        if not filename:
            return
        
        try:
            if key_type == "Public":
                result = self.key_generator.export_public_key(selected_key['fingerprint'])
                if result['success']:
                    with open(filename, 'w') as f:
                        f.write(result['public_key'])
                    messagebox.showinfo("Success", "Public key exported successfully")
                else:
                    messagebox.showerror("Error", f"Export failed: {result['error']}")
            
            else:  # Private key
                passphrase = self.get_passphrase("Enter passphrase for private key:")
                if not passphrase:
                    return
                
                result = self.key_generator.export_private_key(selected_key['fingerprint'], passphrase)
                if result['success']:
                    with open(filename, 'w') as f:
                        f.write(result['private_key'])
                    messagebox.showinfo("Success", "Private key exported successfully")
                else:
                    messagebox.showerror("Error", f"Export failed: {result['error']}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def delete_selected_key(self):
        """Delete the selected key"""
        selection = self.key_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a key to delete")
            return
        
        # Get selected key info
        item = self.key_tree.item(selection[0])
        values = item['values']
        key_type = values[0]  # Public or Private
        key_name = values[1]  # Name
        key_id = values[3]    # Key ID
        
        # Confirm deletion
        if not messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete this {key_type.lower()} key?\n\n"
            f"Name: {key_name}\n"
            f"Key ID: {key_id}\n\n"
            "This action cannot be undone!"
        ):
            return
        
        # Find the full key info
        if key_type == "Public":
            keys = self.key_generator.list_keys(secret=False)
        else:
            keys = self.key_generator.list_keys(secret=True)
        
        selected_key = None
        for key in keys:
            if key['keyid'].endswith(key_id):
                selected_key = key
                break
        
        if not selected_key:
            messagebox.showerror("Error", "Could not find selected key")
            return
        
        try:
            if key_type == "Private":
                passphrase = self.get_passphrase("Enter passphrase to delete private key:")
                if not passphrase:
                    return
                
                # Note: Passphrase verification could be added here if needed
                # For now, we'll proceed with deletion without passphrase verification
                result = self.key_generator.delete_key(
                    selected_key['fingerprint'], 
                    secret=True
                )
            else:
                result = self.key_generator.delete_key(selected_key['fingerprint'], secret=False)
            
            if result['success']:
                self.refresh_key_list()
                self.status_var.set(f"{key_type} key deleted successfully")
            else:
                messagebox.showerror("Error", f"Deletion failed: {result['error']}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Deletion failed: {str(e)}")
    
    def get_passphrase(self, prompt):
        """Get passphrase from user"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Passphrase Required")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Content
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text=prompt).pack(pady=(0, 10))
        
        passphrase_var = tk.StringVar()
        entry = ttk.Entry(main_frame, textvariable=passphrase_var, show="*", width=40)
        entry.pack(pady=(0, 20))
        entry.focus()
        
        result = [None]  # Use list to allow modification in nested function
        
        def ok_clicked():
            result[0] = passphrase_var.get()
            dialog.destroy()
        
        def cancel_clicked():
            dialog.destroy()
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack()
        
        ttk.Button(button_frame, text="OK", command=ok_clicked).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=cancel_clicked).pack(side=tk.LEFT)
        
        # Bind Enter key
        entry.bind('<Return>', lambda e: ok_clicked())
        
        dialog.wait_window()
        return result[0]
    
    def create_backup_dialog(self):
        """Show create backup dialog"""
        # Check if there are any keys to backup
        public_keys = self.key_generator.list_keys(secret=False)
        private_keys = self.key_generator.list_keys(secret=True)
        
        if not public_keys and not private_keys:
            messagebox.showinfo("Info", "No keys available to backup")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Encrypted Backup")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Content
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="Create Encrypted Backup", font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # Instructions
        instructions = tk.Text(main_frame, height=4, wrap=tk.WORD)
        instructions.pack(fill=tk.X, pady=(0, 20))
        instructions.insert(tk.END, 
            "This will create an encrypted backup of all your keys. "
            "The backup will be protected with a password you choose. "
            "Keep this backup file and password safe - you'll need both to restore your keys."
        )
        instructions.config(state=tk.DISABLED)
        
        # Key passphrase
        ttk.Label(main_frame, text="Enter your key passphrase (for private keys):").pack(anchor=tk.W, pady=5)
        key_passphrase_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=key_passphrase_var, show="*", width=50).pack(fill=tk.X, pady=(0, 10))
        
        # Backup password
        ttk.Label(main_frame, text="Choose backup password:").pack(anchor=tk.W, pady=5)
        backup_password_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=backup_password_var, show="*", width=50).pack(fill=tk.X, pady=(0, 10))
        
        # Confirm backup password
        ttk.Label(main_frame, text="Confirm backup password:").pack(anchor=tk.W, pady=5)
        confirm_password_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=confirm_password_var, show="*", width=50).pack(fill=tk.X, pady=(0, 20))
        
        def create_backup():
            key_passphrase = key_passphrase_var.get()
            backup_password = backup_password_var.get()
            confirm_password = confirm_password_var.get()
            
            if not backup_password:
                messagebox.showerror("Error", "Please enter a backup password")
                return
            
            if backup_password != confirm_password:
                messagebox.showerror("Error", "Backup passwords do not match")
                return
            
            if len(backup_password) < 8:
                messagebox.showerror("Error", "Backup password must be at least 8 characters long")
                return
            
            # Choose save location
            filename = filedialog.asksaveasfilename(
                title="Save Backup As",
                defaultextension=".pgpbackup",
                filetypes=[
                    ("PGP Backup", "*.pgpbackup"),
                    ("Encrypted File", "*.enc"),
                    ("All Files", "*.*")
                ]
            )
            
            if not filename:
                return
            
            try:
                result = self.key_generator.create_backup(backup_password, key_passphrase)
                
                if result['success']:
                    with open(filename, 'w') as f:
                        f.write(result['encrypted_backup'])
                    
                    messagebox.showinfo("Success", f"Backup created successfully!\n\nFile: {filename}")
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", f"Backup creation failed: {result['error']}")
            
            except Exception as e:
                messagebox.showerror("Error", f"Backup creation failed: {str(e)}")
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Create Backup", command=create_backup).pack(side=tk.RIGHT, padx=(0, 10))
    
    def restore_backup_dialog(self):
        """Show restore backup dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Restore from Backup")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Content
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="Restore from Backup", font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # Instructions
        instructions = tk.Text(main_frame, height=3, wrap=tk.WORD)
        instructions.pack(fill=tk.X, pady=(0, 20))
        instructions.insert(tk.END, 
            "Select your backup file and enter the backup password to restore your keys. "
            "This will import all keys from the backup into your current keyring."
        )
        instructions.config(state=tk.DISABLED)
        
        # File selection
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(file_frame, text="Backup file:").pack(anchor=tk.W)
        
        file_select_frame = ttk.Frame(file_frame)
        file_select_frame.pack(fill=tk.X, pady=5)
        
        backup_file_var = tk.StringVar()
        file_entry = ttk.Entry(file_select_frame, textvariable=backup_file_var, width=50)
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        def browse_file():
            filename = filedialog.askopenfilename(
                title="Select Backup File",
                filetypes=[
                    ("PGP Backup", "*.pgpbackup"),
                    ("Encrypted File", "*.enc"),
                    ("All Files", "*.*")
                ]
            )
            if filename:
                backup_file_var.set(filename)
        
        ttk.Button(file_select_frame, text="Browse", command=browse_file).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Backup password
        ttk.Label(main_frame, text="Backup password:").pack(anchor=tk.W, pady=5)
        backup_password_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=backup_password_var, show="*", width=50).pack(fill=tk.X, pady=(0, 20))
        
        def restore_backup():
            backup_file = backup_file_var.get()
            backup_password = backup_password_var.get()
            
            if not backup_file:
                messagebox.showerror("Error", "Please select a backup file")
                return
            
            if not backup_password:
                messagebox.showerror("Error", "Please enter the backup password")
                return
            
            try:
                # Read backup file
                with open(backup_file, 'r') as f:
                    encrypted_backup = f.read()
                
                # Restore backup
                result = self.key_generator.restore_backup(encrypted_backup, backup_password)
                
                if result['success']:
                    messagebox.showinfo("Success", "Backup restored successfully!")
                    self.refresh_key_list()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", f"Backup restore failed: {result['error']}")
            
            except FileNotFoundError:
                messagebox.showerror("Error", "Backup file not found")
            except Exception as e:
                messagebox.showerror("Error", f"Backup restore failed: {str(e)}")
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Restore Backup", command=restore_backup).pack(side=tk.RIGHT, padx=(0, 10))
    
    def emergency_kill_switch(self):
        """Emergency data deletion"""
        result = messagebox.askyesno(
            "EMERGENCY KILL SWITCH", 
            "⚠️ WARNING ⚠️\n\n"
            "This will PERMANENTLY DELETE ALL:\n"
            "• Private keys\n"
            "• Public keys\n"
            "• Messages\n"
            "• Application data\n\n"
            "This action CANNOT be undone!\n\n"
            "Are you absolutely sure?"
        )
        if result:
            # Confirm again
            confirm = messagebox.askyesno(
                "FINAL CONFIRMATION", 
                "Last chance to cancel!\n\n"
                "Delete ALL data permanently?\n\n"
                "Type 'DELETE' to confirm:",
                icon='warning'
            )
            if confirm:
                # Get final confirmation by typing
                confirm_text = self.get_text_confirmation("Type 'DELETE' to confirm permanent data deletion:")
                if confirm_text == "DELETE":
                    self.perform_emergency_deletion()
                else:
                    messagebox.showinfo("Cancelled", "Emergency deletion cancelled")
    
    def get_text_confirmation(self, prompt):
        """Get text confirmation from user"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Confirmation Required")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Content
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text=prompt).pack(pady=(0, 10))
        
        text_var = tk.StringVar()
        entry = ttk.Entry(main_frame, textvariable=text_var, width=40)
        entry.pack(pady=(0, 20))
        entry.focus()
        
        result = [None]
        
        def ok_clicked():
            result[0] = text_var.get()
            dialog.destroy()
        
        def cancel_clicked():
            dialog.destroy()
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack()
        
        ttk.Button(button_frame, text="OK", command=ok_clicked).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=cancel_clicked).pack(side=tk.LEFT)
        
        entry.bind('<Return>', lambda e: ok_clicked())
        
        dialog.wait_window()
        return result[0] or ""
    
    def perform_emergency_deletion(self):
        """Perform the actual emergency deletion"""
        try:
            # Clear all GUI fields
            self.compose_text.delete(1.0, tk.END)
            self.encrypted_text.delete(1.0, tk.END)
            self.decrypted_text.config(state=tk.NORMAL)
            self.decrypted_text.delete(1.0, tk.END)
            self.decrypted_text.config(state=tk.DISABLED)
            self.subject_var.set("")
            self.key_info_text.delete(1.0, tk.END)
            
            # Clear key tree
            for item in self.key_tree.get_children():
                self.key_tree.delete(item)
            
            # Clear history tree
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            
            # Clear clipboard
            try:
                self.root.clipboard_clear()
            except:
                pass
            
            # Delete all keys
            public_keys = self.key_generator.list_keys(secret=False)
            private_keys = self.key_generator.list_keys(secret=True)
            
            for key in private_keys:
                try:
                    self.key_generator.delete_key(key['fingerprint'], secret=True)
                except:
                    pass
            
            for key in public_keys:
                try:
                    self.key_generator.delete_key(key['fingerprint'], secret=False)
                except:
                    pass
            
            # Clean up crypto backend
            self.key_generator.cleanup()
            
            # Delete data directory
            import shutil
            if os.path.exists(DATA_DIR):
                try:
                    shutil.rmtree(DATA_DIR)
                except:
                    pass
            
            # Recreate data directory
            os.makedirs(DATA_DIR, exist_ok=True)
            
            # Reinitialize crypto backend
            self.key_generator = SecureKeyGenerator(
                gnupg_home=os.path.join(DATA_DIR, "gnupg")
            )
            
            # Update status
            self.status_var.set("EMERGENCY DELETION COMPLETED")
            self.key_count_var.set("Keys: 0")
            
            messagebox.showinfo(
                "Emergency Deletion Complete", 
                "All data has been permanently deleted.\n\n"
                "The application has been reset to a clean state."
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Emergency deletion encountered an error: {str(e)}")
    
    def clear_all_data(self):
        """Clear all application data"""
        result = messagebox.askyesno(
            "Clear All Data",
            "This will delete all keys, messages, and application data.\n\n"
            "Are you sure you want to continue?"
        )
        
        if result:
            confirm = messagebox.askyesno(
                "Confirm Clear Data",
                "This action cannot be undone!\n\n"
                "Proceed with clearing all data?"
            )
            
            if confirm:
                self.perform_emergency_deletion()
    
    def compose_message_dialog(self):
        """Show compose message dialog"""
        # Switch to compose tab
        self.message_notebook.select(0)
        self.notebook.select(1)  # Switch to Messages tab
        
        # Update recipient list
        self.update_recipient_list()
    
    def decrypt_message_dialog(self):
        """Show decrypt message dialog"""
        # Switch to decrypt tab
        self.message_notebook.select(1)
        self.notebook.select(1)  # Switch to Messages tab
    
    def update_recipient_list(self):
        """Update the recipient combobox with available public keys and contacts"""
        # Get all public keys
        public_keys = self.key_generator.list_keys(secret=False)
        key_map = {key['fingerprint']: key for key in public_keys}
        
        # Get contacts
        contacts = self.load_contacts()
        
        recipients = []
        
        # Add contacts first (preferred)
        for fingerprint, contact_info in contacts.items():
            if fingerprint in key_map:
                key_info = key_map[fingerprint]
                recipients.append(f"📞 {contact_info['name']} ({key_info['keyid'][-8:]})")
        
        # Add separator if we have both contacts and other keys
        if contacts and len(public_keys) > len(contacts):
            recipients.append("--- Other Public Keys ---")
        
        # Add other public keys (not in contacts)
        for key in public_keys:
            if key['fingerprint'] not in contacts:
                if key['uids']:
                    uid = key['uids'][0]
                    recipients.append(f"🔑 {uid} ({key['keyid'][-8:]})")
        
        self.recipient_combo['values'] = recipients
        
        if recipients and not recipients[0].startswith("---"):
            self.recipient_combo.set(recipients[0])
        elif len(recipients) > 1:
            # Skip separator and select first actual recipient
            for recipient in recipients:
                if not recipient.startswith("---"):
                    self.recipient_combo.set(recipient)
                    break
        else:
            self.recipient_combo.set("No public keys available")
    
    def encrypt_message(self):
        """Encrypt the composed message"""
        # Get message content
        subject = self.subject_var.get().strip()
        message_text = self.compose_text.get(1.0, tk.END).strip()
        recipient = self.recipient_var.get()
        
        if not message_text:
            messagebox.showwarning("Warning", "Please enter a message to encrypt")
            return
        
        if not recipient or recipient == "No public keys available":
            messagebox.showwarning("Warning", "Please select a recipient")
            return
        
        try:
            # Extract key ID from recipient string
            key_id = recipient.split('(')[-1].replace(')', '')
            
            # Find the full fingerprint
            public_keys = self.key_generator.list_keys(secret=False)
            recipient_fingerprint = None
            
            for key in public_keys:
                if key['keyid'].endswith(key_id):
                    recipient_fingerprint = key['fingerprint']
                    break
            
            if not recipient_fingerprint:
                messagebox.showerror("Error", "Could not find recipient key")
                return
            
            # Prepare full message
            full_message = f"Subject: {subject}\n\n{message_text}"
            
            # Encrypt the message
            result = self.key_generator.encrypt_message(full_message, [recipient_fingerprint])
            
            if result['success']:
                # Show encrypted message in a dialog
                self.show_encrypted_message(result['encrypted_message'], subject, recipient)
                
                # Clear compose fields
                self.compose_text.delete(1.0, tk.END)
                self.subject_var.set("")
                
                self.status_var.set("Message encrypted successfully")
            else:
                messagebox.showerror("Error", f"Encryption failed: {result['error']}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Encryption failed: {str(e)}")
    
    def show_encrypted_message(self, encrypted_message, subject, recipient):
        """Show the encrypted message in a dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Encrypted Message")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Content
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="Message Encrypted Successfully", font=('Arial', 16, 'bold')).pack(pady=(0, 10))
        
        # Info
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(info_frame, text=f"Subject: {subject}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Recipient: {recipient}").pack(anchor=tk.W)
        
        # Encrypted message
        ttk.Label(main_frame, text="Encrypted Message:").pack(anchor=tk.W, pady=(10, 5))
        
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD)
        text_scroll = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=text_scroll.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget.insert(tk.END, encrypted_message)
        text_widget.config(state=tk.DISABLED)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        def copy_to_clipboard():
            dialog.clipboard_clear()
            dialog.clipboard_append(encrypted_message)
            messagebox.showinfo("Copied", "Encrypted message copied to clipboard")
        
        def save_to_file():
            filename = filedialog.asksaveasfilename(
                title="Save Encrypted Message",
                defaultextension=".txt",
                filetypes=[
                    ("Text Files", "*.txt"),
                    ("PGP Message", "*.pgp"),
                    ("All Files", "*.*")
                ]
            )
            
            if filename:
                try:
                    with open(filename, 'w') as f:
                        f.write(encrypted_message)
                    messagebox.showinfo("Saved", "Encrypted message saved to file")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save file: {str(e)}")
        
        ttk.Button(button_frame, text="Copy to Clipboard", command=copy_to_clipboard).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Save to File", command=save_to_file).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(button_frame, text="Close", command=dialog.destroy).pack(side=tk.RIGHT)
    
    def decrypt_message(self):
        """Decrypt the input message"""
        encrypted_message = self.encrypted_text.get(1.0, tk.END).strip()
        
        if not encrypted_message:
            messagebox.showwarning("Warning", "Please enter an encrypted message to decrypt")
            return
        
        # Validate message format
        if not ("-----BEGIN PGP MESSAGE-----" in encrypted_message and "-----END PGP MESSAGE-----" in encrypted_message):
            messagebox.showerror("Error", "Invalid PGP message format")
            return
        
        # Get passphrase
        passphrase = self.get_passphrase("Enter passphrase to decrypt message:")
        if not passphrase:
            return
        
        try:
            result = self.key_generator.decrypt_message(encrypted_message, passphrase)
            
            if result['success']:
                decrypted_message = result['decrypted_message']
                
                # Display decrypted message
                self.decrypted_text.config(state=tk.NORMAL)
                self.decrypted_text.delete(1.0, tk.END)
                self.decrypted_text.insert(tk.END, decrypted_message)
                self.decrypted_text.config(state=tk.DISABLED)
                
                self.status_var.set("Message decrypted successfully")
                
                # Add to history
                self.add_to_message_history("Decrypted", decrypted_message[:50] + "...", "Unknown", "Now")
            else:
                messagebox.showerror("Error", f"Decryption failed: {result['error']}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Decryption failed: {str(e)}")
    
    def copy_encrypted_message(self):
        """Copy encrypted message to clipboard"""
        encrypted_message = self.encrypted_text.get(1.0, tk.END).strip()
        
        if not encrypted_message:
            messagebox.showwarning("Warning", "No encrypted message to copy")
            return
        
        try:
            # Copy to clipboard
            self.root.clipboard_clear()
            self.root.clipboard_append(encrypted_message)
            
            # Show success message
            messagebox.showinfo("Success", f"Copied {len(encrypted_message)} characters to clipboard")
            
            # Update status
            self.status_var.set("Encrypted message copied to clipboard")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy to clipboard: {str(e)}")
    
    def paste_encrypted_message(self):
        """Paste encrypted message from clipboard"""
        try:
            # Get clipboard content
            clipboard_content = self.root.clipboard_get()
            
            if not clipboard_content:
                messagebox.showwarning("Warning", "Clipboard is empty")
                return
            
            # Clear existing content and paste new content
            self.encrypted_text.delete(1.0, tk.END)
            self.encrypted_text.insert(tk.END, clipboard_content)
            
            # Show success message
            messagebox.showinfo("Success", f"Pasted {len(clipboard_content)} characters from clipboard")
            
            # Update status
            self.status_var.set("Encrypted message pasted from clipboard")
            
        except tk.TclError:
            messagebox.showerror("Error", "Failed to access clipboard")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste from clipboard: {str(e)}")
    
    def add_to_message_history(self, msg_type, subject, recipient, date, full_content=""):
        """Add a message to the history with full content storage"""
        import uuid
        
        # Generate unique ID for this message
        message_id = str(uuid.uuid4())
        
        # Store full message content
        self.message_history_data[message_id] = {
            'type': msg_type,
            'subject': subject,
            'recipient': recipient,
            'date': date,
            'content': full_content,
            'timestamp': time.time()
        }
        
        # Add to tree view (with hidden ID column)
        self.history_tree.insert('', 'end', values=(msg_type, subject, recipient, date, message_id))
        
        # Save to persistent storage if data manager is available
        try:
            if hasattr(self.key_generator, 'data_manager') and self.key_generator.data_manager.encryption:
                self.key_generator.data_manager.save_data("message_history.json", self.message_history_data)
        except Exception as e:
            print(f"Warning: Failed to save message history: {e}")
    
    def on_history_selected(self, event):
        """Handle history item selection"""
        selection = self.history_tree.selection()
        if selection:
            item = selection[0]
            values = self.history_tree.item(item, 'values')
            
            if len(values) >= 5:
                message_id = values[4]  # Hidden ID column
                
                if message_id in self.message_history_data:
                    message_data = self.message_history_data[message_id]
                    
                    # Update label
                    self.history_message_label.config(
                        text=f"📧 {message_data['type']} Message: {message_data['subject']}"
                    )
                    
                    # Display message content
                    self.history_message_text.config(state=tk.NORMAL)
                    self.history_message_text.delete(1.0, tk.END)
                    
                    # Format message display
                    display_text = f"📋 Message Details:\n"
                    display_text += "=" * 50 + "\n\n"
                    display_text += f"Type: {message_data['type']}\n"
                    display_text += f"Subject: {message_data['subject']}\n"
                    display_text += f"Recipient/Sender: {message_data['recipient']}\n"
                    display_text += f"Date: {message_data['date']}\n"
                    display_text += "\n" + "=" * 50 + "\n"
                    display_text += "📄 Message Content:\n"
                    display_text += "=" * 50 + "\n\n"
                    display_text += message_data['content']
                    
                    self.history_message_text.insert(tk.END, display_text)
                    self.history_message_text.config(state=tk.DISABLED)
                else:
                    self.show_history_placeholder()
        else:
            self.show_history_placeholder()
    
    def on_history_double_click(self, event):
        """Handle double-click on history item"""
        selection = self.history_tree.selection()
        if selection:
            item = selection[0]
            values = self.history_tree.item(item, 'values')
            
            if len(values) >= 5:
                message_id = values[4]
                
                if message_id in self.message_history_data:
                    message_data = self.message_history_data[message_id]
                    
                    # Show message in a popup window
                    self.show_message_popup(message_data)
    
    def show_message_popup(self, message_data):
        """Show message in a popup window"""
        popup = tk.Toplevel(self.root)
        popup.title(f"Message: {message_data['subject']}")
        popup.geometry("600x500")
        popup.resizable(True, True)
        
        # Make it modal
        popup.transient(self.root)
        popup.grab_set()
        
        # Center the popup
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (600 // 2)
        y = (popup.winfo_screenheight() // 2) - (500 // 2)
        popup.geometry(f"600x500+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(popup, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Header
        header_text = f"📧 {message_data['type']} Message - {message_data['date']}"
        ttk.Label(main_frame, text=header_text, font=('Arial', 12, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 10)
        )
        
        # Message content
        text_widget = tk.Text(
            main_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg='#f8f9fa',
            relief=tk.SUNKEN,
            borderwidth=2
        )
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Grid
        text_widget.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # Insert content
        display_text = f"Subject: {message_data['subject']}\n"
        display_text += f"Recipient/Sender: {message_data['recipient']}\n"
        display_text += f"Type: {message_data['type']}\n"
        display_text += f"Date: {message_data['date']}\n"
        display_text += "\n" + "=" * 50 + "\n\n"
        display_text += message_data['content']
        
        text_widget.insert(tk.END, display_text)
        text_widget.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(
            main_frame, 
            text="Close", 
            command=popup.destroy
        ).grid(row=2, column=0, pady=(10, 0))
    
    def show_history_placeholder(self):
        """Show placeholder text in history viewer"""
        self.history_message_label.config(text="Select a message from the history to view its content")
        self.history_message_text.config(state=tk.NORMAL)
        self.history_message_text.delete(1.0, tk.END)
        self.history_message_text.insert(tk.END, 
            "📋 Message History Viewer\n\n"
            "Select a message from the list above to view its full content.\n"
            "Double-click a message to open it in a separate window.\n\n"
            "💡 Tip: All your encrypted and decrypted messages are stored here for easy reference."
        )
        self.history_message_text.config(state=tk.DISABLED)
    
    def load_message_history(self):
        """Load message history from storage"""
        try:
            if hasattr(self.key_generator, 'data_manager') and self.key_generator.data_manager.encryption:
                stored_history = self.key_generator.data_manager.load_data("message_history.json", default={})
                self.message_history_data.update(stored_history)
                
                # Populate tree view
                for message_id, message_data in stored_history.items():
                    self.history_tree.insert('', 'end', values=(
                        message_data['type'],
                        message_data['subject'],
                        message_data['recipient'],
                        message_data['date'],
                        message_id
                    ))
        except Exception as e:
            print(f"Warning: Failed to load message history: {e}")
    
    def burn_message_now(self):
        """Burn/delete the current message"""
        result = messagebox.askyesno(
            "Burn Message", 
            "Are you sure you want to permanently delete the current message?\n\nThis action cannot be undone!"
        )
        if result:
            # Clear all message fields in compose tab
            self.compose_text.delete(1.0, tk.END)
            
            # Clear encrypted message field in decrypt tab
            self.encrypted_text.delete(1.0, tk.END)
            
            # Clear decrypted message field in decrypt tab
            self.decrypted_text.config(state=tk.NORMAL)
            self.decrypted_text.delete(1.0, tk.END)
            self.decrypted_text.config(state=tk.DISABLED)
            
            # Clear history message viewer
            self.history_message_text.config(state=tk.NORMAL)
            self.history_message_text.delete(1.0, tk.END)
            self.history_message_text.config(state=tk.DISABLED)
            
            # Clear subject and recipient fields
            self.subject_var.set("")
            if hasattr(self, 'recipient_var'):
                self.recipient_var.set("")
            
            # Clear any selected history item
            for item in self.history_tree.selection():
                self.history_tree.selection_remove(item)
            
            # Update status
            self.status_var.set("Message burned successfully")
            
            # Also clear clipboard for security
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append("")  # Ensure clipboard is truly cleared
            except:
                pass
            
            # Force a refresh of the display
            self.root.update_idletasks()
    
    def emergency_kill_switch(self):
        """Emergency data deletion"""
        result = messagebox.askyesno(
            "EMERGENCY KILL SWITCH", 
            "⚠️ WARNING ⚠️\n\nThis will PERMANENTLY DELETE ALL:\n• Private keys\n• Public keys\n• Messages\n• Contacts\n• Application data\n\nThis action CANNOT be undone!\n\nAre you absolutely sure?"
        )
        
        if result:
            confirm = messagebox.askyesno(
                "FINAL WARNING", 
                "Last chance to cancel!\n\nDelete ALL data permanently?"
            )
            if confirm:
                try:
                    # Clear clipboard
                    try:
                        self.root.clipboard_clear()
                    except:
                        pass
                    
                    # Delete all key files and data
                    import shutil
                    import os
                    
                    data_dir = self.key_generator.gnupg_home
                    if os.path.exists(data_dir):
                        # Secure deletion - overwrite files multiple times
                        for root, dirs, files in os.walk(data_dir):
                            for file in files:
                                file_path = os.path.join(root, file)
                                try:
                                    # Overwrite file with random data 3 times
                                    if os.path.exists(file_path):
                                        file_size = os.path.getsize(file_path)
                                        with open(file_path, 'wb') as f:
                                            for _ in range(3):
                                                f.seek(0)
                                                f.write(os.urandom(file_size))
                                                f.flush()
                                                os.fsync(f.fileno())
                                except:
                                    pass
                        
                        # Remove directory
                        shutil.rmtree(data_dir, ignore_errors=True)
                    
                    # Clear all GUI elements
                    for item in self.key_tree.get_children():
                        self.key_tree.delete(item)
                    
                    for item in self.contacts_tree.get_children():
                        self.contacts_tree.delete(item)
                    
                    for item in self.history_tree.get_children():
                        self.history_tree.delete(item)
                    
                    # Clear text fields
                    self.compose_text.delete(1.0, tk.END)
                    self.encrypted_text.delete(1.0, tk.END)
                    self.key_info_text.delete(1.0, tk.END)
                    self.contact_info_text.delete(1.0, tk.END)
                    
                    # Reset variables
                    self.subject_var.set("")
                    self.recipient_var.set("")
                    self.key_count_var.set("Keys: 0")
                    self.contact_count_var.set("Contacts: 0")
                    
                    # Clear recipient combo
                    self.recipient_combo['values'] = []
                    self.recipient_combo.set("No public keys available")
                    
                    messagebox.showinfo(
                        "EMERGENCY KILL COMPLETE", 
                        "All data has been permanently deleted.\n\n"
                        "The application will now exit for security."
                    )
                    
                    # Exit application
                    self.root.quit()
                    self.root.destroy()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Emergency deletion encountered an error: {str(e)}")
    
    def clear_all_data(self):
        """Clear all application data"""
        result = messagebox.askyesno(
            "Clear All Data",
            "This will delete all keys, messages, contacts, and application data.\n\n"
            "This is less secure than the Emergency Kill Switch but allows you to continue using the application.\n\n"
            "Are you sure you want to continue?"
        )
        
        if result:
            try:
                # Clear clipboard
                try:
                    self.root.clipboard_clear()
                except:
                    pass
                
                # Delete all key files and data
                import shutil
                import os
                
                data_dir = self.key_generator.gnupg_home
                if os.path.exists(data_dir):
                    # Simple deletion (not secure overwrite)
                    shutil.rmtree(data_dir, ignore_errors=True)
                    
                    # Recreate the directory
                    os.makedirs(data_dir, exist_ok=True)
                
                # Reinitialize key generator
                from crypto.key_generator import SecureKeyGenerator
                self.key_generator = SecureKeyGenerator(data_dir)
                
                # Clear all GUI elements
                for item in self.key_tree.get_children():
                    self.key_tree.delete(item)
                
                for item in self.contacts_tree.get_children():
                    self.contacts_tree.delete(item)
                
                for item in self.history_tree.get_children():
                    self.history_tree.delete(item)
                
                # Clear text fields
                self.compose_text.delete(1.0, tk.END)
                self.encrypted_text.delete(1.0, tk.END)
                self.key_info_text.delete(1.0, tk.END)
                self.contact_info_text.delete(1.0, tk.END)
                
                # Reset variables
                self.subject_var.set("")
                self.recipient_var.set("")
                self.key_count_var.set("Keys: 0")
                self.contact_count_var.set("Contacts: 0")
                
                # Clear recipient combo
                self.recipient_combo['values'] = []
                self.recipient_combo.set("No public keys available")
                
                messagebox.showinfo(
                    "Data Cleared", 
                    "All application data has been cleared.\n\n"
                    "You can now start fresh with new keys and contacts."
                )
                
                self.status_var.set("All data cleared - ready for fresh start")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear data: {str(e)}")
    
    def on_key_selected(self, event):
        """Handle key selection in the tree"""
        selection = self.key_tree.selection()
        if selection:
            # Get selected item
            item = selection[0]
            key_values = self.key_tree.item(item, 'values')
            if len(key_values) < 4:
                return
                
            key_type = key_values[0]  # Type (Public/Private)
            key_name = key_values[1]  # Name
            key_email = key_values[2] # Email
            key_id = key_values[3]    # Key ID (last 8 chars)
            
            # Update key info display
            self.key_info_text.delete(1.0, tk.END)
            
            try:
                # Get key details based on type
                if key_type == "Public":
                    keys = self.key_generator.list_keys(secret=False)
                else:
                    keys = self.key_generator.list_keys(secret=True)
                
                # Find the selected key by key ID (more reliable than name/email matching)
                selected_key = None
                for key in keys:
                    if key['keyid'].endswith(key_id):
                        selected_key = key
                        break
                
                if selected_key:
                    # For private keys, require passphrase
                    if key_type == "Private":
                        from tkinter import simpledialog
                        passphrase = simpledialog.askstring(
                            "Private Key Access", 
                            "Enter passphrase to view private key information:",
                            show='*'
                        )
                        if not passphrase:
                            self.key_info_text.insert(tk.END, "❌ Private key information access cancelled.\n\nPassphrase required to view private key details.")
                            return
                        
                        # Verify passphrase by attempting to use the key
                        try:
                            # Test the passphrase by trying to export the private key
                            test_result = self.key_generator.export_private_key(selected_key['fingerprint'], passphrase)
                            if not test_result.get('success', False):
                                self.key_info_text.insert(tk.END, "❌ Incorrect passphrase.\n\nCannot display private key information.")
                                return
                        except Exception as e:
                            self.key_info_text.insert(tk.END, f"❌ Passphrase verification failed.\n\nError: {str(e)}")
                            return
                    
                    # Display key information
                    info_text = f"🔑 {key_type} Key Information\n"
                    info_text += "=" * 50 + "\n\n"
                    
                    # Basic information
                    info_text += f"📋 Key ID: {selected_key.get('keyid', 'N/A')}\n"
                    info_text += f"🔍 Fingerprint: {selected_key.get('fingerprint', 'N/A')}\n"
                    info_text += f"🔐 Algorithm: {selected_key.get('algo', 'RSA')}\n"
                    info_text += f"📏 Key Length: {selected_key.get('length', 'N/A')} bits\n"
                    
                    # User IDs
                    if selected_key.get('uids'):
                        info_text += f"\n👤 User IDs:\n"
                        for uid in selected_key['uids']:
                            info_text += f"   • {uid}\n"
                    
                    # Creation date
                    if selected_key.get('created') or selected_key.get('date'):
                        creation_timestamp = selected_key.get('created') or selected_key.get('date')
                        try:
                            import datetime
                            if isinstance(creation_timestamp, str):
                                # Try to parse as timestamp
                                creation_timestamp = float(creation_timestamp)
                            creation_date = datetime.datetime.fromtimestamp(creation_timestamp)
                            info_text += f"\n📅 Created: {creation_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
                        except:
                            info_text += f"\n📅 Created: {creation_timestamp}\n"
                    
                    # Expiration
                    if selected_key.get('expires'):
                        if selected_key['expires'] == '' or selected_key['expires'] == '0':
                            info_text += f"⏰ Expires: Never\n"
                        else:
                            try:
                                import datetime
                                exp_timestamp = float(selected_key['expires'])
                                exp_date = datetime.datetime.fromtimestamp(exp_timestamp)
                                info_text += f"⏰ Expires: {exp_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
                            except:
                                info_text += f"⏰ Expires: {selected_key['expires']}\n"
                    
                    # Trust level
                    if selected_key.get('trust'):
                        trust_levels = {
                            'o': 'Unknown',
                            'i': 'Invalid',
                            'd': 'Disabled',
                            'r': 'Revoked',
                            'e': 'Expired',
                            '-': 'Unknown',
                            'q': 'Undefined',
                            'n': 'Never',
                            'm': 'Marginal',
                            'f': 'Full',
                            'u': 'Ultimate'
                        }
                        trust = trust_levels.get(selected_key['trust'], selected_key['trust'])
                        info_text += f"🛡️ Trust Level: {trust}\n"
                    
                    # Additional security info
                    info_text += f"\n🔒 Security Information:\n"
                    info_text += f"   • Key Type: {key_type}\n"
                    
                    if key_type == "Private":
                        info_text += f"   • Status: Private key available for decryption\n"
                        info_text += f"   • Usage: Can decrypt messages and sign data\n"
                    else:
                        info_text += f"   • Status: Public key only\n"
                        info_text += f"   • Usage: Can encrypt messages for this recipient\n"
                    
                    # Usage instructions
                    info_text += f"\n📖 Usage Instructions:\n"
                    if key_type == "Private":
                        info_text += f"   • Use this key to decrypt messages sent to you\n"
                        info_text += f"   • Export the public key to share with others\n"
                        info_text += f"   • Keep the private key secure and never share it\n"
                    else:
                        info_text += f"   • Use this key to encrypt messages for the recipient\n"
                        info_text += f"   • This is someone else's public key\n"
                        info_text += f"   • You cannot decrypt messages with this key\n"
                    
                    self.key_info_text.insert(tk.END, info_text)
                else:
                    self.key_info_text.insert(tk.END, "❌ Key information not found\n\nThe selected key could not be located in the keyring.")
                    
            except Exception as e:
                error_text = f"❌ Error loading key information:\n{str(e)}\n\nPlease try refreshing the key list."
                self.key_info_text.insert(tk.END, error_text)
        else:
            # No selection
            self.key_info_text.delete(1.0, tk.END)
            self.key_info_text.insert(tk.END, "Select a key from the list above to view detailed information")
    
    def refresh_key_list(self):
        """Refresh the key list"""
        # Clear current items
        for item in self.key_tree.get_children():
            self.key_tree.delete(item)
        
        # Load keys from backend
        try:
            public_keys = self.key_generator.list_keys(secret=False)
            private_keys = self.key_generator.list_keys(secret=True)
            
            # Load contacts to get proper names
            contacts = self.load_contacts()
            
            # Create fingerprint to contact name mapping
            fingerprint_to_name = {}
            for fingerprint, contact_info in contacts.items():
                fingerprint_to_name[fingerprint] = contact_info['name']
            
            # Add public keys
            for key in public_keys:
                # Try to get contact name first, fallback to key UID
                display_name = fingerprint_to_name.get(key['fingerprint'], None)
                
                if not display_name:
                    # Fallback to parsing UID
                    name = key['uids'][0] if key['uids'] else 'Unknown'
                    if '<' in name and '>' in name:
                        display_name = name.split('<')[0].strip()
                    else:
                        display_name = name
                
                # Extract email from UID
                email = ''
                if key['uids']:
                    uid = key['uids'][0]
                    if '<' in uid and '>' in uid:
                        email = uid.split('<')[1].replace('>', '').strip()
                
                self.key_tree.insert('', 'end', values=(
                    'Public',
                    display_name,
                    email,
                    key['keyid'][-8:],  # Last 8 chars of key ID
                    key['date']
                ))
            
            # Add private keys
            for key in private_keys:
                # Try to get contact name first, fallback to key UID
                display_name = fingerprint_to_name.get(key['fingerprint'], None)
                
                if not display_name:
                    # Fallback to parsing UID
                    name = key['uids'][0] if key['uids'] else 'Unknown'
                    if '<' in name and '>' in name:
                        display_name = name.split('<')[0].strip()
                    else:
                        display_name = name
                
                # Extract email from UID
                email = ''
                if key['uids']:
                    uid = key['uids'][0]
                    if '<' in uid and '>' in uid:
                        email = uid.split('<')[1].replace('>', '').strip()
                
                self.key_tree.insert('', 'end', values=(
                    'Private',
                    display_name,
                    email,
                    key['keyid'][-8:],  # Last 8 chars of key ID
                    key['date']
                ))
            
            # Update status
            total_keys = len(public_keys) + len(private_keys)
            self.key_count_var.set(f"Keys: {total_keys}")
            self.status_var.set("Key list refreshed")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh key list: {str(e)}")
    
    def show_how_we_built_this(self):
        """Show the How We Built This documentation"""
        doc_window = tk.Toplevel(self.root)
        doc_window.title("How We Built This - PGP Encryption Tool v2.1")
        doc_window.geometry("900x700")
        doc_window.resizable(True, True)
        
        # Make it modal
        doc_window.transient(self.root)
        doc_window.grab_set()
        
        # Center the window
        doc_window.update_idletasks()
        x = (doc_window.winfo_screenwidth() // 2) - (900 // 2)
        y = (doc_window.winfo_screenheight() // 2) - (700 // 2)
        doc_window.geometry(f"900x700+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(doc_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Header
        header_label = ttk.Label(
            main_frame, 
            text="How We Built This - Technical Documentation", 
            font=('Arial', 16, 'bold')
        )
        header_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg='#f8f9fa',
            relief=tk.SUNKEN,
            borderwidth=2,
            padx=10,
            pady=10
        )
        
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Load and display documentation
        try:
            doc_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "HOW_WE_BUILT_THIS.md")
            if os.path.exists(doc_path):
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                text_widget.insert(tk.END, content)
            else:
                text_widget.insert(tk.END, 
                    "📚 How We Built This - PGP Encryption Tool v2.1\n\n"
                    "Documentation file not found. This would normally contain:\n\n"
                    "• Technical architecture details\n"
                    "• Development process and methodology\n"
                    "• Security considerations and threat model\n"
                    "• Cryptographic implementation details\n"
                    "• Performance optimization strategies\n"
                    "• Testing and quality assurance procedures\n"
                    "• Future enhancement roadmap\n\n"
                    f"Developer: {APP_AUTHOR}\n"
                    f"Version: {APP_VERSION}\n"
                    "Date: January 2025"
                )
        except Exception as e:
            text_widget.insert(tk.END, f"Error loading documentation: {str(e)}")
        
        text_widget.config(state=tk.DISABLED)
        
        # Close button
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=(10, 0))
        
        ttk.Button(
            button_frame, 
            text="Close", 
            command=doc_window.destroy
        ).pack()
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About", 
            f"{APP_NAME} v{APP_VERSION}\n"
            f"Developed by {APP_AUTHOR}\n\n"
            "A secure offline PGP encryption tool\n\n"
            "Features:\n"
            "• PGP key generation with entropy collection\n"
            "• Message encryption/decryption\n"
            "• Key management and backup\n"
            "• Emergency data deletion\n"
            "• Complete offline operation"
        )
    
    def on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            # Cleanup
            try:
                self.key_generator.cleanup()
            except:
                pass
            self.root.destroy()
    
    # Contacts Management Methods
    def add_contact_dialog(self):
        """Show add contact dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Contact")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Contact name
        ttk.Label(main_frame, text="Contact Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(main_frame, textvariable=name_var, width=40)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # IRC nickname (optional)
        ttk.Label(main_frame, text="IRC Nickname (optional):").grid(row=1, column=0, sticky=tk.W, pady=5)
        irc_nick_var = tk.StringVar()
        irc_nick_entry = ttk.Entry(main_frame, textvariable=irc_nick_var, width=40)
        irc_nick_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Public key
        ttk.Label(main_frame, text="Public Key:").grid(row=2, column=0, sticky=tk.NW, pady=5)
        key_text = tk.Text(main_frame, height=10, width=50)
        key_scroll = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=key_text.yview)
        key_text.configure(yscrollcommand=key_scroll.set)
        key_text.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(10, 0))
        key_scroll.grid(row=2, column=2, sticky=(tk.N, tk.S), pady=5)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(20, 0))
        
        def save_contact():
            name = name_var.get().strip()
            irc_nickname = irc_nick_var.get().strip()
            public_key = key_text.get(1.0, tk.END).strip()
            
            if not name:
                messagebox.showerror("Error", "Please enter a contact name")
                return
            
            if not public_key:
                messagebox.showerror("Error", "Please enter the contact's public key")
                return
            
            # Import the public key
            result = self.key_generator.import_key(public_key)
            if result['success']:
                # Save contact info with IRC nickname
                self.save_contact_info(name, result['fingerprint'], irc_nickname)
                messagebox.showinfo("Success", f"Contact '{name}' added successfully!")
                dialog.destroy()
                self.refresh_contacts_list()
                self.refresh_key_list()  # Refresh keys to show contact name
                self.update_recipient_list()  # Update recipient list
                if hasattr(self, 'refresh_chat_contacts'):
                    self.refresh_chat_contacts()  # Update chat contacts
            else:
                messagebox.showerror("Error", f"Failed to import key: {result['error']}")
        
        ttk.Button(button_frame, text="Save Contact", command=save_contact).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT)
        
        # Focus on name entry
        name_entry.focus()
    
    def save_contact_info(self, name, fingerprint, irc_nickname=""):
        """Save contact information to encrypted file"""
        import datetime
        
        # Load existing contacts
        contacts = self.load_contacts()
        
        # Add new contact
        contacts[fingerprint] = {
            "name": name,
            "fingerprint": fingerprint,
            "date_added": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "irc_nickname": irc_nickname  # Add IRC nickname field for chat integration
        }
        
        # Try to get and store the public key for chat functionality
        try:
            export_result = self.key_generator.export_public_key(fingerprint)
            if export_result.get('success'):
                contacts[fingerprint]['public_key'] = export_result.get('public_key')
        except Exception as e:
            print(f"Warning: Could not export public key for contact: {e}")
        
        
        # Save contacts using encrypted storage
        try:
            if hasattr(self.key_generator, 'data_manager') and self.key_generator.data_manager:
                self.key_generator.data_manager.save_data("contacts.json", contacts)
            else:
                # Fallback to unencrypted storage if data manager not available
                import json
                contacts_file = os.path.join(self.key_generator.gnupg_home, "contacts.json")
                with open(contacts_file, 'w') as f:
                    json.dump(contacts, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save contact: {str(e)}")
    
    def load_contacts(self):
        """Load contacts from encrypted file"""
        try:
            if hasattr(self.key_generator, 'data_manager') and self.key_generator.data_manager:
                # Try to load from encrypted storage first
                contacts = self.key_generator.data_manager.load_data("contacts.json", {})
                if contacts:
                    return contacts
            
            # Fallback to unencrypted file (for migration)
            import json
            contacts_file = os.path.join(self.key_generator.gnupg_home, "contacts.json")
            
            if os.path.exists(contacts_file):
                try:
                    with open(contacts_file, 'r') as f:
                        contacts = json.load(f)
                    
                    # Migrate to encrypted storage if data manager is available
                    if hasattr(self.key_generator, 'data_manager') and self.key_generator.data_manager and contacts:
                        self.key_generator.data_manager.save_data("contacts.json", contacts)
                        # Optionally remove old unencrypted file
                        # os.remove(contacts_file)
                    
                    return contacts
                except (json.JSONDecodeError, IOError):
                    pass
        except Exception as e:
            print(f"Warning: Failed to load contacts: {e}")
        
        return {}
    
    def refresh_contacts_list(self):
        """Refresh the contacts list"""
        # Clear current items
        for item in self.contacts_tree.get_children():
            self.contacts_tree.delete(item)
        
        try:
            contacts = self.load_contacts()
            public_keys = self.key_generator.list_keys(secret=False)
            
            # Create a map of fingerprints to key info
            key_map = {key['fingerprint']: key for key in public_keys}
            
            # Add contacts to tree
            for fingerprint, contact_info in contacts.items():
                if fingerprint in key_map:
                    key_info = key_map[fingerprint]
                    irc_nick = contact_info.get('irc_nickname', '')
                    display_nick = irc_nick if irc_nick else '(none)'
                    self.contacts_tree.insert('', 'end', values=(
                        contact_info['name'],
                        key_info['keyid'][-8:],  # Last 8 chars of key ID
                        display_nick,  # IRC nickname
                        contact_info.get('date_added', contact_info.get('added_date', 'Unknown'))
                    ), tags=(fingerprint,))
            
            # Update status
            self.contact_count_var.set(f"Contacts: {len(contacts)}")
            self.status_var.set("Contacts list refreshed")
            
            # Also update recipient list in compose message
            self.update_recipient_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh contacts list: {str(e)}")
    
    def remove_contact(self):
        """Remove selected contact"""
        selection = self.contacts_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a contact to remove")
            return
        
        item = selection[0]
        contact_name = self.contacts_tree.item(item)['values'][0]
        fingerprint = self.contacts_tree.item(item)['tags'][0]
        
        result = messagebox.askyesno(
            "Delete Contact", 
            f"Are you sure you want to delete contact '{contact_name}'?\n\n"
            "This will permanently remove the contact from your list.\n"
            "The associated public key will remain in your keyring."
        )
        
        if result:
            try:
                # Load contacts using encrypted storage
                contacts = self.load_contacts()
                if fingerprint in contacts:
                    del contacts[fingerprint]
                    
                    # Save using encrypted storage
                    if hasattr(self.key_generator, 'data_manager') and self.key_generator.data_manager:
                        self.key_generator.data_manager.save_data("contacts.json", contacts)
                    else:
                        # Fallback to unencrypted storage if data manager not available
                        import json
                        contacts_file = os.path.join(self.key_generator.gnupg_home, "contacts.json")
                        with open(contacts_file, 'w') as f:
                            json.dump(contacts, f, indent=2)
                    
                    # Refresh all contact-related lists
                    self.refresh_contacts_list()
                    self.update_recipient_list()
                    if hasattr(self, 'refresh_chat_contacts'):
                        self.refresh_chat_contacts()
                    
                    messagebox.showinfo("Success", f"Contact '{contact_name}' deleted successfully!")
                else:
                    messagebox.showwarning("Warning", "Contact not found in database")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete contact: {str(e)}")
    
    def delete_contact_with_key(self):
        """Delete selected contact and optionally remove the associated key"""
        selection = self.contacts_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a contact to delete")
            return
        
        item = selection[0]
        contact_name = self.contacts_tree.item(item)['values'][0]
        fingerprint = self.contacts_tree.item(item)['tags'][0]
        
        # Create custom dialog for deletion options
        dialog = tk.Toplevel(self.root)
        dialog.title("Delete Contact")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Warning message
        ttk.Label(main_frame, text=f"Delete contact '{contact_name}'?", 
                 font=('Arial', 10, 'bold')).pack(pady=(0, 10))
        
        ttk.Label(main_frame, text="Choose deletion options:", 
                 font=('Arial', 9)).pack(pady=(0, 15))
        
        # Options
        delete_contact_var = tk.BooleanVar(value=True)
        delete_key_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(main_frame, text="Delete contact from contact list", 
                       variable=delete_contact_var, state="disabled").pack(anchor=tk.W, pady=2)
        
        ttk.Checkbutton(main_frame, text="Also delete the associated public key from keyring", 
                       variable=delete_key_var).pack(anchor=tk.W, pady=2)
        
        # Warning for key deletion
        warning_frame = ttk.Frame(main_frame)
        warning_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(warning_frame, text="⚠️ Warning:", foreground="red", 
                 font=('Arial', 8, 'bold')).pack(anchor=tk.W)
        ttk.Label(warning_frame, text="Deleting the key will prevent decrypting messages from this contact.", 
                 font=('Arial', 8), wraplength=350).pack(anchor=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(20, 0))
        
        def confirm_delete():
            try:
                # Delete contact
                if delete_contact_var.get():
                    contacts = self.load_contacts()
                    if fingerprint in contacts:
                        del contacts[fingerprint]
                        
                        # Save using encrypted storage
                        if hasattr(self.key_generator, 'data_manager') and self.key_generator.data_manager:
                            self.key_generator.data_manager.save_data("contacts.json", contacts)
                        else:
                            # Fallback to unencrypted storage if data manager not available
                            import json
                            contacts_file = os.path.join(self.key_generator.gnupg_home, "contacts.json")
                            with open(contacts_file, 'w') as f:
                                json.dump(contacts, f, indent=2)
                
                # Delete key if requested
                if delete_key_var.get():
                    try:
                        result = self.key_generator.delete_key(fingerprint)
                        if not result.get('success', False):
                            messagebox.showwarning("Warning", f"Contact deleted but failed to delete key: {result.get('error', 'Unknown error')}")
                    except Exception as e:
                        messagebox.showwarning("Warning", f"Contact deleted but failed to delete key: {str(e)}")
                
                # Refresh all lists
                self.refresh_contacts_list()
                self.update_recipient_list()
                self.refresh_key_list()
                if hasattr(self, 'refresh_chat_contacts'):
                    self.refresh_chat_contacts()
                
                dialog.destroy()
                
                action_text = "Contact deleted"
                if delete_key_var.get():
                    action_text += " and key removed"
                messagebox.showinfo("Success", f"{action_text} successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete contact: {str(e)}")
        
        ttk.Button(button_frame, text="Delete", command=confirm_delete).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT)
    
    def import_contact_key(self):
        """Import a public key file for a contact"""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="Import Public Key",
            filetypes=[
                ("PGP Key files", "*.asc *.pgp *.gpg"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    key_data = f.read()
                
                # Show add contact dialog with pre-filled key
                self.add_contact_dialog_with_key(key_data)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read key file: {str(e)}")
    
    def export_contact_card(self):
        """Export selected contact as encrypted contact card"""
        selection = self.contacts_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a contact to export")
            return
        
        item = selection[0]
        contact_name = self.contacts_tree.item(item)['values'][0]
        fingerprint = self.contacts_tree.item(item)['tags'][0]
        
        try:
            # Get contact information
            contacts = self.load_contacts()
            if fingerprint not in contacts:
                messagebox.showerror("Error", "Contact not found in database")
                return
            
            contact_info = contacts[fingerprint]
            
            # Get public key
            public_keys = self.key_generator.list_keys(secret=False)
            public_key_data = None
            
            for key in public_keys:
                if key['fingerprint'] == fingerprint:
                    # Export the public key
                    export_result = self.key_generator.export_public_key(fingerprint)
                    if export_result.get('success'):
                        public_key_data = export_result.get('public_key', '')
                    break
            
            if not public_key_data:
                messagebox.showerror("Error", "Could not export public key for contact")
                return
            
            # Show export dialog
            self.show_export_contact_card_dialog(contact_info, public_key_data)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to prepare contact card export: {str(e)}")
    
    def show_export_contact_card_dialog(self, contact_info, public_key_data):
        """Show dialog for exporting contact card"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Export Contact Card")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="Export Contact Card", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 15))
        
        # Contact info frame
        info_frame = ttk.LabelFrame(main_frame, text="Contact Information", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(info_frame, text=f"Name: {contact_info['name']}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"IRC Nickname: {contact_info.get('irc_nickname', 'Not set')}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Email: {contact_info.get('email', 'Not set')}").pack(anchor=tk.W)
        
        # Export options frame
        options_frame = ttk.LabelFrame(main_frame, text="Export Options", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Email field
        ttk.Label(options_frame, text="Email (optional):").pack(anchor=tk.W)
        email_var = tk.StringVar(value=contact_info.get('email', ''))
        email_entry = ttk.Entry(options_frame, textvariable=email_var, width=40)
        email_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Notes field
        ttk.Label(options_frame, text="Notes (optional):").pack(anchor=tk.W)
        notes_text = tk.Text(options_frame, height=3, width=40)
        notes_text.pack(fill=tk.X, pady=(0, 10))
        
        # Password frame
        password_frame = ttk.LabelFrame(main_frame, text="Encryption Options", padding="10")
        password_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Checkbox for password protection
        use_password_var = tk.BooleanVar(value=True)
        password_checkbox = ttk.Checkbutton(
            password_frame, 
            text="Encrypt contact card with password (recommended)", 
            variable=use_password_var,
            command=lambda: toggle_password_fields()
        )
        password_checkbox.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(password_frame, text="Password to encrypt contact card:").pack(anchor=tk.W)
        password_var = tk.StringVar()
        password_entry = ttk.Entry(password_frame, textvariable=password_var, show="*", width=40)
        password_entry.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(password_frame, text="Confirm password:").pack(anchor=tk.W)
        confirm_var = tk.StringVar()
        confirm_entry = ttk.Entry(password_frame, textvariable=confirm_var, show="*", width=40)
        confirm_entry.pack(fill=tk.X)
        
        def toggle_password_fields():
            """Enable/disable password fields based on checkbox"""
            if use_password_var.get():
                password_entry.config(state='normal')
                confirm_entry.config(state='normal')
            else:
                password_entry.config(state='disabled')
                confirm_entry.config(state='disabled')
                password_var.set('')
                confirm_var.set('')
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(15, 0))
        
        def export_card():
            password = password_var.get() if use_password_var.get() else None
            confirm = confirm_var.get() if use_password_var.get() else None
            
            # Validate password only if encryption is enabled
            if use_password_var.get():
                if not password:
                    messagebox.showerror("Error", "Please enter a password")
                    return
                
                if password != confirm:
                    messagebox.showerror("Error", "Passwords do not match")
                    return
                
                if len(password) < 6:
                    messagebox.showerror("Error", "Password must be at least 6 characters")
                    return
            
            try:
                from tkinter import filedialog
                from security.contact_card import ContactCardManager, ContactCard
                
                # Create contact card
                card_manager = ContactCardManager()
                contact_card = ContactCard(
                    name=contact_info['name'],
                    irc_nickname=contact_info.get('irc_nickname', ''),
                    public_key=public_key_data,
                    email=email_var.get(),
                    notes=notes_text.get("1.0", tk.END).strip()
                )
                
                # Choose save location
                file_path = filedialog.asksaveasfilename(
                    title="Save Contact Card",
                    defaultextension=".pgpcard",
                    filetypes=[
                        ("PGP Contact Cards", "*.pgpcard"),
                        ("All files", "*.*")
                    ],
                    initialfile=f"{contact_info['name'].replace(' ', '_')}_contact_card.pgpcard"
                )
                
                if file_path:
                    # Export contact card
                    card_manager.export_contact_card(contact_card, file_path, password)
                    
                    dialog.destroy()
                    encryption_status = "encrypted" if password else "unencrypted"
                    messagebox.showinfo("Success", 
                                      f"Contact card exported successfully!\n\n"
                                      f"File: {file_path}\n"
                                      f"Type: {encryption_status.title()} contact card\n\n"
                                      f"Share this {encryption_status} file with others to exchange contact information.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export contact card: {str(e)}")
        
        ttk.Button(button_frame, text="Export", command=export_card).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT)
    
    def import_contact_card(self):
        """Import contact from encrypted contact card"""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="Import Contact Card",
            filetypes=[
                ("PGP Contact Cards", "*.pgpcard"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                from security.contact_card import ContactCardManager
                
                card_manager = ContactCardManager()
                
                # Validate file first
                is_valid, info = card_manager.validate_contact_card_file(file_path)
                if not is_valid:
                    messagebox.showerror("Error", f"Invalid contact card file:\n{info}")
                    return
                
                # Show import dialog
                self.show_import_contact_card_dialog(file_path, info)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read contact card: {str(e)}")
    
    def show_import_contact_card_dialog(self, file_path, card_info):
        """Show dialog for importing contact card"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Import Contact Card")
        dialog.geometry("450x350")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="Import Contact Card", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 15))
        
        # File info frame
        info_frame = ttk.LabelFrame(main_frame, text="Contact Card Information", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(info_frame, text=f"File: {os.path.basename(file_path)}").pack(anchor=tk.W)
        for line in card_info.split('\n'):
            if line.strip():
                ttk.Label(info_frame, text=line).pack(anchor=tk.W)
        
        # Check if card is encrypted
        is_encrypted = "Format: Encrypted" in card_info
        
        # Password frame (only show if encrypted)
        password_frame = None
        password_var = None
        password_entry = None
        
        if is_encrypted:
            password_frame = ttk.LabelFrame(main_frame, text="Decryption Password", padding="10")
            password_frame.pack(fill=tk.X, pady=(0, 15))
            
            ttk.Label(password_frame, text="Enter password to decrypt contact card:").pack(anchor=tk.W)
            password_var = tk.StringVar()
            password_entry = ttk.Entry(password_frame, textvariable=password_var, show="*", width=40)
            password_entry.pack(fill=tk.X, pady=(5, 0))
            password_entry.focus()
        else:
            # For unencrypted cards, show info that no password is needed
            no_password_frame = ttk.LabelFrame(main_frame, text="Import Information", padding="10")
            no_password_frame.pack(fill=tk.X, pady=(0, 15))
            ttk.Label(no_password_frame, text="This contact card is unencrypted and ready to import.").pack(anchor=tk.W)
        
        # Preview frame (initially hidden)
        preview_frame = ttk.LabelFrame(main_frame, text="Contact Preview", padding="10")
        preview_labels = {}
        
        def create_preview_labels():
            preview_labels['name'] = ttk.Label(preview_frame, text="")
            preview_labels['name'].pack(anchor=tk.W)
            preview_labels['irc'] = ttk.Label(preview_frame, text="")
            preview_labels['irc'].pack(anchor=tk.W)
            preview_labels['email'] = ttk.Label(preview_frame, text="")
            preview_labels['email'].pack(anchor=tk.W)
            preview_labels['notes'] = ttk.Label(preview_frame, text="")
            preview_labels['notes'].pack(anchor=tk.W)
        
        create_preview_labels()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(15, 0))
        
        contact_card_data = None
        
        def preview_card():
            nonlocal contact_card_data
            password = password_var.get() if is_encrypted and password_var else None
            
            # Only require password for encrypted cards
            if is_encrypted and not password:
                messagebox.showerror("Error", "Please enter a password")
                return
            
            try:
                from security.contact_card import ContactCardManager
                
                card_manager = ContactCardManager()
                contact_card_data = card_manager.import_contact_card(file_path, password)
                
                # Update preview
                preview_labels['name'].config(text=f"Name: {contact_card_data.name}")
                preview_labels['irc'].config(text=f"IRC Nickname: {contact_card_data.irc_nickname or 'Not set'}")
                preview_labels['email'].config(text=f"Email: {contact_card_data.email or 'Not set'}")
                notes_text = contact_card_data.notes[:50] + "..." if len(contact_card_data.notes) > 50 else contact_card_data.notes
                preview_labels['notes'].config(text=f"Notes: {notes_text or 'None'}")
                
                # Show preview frame
                preview_frame.pack(fill=tk.X, pady=(0, 15))
                
                # Enable import button
                import_button.config(state=tk.NORMAL)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to decrypt contact card: {str(e)}")
                contact_card_data = None
                preview_frame.pack_forget()
                import_button.config(state=tk.DISABLED)
        
        def import_card():
            if not contact_card_data:
                messagebox.showerror("Error", "Please preview the contact card first")
                return
            
            try:
                # Import the public key
                import_result = self.key_generator.import_key(contact_card_data.public_key)
                
                if not import_result.get('success'):
                    messagebox.showerror("Error", f"Failed to import public key: {import_result.get('error', 'Unknown error')}")
                    return
                
                fingerprint = import_result.get('fingerprint')
                if not fingerprint:
                    messagebox.showerror("Error", "Could not get key fingerprint")
                    return
                
                # Add contact to database
                contacts = self.load_contacts()
                contacts[fingerprint] = {
                    'name': contact_card_data.name,
                    'irc_nickname': contact_card_data.irc_nickname,
                    'email': contact_card_data.email,
                    'notes': contact_card_data.notes,
                    'date_added': time.strftime("%Y-%m-%d %H:%M:%S"),
                    'imported_from_card': True,
                    'public_key': contact_card_data.public_key  # Store public key for chat functionality
                }
                
                # Save contacts using encrypted storage
                if hasattr(self.key_generator, 'data_manager') and self.key_generator.data_manager:
                    self.key_generator.data_manager.save_data("contacts.json", contacts)
                else:
                    # Fallback to unencrypted storage if data manager not available
                    import json
                    contacts_file = os.path.join(self.key_generator.gnupg_home, "contacts.json")
                    with open(contacts_file, 'w') as f:
                        json.dump(contacts, f, indent=2)
                
                # Refresh all lists
                self.refresh_contacts_list()
                self.update_recipient_list()
                self.refresh_key_list()
                if hasattr(self, 'refresh_chat_contacts'):
                    self.refresh_chat_contacts()
                
                dialog.destroy()
                messagebox.showinfo("Success", 
                                  f"Contact card imported successfully!\n\n"
                                  f"Contact: {contact_card_data.name}\n"
                                  f"IRC Nickname: {contact_card_data.irc_nickname or 'Not set'}\n"
                                  f"Public key imported and contact added to database.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import contact: {str(e)}")
        
        # Update button text based on encryption status
        preview_text = "Preview" if is_encrypted else "Load Contact"
        preview_button = ttk.Button(button_frame, text=preview_text, command=preview_card)
        preview_button.pack(side=tk.LEFT, padx=(0, 10))
        
        import_button = ttk.Button(button_frame, text="Import", command=import_card, state=tk.DISABLED)
        import_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT)
        
        # For unencrypted cards, auto-load the contact
        if not is_encrypted:
            dialog.after(100, preview_card)  # Auto-load after dialog is shown
        
        # Bind Enter key to preview/load
        def on_enter(event):
            if contact_card_data is None:
                preview_card()
            else:
                import_card()
        
        # Only bind Enter key if password entry exists (encrypted cards)
        if password_entry:
            password_entry.bind('<Return>', on_enter)
    
    def add_contact_dialog_with_key(self, key_data):
        """Show add contact dialog with pre-filled key data"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Contact")
        dialog.geometry("400x350")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Contact name
        ttk.Label(main_frame, text="Contact Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(main_frame, textvariable=name_var, width=40)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # IRC nickname (optional)
        ttk.Label(main_frame, text="IRC Nickname (optional):").grid(row=1, column=0, sticky=tk.W, pady=5)
        irc_nick_var = tk.StringVar()
        irc_nick_entry = ttk.Entry(main_frame, textvariable=irc_nick_var, width=40)
        irc_nick_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Public key (pre-filled)
        ttk.Label(main_frame, text="Public Key:").grid(row=2, column=0, sticky=tk.NW, pady=5)
        key_text = tk.Text(main_frame, height=10, width=50)
        key_scroll = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=key_text.yview)
        key_text.configure(yscrollcommand=key_scroll.set)
        key_text.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(10, 0))
        key_scroll.grid(row=2, column=2, sticky=(tk.N, tk.S), pady=5)
        
        # Pre-fill the key data
        key_text.insert(1.0, key_data)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(20, 0))
        
        def save_contact():
            name = name_var.get().strip()
            irc_nickname = irc_nick_var.get().strip()
            public_key = key_text.get(1.0, tk.END).strip()
            
            if not name:
                messagebox.showerror("Error", "Please enter a contact name")
                return
            
            if not public_key:
                messagebox.showerror("Error", "Please enter the contact's public key")
                return
            
            # Import the public key
            result = self.key_generator.import_key(public_key)
            if result['success']:
                # Save contact info with IRC nickname
                self.save_contact_info(name, result['fingerprint'], irc_nickname)
                messagebox.showinfo("Success", f"Contact '{name}' added successfully!")
                dialog.destroy()
                self.refresh_contacts_list()
                self.refresh_key_list()  # Refresh keys to show contact name
                self.update_recipient_list()  # Update recipient list
                if hasattr(self, 'refresh_chat_contacts'):
                    self.refresh_chat_contacts()  # Update chat contacts
            else:
                messagebox.showerror("Error", f"Failed to import key: {result['error']}")
        
        ttk.Button(button_frame, text="Save Contact", command=save_contact).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT)
        
        # Focus on name entry
        name_entry.focus()
    
    def on_contact_selected(self, event):
        """Handle contact selection"""
        selection = self.contacts_tree.selection()
        if selection:
            item = selection[0]
            contact_name = self.contacts_tree.item(item)['values'][0]
            key_id = self.contacts_tree.item(item)['values'][1]
            added_date = self.contacts_tree.item(item)['values'][2]
            fingerprint = self.contacts_tree.item(item)['tags'][0]
            
            # Update contact info display
            self.contact_info_text.delete(1.0, tk.END)
            info = f"Contact: {contact_name}\n"
            info += f"Key ID: {key_id}\n"
            info += f"Added: {added_date}\n"
            info += f"Fingerprint: {fingerprint}"
            self.contact_info_text.insert(tk.END, info)

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
        
        # CRITICAL FIX: Get the master password from the login dialog and initialize encryption
        try:
            if hasattr(login_dialog, 'master_password') and login_dialog.master_password:
                master_password = login_dialog.master_password
                print("Debug: Retrieved master password from login dialog")
                
                # Initialize encryption in the key generator's PGP handler
                if hasattr(self.key_generator, 'pgp_handler') and self.key_generator.pgp_handler:
                    # Set master password in the main PGP handler wrapper
                    self.key_generator.pgp_handler.set_master_password(master_password)
                    print("Debug: Master password set in main PGP handler")
                    
                    if hasattr(self.key_generator.pgp_handler, 'handler') and self.key_generator.pgp_handler.handler:
                        # Set master password in the pure Python PGP handler
                        self.key_generator.pgp_handler.handler.set_master_password(master_password)
                        print("Debug: Master password set in PGP handler")
                        
                        # Verify encryption is now initialized
                        if hasattr(self.key_generator.pgp_handler.handler, 'data_manager'):
                            data_manager = self.key_generator.pgp_handler.handler.data_manager
                            if data_manager.encryption:
                                print("Debug: Encryption successfully initialized!")
                            else:
                                print("Debug: Warning - encryption still not initialized")
                    else:
                        print("Debug: No pure Python handler found")
                else:
                    print("Debug: No PGP handler found")
            else:
                print("Debug: No master password found in login dialog")
                
        except Exception as e:
            print(f"Warning: Failed to initialize encryption: {e}")
            import traceback
            traceback.print_exc()
        
        # Load message history
        self.load_message_history()
        
        # Initial setup
        self.refresh_key_list()
        self.refresh_contacts_list()
        
        # FIXED: Initialize chat profiles dropdown properly
        if SECURE_CHAT_AVAILABLE:
            print("Debug: Initializing chat system...")
            # CRITICAL: Ensure encryption is properly initialized for chat system
            self._ensure_chat_encryption_initialized()
            self.refresh_chat_profiles()  # Load available key pairs into profile selector
            self.refresh_chat_contacts()  # Load contacts into chat contacts list
            print("Debug: Chat system initialized")
        
        print("Debug: Starting main window mainloop")
        
        # Start the main loop
        self.root.mainloop()
    
    # ===== SECURE CHAT METHODS =====
    
    def _ensure_chat_encryption_initialized(self):
        """Ensure encryption is properly initialized for chat system access"""
        try:
            print("DEBUG: Checking chat encryption initialization...")
            
            # Check if we have a key generator with PGP handler
            if not hasattr(self, 'key_generator') or not self.key_generator:
                print("DEBUG: No key generator found")
                return False
                
            if not hasattr(self.key_generator, 'pgp_handler') or not self.key_generator.pgp_handler:
                print("DEBUG: No PGP handler found")
                return False
                
            # Check if the PGP handler has the pure Python handler
            if not hasattr(self.key_generator.pgp_handler, 'handler') or not self.key_generator.pgp_handler.handler:
                print("DEBUG: No pure Python handler found")
                return False
                
            # Check if data manager exists and has encryption
            handler = self.key_generator.pgp_handler.handler
            if not hasattr(handler, 'data_manager') or not handler.data_manager:
                print("DEBUG: No data manager found")
                return False
                
            data_manager = handler.data_manager
            if not hasattr(data_manager, 'encryption') or not data_manager.encryption:
                print("DEBUG: Data manager encryption not initialized")
                print("DEBUG: This means keys are encrypted but we can't access them")
                print("DEBUG: The login process should have initialized encryption")
                
                # Try to check if we can access the login dialog's password
                # In a real scenario, we'd need to get this from the login process
                # For now, we'll just indicate the issue
                return False
            else:
                print("DEBUG: Data manager encryption is properly initialized")
                return True
                
        except Exception as e:
            print(f"DEBUG: Error checking encryption initialization: {e}")
            return False
    
    def show_key_coordination_dialog(self):
        """Show the key coordination dialog to help resolve key mismatches"""
        if not SECURE_CHAT_AVAILABLE:
            messagebox.showerror("Error", "Secure chat functionality is not available")
            return
        
        try:
            # Get current profile fingerprint
            current_profile = None
            if hasattr(self, 'secure_chat') and self.secure_chat:
                current_profile = getattr(self.secure_chat, '_current_profile_fingerprint', None)
            
            # Import and show the dialog
            from .key_coordination_dialog import KeyCoordinationDialog
            dialog = KeyCoordinationDialog(self.root, self.key_generator, current_profile)
            result = dialog.show()
            
            # Handle dialog result
            if result and result.get('action') == 'switch_profile':
                fingerprint = result['fingerprint']
                name = result['name']
                
                # Update the chat profile dropdown
                self.refresh_chat_profiles()
                
                # Select the new profile
                for i, value in enumerate(self.chat_profile_combo['values']):
                    if fingerprint[-8:] in value:
                        self.chat_profile_combo.current(i)
                        self.on_chat_profile_changed(None)
                        messagebox.showinfo("Profile Switched", 
                                          f"Chat profile switched to '{name}'\\n\\n"
                                          f"Try receiving messages again with this profile.")
                        break
                        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show key coordination dialog: {str(e)}")

    def generate_chat_nickname(self):
        """Generate a random IRC nickname"""
        prefix = "PGPUser_"
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        nickname = prefix + suffix
        self.chat_nickname_var.set(nickname)
    
    def toggle_chat_connection(self):
        """Toggle IRC connection"""
        if self.secure_chat and self.secure_chat.irc_client.connected:
            self.disconnect_from_chat()
        else:
            self.connect_to_chat()
    
    def connect_to_chat(self):
        """Connect to IRC for secure chat - ENHANCED GUI FIX WITH PASSPHRASE HANDLING"""
        if not SECURE_CHAT_AVAILABLE:
            messagebox.showerror("Error", "Secure chat functionality is not available")
            return
            
        try:
            # Get connection details first
            network = self.chat_network_var.get()
            nickname = self.chat_irc_nickname_var.get().strip()
            
            print(f"DEBUG: GUI connect_to_chat called with network='{network}', nickname='{nickname}'")
            
            if not nickname:
                # Try to get from old nickname field as fallback
                nickname = self.chat_nickname_var.get().strip() if hasattr(self, 'chat_nickname_var') else ""
                print(f"DEBUG: Using fallback nickname: '{nickname}'")
                
            if not nickname:
                print("DEBUG: No nickname provided")
                messagebox.showerror("Error", "Please enter a nickname or select a chat profile")
                return
            
            if not network:
                print("DEBUG: No network selected")
                messagebox.showerror("Error", "Please select an IRC network")
                return
            
            # Initialize secure chat if not already done
            if not self.secure_chat:
                print("DEBUG: Initializing secure chat handler")
                # Get the PGP handler from key generator
                pgp_handler = self.key_generator.pgp_handler
                self.secure_chat = SecureChatHandler(pgp_handler)
                
                # Set up callbacks with enhanced error handling
                def on_message_received(message):
                    try:
                        self.on_chat_message_received(message)
                    except Exception as e:
                        print(f"DEBUG: Error in message callback: {e}")
                
                def on_error(error_msg):
                    try:
                        print(f"DEBUG: IRC Error: {error_msg}")
                        self.on_chat_error(error_msg)
                    except Exception as e:
                        print(f"DEBUG: Error in error callback: {e}")
                
                self.secure_chat.on_message_callback = on_message_received
                self.secure_chat.on_error_callback = on_error
                print("DEBUG: Secure chat handler initialized")
            
            # Set the current passphrase and profile for decryption if we have one
            current_profile = self.chat_profile_var.get()
            if current_profile and hasattr(self, 'chat_profiles'):
                # Find the selected profile data
                selected_profile = None
                for profile in self.chat_profiles:
                    if profile['display'] == current_profile:
                        selected_profile = profile
                        break
                
                if selected_profile:
                    # Set the profile fingerprint for decryption
                    self.secure_chat._current_profile_fingerprint = selected_profile['fingerprint']
                    print(f"DEBUG: Set profile fingerprint for decryption: {selected_profile['fingerprint']}")
                    
                    # If we have a passphrase stored, use it
                    if hasattr(self, '_current_key_passphrase'):
                        self.secure_chat._current_passphrase = self._current_key_passphrase
                        print("DEBUG: Set current passphrase for decryption")
                else:
                    print("DEBUG: Could not find selected profile data")
            else:
                print("DEBUG: No profile selected or no profiles available")
            
            # Set save history preference
            self.secure_chat.save_history = self.chat_save_history_var.get()
            
            # Update UI
            self.chat_status_var.set("Connecting...")
            self.chat_status_label.configure(foreground="orange")
            self.chat_connect_button.configure(text="Connecting...", state="disabled")
            self.root.update()
            
            print(f"DEBUG: Attempting IRC connection to {network} as {nickname}")
            
            # Connect to IRC with enhanced error handling
            try:
                connection_result = self.secure_chat.connect_to_irc(network, nickname)
                print(f"DEBUG: IRC connection result: {connection_result}")
            except Exception as e:
                print(f"DEBUG: Exception during IRC connection: {e}")
                connection_result = False
            
            if connection_result:
                print("DEBUG: Connection initiated, waiting for status check")
                # Wait a moment for connection to establish
                self.root.after(3000, self._check_connection_status)  # Increased timeout
            else:
                # Connection failed immediately
                print("DEBUG: Connection failed immediately")
                self.chat_status_var.set("Connection failed")
                self.chat_status_label.configure(foreground="red")
                self.chat_connect_button.configure(text="Connect", state="normal")
                messagebox.showerror("Connection Error", "Failed to connect to IRC network. Check your internet connection and try again.")
            
        except Exception as e:
            print(f"DEBUG: Exception in connect_to_chat: {e}")
            self.chat_status_var.set("Connection failed")
            self.chat_status_label.configure(foreground="red")
            self.chat_connect_button.configure(text="Connect", state="normal")
            messagebox.showerror("Connection Error", f"Failed to connect: {str(e)}")
    
    def _check_connection_status(self):
        """Check if IRC connection was successful - ENHANCED VERSION"""
        try:
            print("DEBUG: Checking connection status...")
            
            if self.secure_chat and self.secure_chat.is_connected():
                # Connection successful
                network = self.chat_network_var.get()
                nickname = self.chat_irc_nickname_var.get()
                
                print(f"DEBUG: Connection successful to {network} as {nickname}")
                
                self.chat_status_var.set(f"Connected to {network}")
                self.chat_status_label.configure(foreground="green")
                self.chat_connect_button.configure(text="Disconnect", state="normal")
                self.chat_send_button.configure(state="normal")
                
                # Add system message to chat log
                self.add_chat_log_message("SYSTEM", f"Connected to {network} as {nickname}")
                
                # Initialize group chat
                try:
                    if self.initialize_group_chat():
                        self.add_chat_log_message("SYSTEM", "Group chat initialized")
                except Exception as e:
                    print(f"DEBUG: Group chat initialization failed: {e}")
                    
                # Refresh chat contacts to sync with IRC
                try:
                    self.refresh_chat_contacts()
                except Exception as e:
                    print(f"DEBUG: Contact refresh failed: {e}")
                
            else:
                # Connection failed
                print("DEBUG: Connection failed - not connected after timeout")
                self.chat_status_var.set("Connection failed")
                self.chat_status_label.configure(foreground="red")
                self.chat_connect_button.configure(text="Connect", state="normal")
                
                # Show more detailed error message
                error_msg = "Failed to establish IRC connection. This could be due to:\n\n"
                error_msg += "• Network connectivity issues\n"
                error_msg += "• Firewall blocking IRC ports (6667/6697)\n"
                error_msg += "• IRC server temporarily unavailable\n"
                error_msg += "• Nickname already in use\n\n"
                error_msg += "Try:\n"
                error_msg += "• Different IRC network (OFTC or EFNet)\n"
                error_msg += "• Different nickname\n"
                error_msg += "• Check your internet connection"
                
                messagebox.showerror("Connection Error", error_msg)
                
        except Exception as e:
            print(f"DEBUG: Error checking connection status: {e}")
            self.chat_status_var.set("Connection failed")
            self.chat_status_label.configure(foreground="red")
            self.chat_connect_button.configure(text="Connect", state="normal")
    
    def disconnect_from_chat(self):
        """Disconnect from IRC"""
        try:
            if self.secure_chat:
                self.secure_chat.disconnect_from_irc()
            
            # Update UI
            self.chat_status_var.set("Disconnected")
            self.chat_status_label.configure(foreground="red")
            self.chat_connect_button.configure(text="Connect", state="normal")
            self.chat_send_button.configure(state="disabled")
            
            # Add system message to chat log
            self.add_chat_log_message("SYSTEM", "Disconnected from IRC")
            
        except Exception as e:
            messagebox.showerror("Disconnect Error", f"Failed to disconnect: {str(e)}")
    
    def add_chat_contact_dialog(self):
        """Show dialog to add a new chat contact"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Chat Contact")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Contact name
        ttk.Label(main_frame, text="Contact Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=name_var, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # IRC nickname
        ttk.Label(main_frame, text="IRC Nickname:").grid(row=1, column=0, sticky=tk.W, pady=5)
        irc_nick_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=irc_nick_var, width=30).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Method selection
        ttk.Label(main_frame, text="Key Method:").grid(row=2, column=0, sticky=tk.W, pady=5)
        method_var = tk.StringVar(value="fingerprint")
        method_frame = ttk.Frame(main_frame)
        method_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Radiobutton(method_frame, text="Use Fingerprint", variable=method_var, 
                       value="fingerprint").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(method_frame, text="Import Public Key", variable=method_var, 
                       value="public_key").grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        # Fingerprint entry
        ttk.Label(main_frame, text="PGP Fingerprint:").grid(row=3, column=0, sticky=tk.W, pady=5)
        fingerprint_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=fingerprint_var, width=30).grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Public key text area
        ttk.Label(main_frame, text="Public Key:").grid(row=4, column=0, sticky=(tk.W, tk.N), pady=5)
        key_frame = ttk.Frame(main_frame)
        key_frame.grid(row=4, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        key_frame.columnconfigure(0, weight=1)
        key_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        public_key_text = tk.Text(key_frame, height=8, width=50)
        public_key_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        key_scroll = ttk.Scrollbar(key_frame, orient="vertical", command=public_key_text.yview)
        key_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        public_key_text.configure(yscrollcommand=key_scroll.set)
        
        # Paste button
        ttk.Button(key_frame, text="Paste from Clipboard", 
                  command=lambda: self.paste_to_text_widget(public_key_text)).grid(row=1, column=0, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        def add_contact():
            try:
                name = name_var.get().strip()
                irc_nick = irc_nick_var.get().strip()
                
                if not name or not irc_nick:
                    messagebox.showerror("Error", "Please enter both name and IRC nickname")
                    return
                
                if method_var.get() == "fingerprint":
                    fingerprint = fingerprint_var.get().strip()
                    if not fingerprint:
                        messagebox.showerror("Error", "Please enter PGP fingerprint")
                        return
                    
                    # Add contact with fingerprint
                    if self.secure_chat:
                        contact = self.secure_chat.add_contact(name, irc_nick, pgp_fingerprint=fingerprint)
                        # Also add to unified contacts system
                        self.add_chat_contact_to_unified_system(name, irc_nick, pgp_fingerprint=fingerprint)
                    else:
                        # Store for later when chat is initialized
                        self.chat_contacts[irc_nick] = {
                            "name": name,
                            "fingerprint": fingerprint,
                            "public_key": None
                        }
                else:
                    public_key = public_key_text.get("1.0", tk.END).strip()
                    if not public_key:
                        messagebox.showerror("Error", "Please enter public key")
                        return
                    
                    # Add contact with public key
                    if self.secure_chat:
                        contact = self.secure_chat.add_contact(name, irc_nick, public_key=public_key)
                        # Also add to unified contacts system
                        self.add_chat_contact_to_unified_system(name, irc_nick, public_key=public_key)
                    else:
                        # Store for later when chat is initialized
                        self.chat_contacts[irc_nick] = {
                            "name": name,
                            "fingerprint": None,
                            "public_key": public_key
                        }
                
                # Update contacts list
                self.refresh_chat_contacts()
                # Also refresh the main contacts tab
                self.refresh_contacts_list()
                
                messagebox.showinfo("Success", f"Contact '{name}' added successfully")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add contact: {str(e)}")
        
        ttk.Button(button_frame, text="Add Contact", command=add_contact).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).grid(row=0, column=1, padx=5)
    
    def paste_to_text_widget(self, text_widget):
        """Paste clipboard content to text widget"""
        try:
            clipboard_content = self.root.clipboard_get()
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", clipboard_content)
        except tk.TclError:
            messagebox.showwarning("Warning", "Clipboard is empty")
    
    def refresh_chat_contacts(self):
        """Refresh the chat contacts list - ENHANCED VERSION"""
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
                        try:
                            # ENHANCED: Prioritize public key over fingerprint
                            public_key = contact_info.get('public_key')
                            if public_key:
                                print(f"DEBUG: Adding contact {contact_info['name']} with public key")
                                self.secure_chat.add_contact(contact_info['name'], irc_nick, public_key=public_key)
                            else:
                                print(f"DEBUG: Adding contact {contact_info['name']} with fingerprint")
                                self.secure_chat.add_contact(contact_info['name'], irc_nick, pgp_fingerprint=fingerprint)
                        except Exception as e:
                            print(f"WARNING: Failed to add contact {contact_info['name']} to secure chat: {e}")
            
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
    
    def start_chat_with_contact(self, event):
        """Start chat with selected contact"""
        selection = self.chat_contacts_listbox.curselection()
        if selection:
            contact_text = self.chat_contacts_listbox.get(selection[0])
            # Extract nickname from "Name (nickname)" format
            nickname = contact_text.split('(')[-1].rstrip(')')
            self.chat_target_var.set(nickname)
    
    def send_chat_message(self, event=None):
        """Send encrypted chat message"""
        try:
            if not self.secure_chat or not self.secure_chat.irc_client.connected:
                messagebox.showerror("Error", "Not connected to IRC")
                return
            
            target = self.chat_target_var.get().strip()
            message = self.chat_message_var.get().strip()
            
            if not target:
                messagebox.showerror("Error", "Please select a chat target")
                return
            
            if not message:
                return  # Don't send empty messages
            
            # Send secure message
            self.secure_chat.send_secure_message(target, message)
            
            # Add to chat log
            self.add_chat_log_message("You", f"→ {target}: {message}", encrypted=True)
            
            # Save to message history if enabled
            if self.chat_save_history_var.get():
                self.add_to_message_history(
                    msg_type="Chat Sent",
                    subject=f"Chat to {target}",
                    recipient=target,
                    date=time.strftime("%Y-%m-%d %H:%M:%S"),
                    full_content=message
                )
            
            # Clear message input
            self.chat_message_var.set("")
            
        except Exception as e:
            messagebox.showerror("Send Error", f"Failed to send message: {str(e)}")
    
    def on_chat_message_received(self, chat_message):
        """Handle received chat message"""
        try:
            # Add to chat log
            encryption_status = "🔒" if chat_message.encrypted else "📝"
            verification_status = "✓" if chat_message.verified else ""
            
            sender_display = f"{chat_message.sender} {encryption_status}{verification_status}"
            self.add_chat_log_message(sender_display, chat_message.content, 
                                    encrypted=chat_message.encrypted)
            
            # Save to message history if enabled
            if self.chat_save_history_var.get():
                self.add_to_message_history(
                    msg_type="Chat Received",
                    subject=f"Chat from {chat_message.sender}",
                    recipient=chat_message.sender,
                    date=time.strftime("%Y-%m-%d %H:%M:%S"),
                    full_content=chat_message.content
                )
            
        except Exception as e:
            self.add_chat_log_message("ERROR", f"Failed to process message: {str(e)}")
    
    def on_chat_error(self, error_message: str):
        """Handle chat errors - ENHANCED WITH PASSPHRASE PROMPTING"""
        print(f"DEBUG: Chat error: {error_message}")
        
        # Check if this is a passphrase-related error
        if "passphrase" in error_message.lower() or "private key" in error_message.lower():
            # This might be a decryption error that needs a passphrase
            # For now, we'll show the error but in the future we could prompt for passphrase
            self.add_chat_log_message("ERROR", error_message)
            
            # If we don't have a passphrase set, we could prompt for one
            if not hasattr(self.secure_chat, '_current_passphrase') or not self.secure_chat._current_passphrase:
                # Could add passphrase prompt here in the future
                self.add_chat_log_message("SYSTEM", "Tip: If you have a passphrase on your private key, you may need to enter it for decryption")
        else:
            # Regular error handling
            self.add_chat_log_message("ERROR", error_message)
    def add_chat_log_message(self, sender, message, encrypted=False):
        """Add message to chat log"""
        try:
            self.chat_log_text.configure(state=tk.NORMAL)
            
            # Add timestamp
            timestamp = time.strftime("%H:%M:%S")
            
            # Format message
            if sender == "SYSTEM":
                formatted_message = f"[{timestamp}] SYSTEM: {message}\n"
                self.chat_log_text.insert(tk.END, formatted_message)
            elif sender == "ERROR":
                formatted_message = f"[{timestamp}] ERROR: {message}\n"
                self.chat_log_text.insert(tk.END, formatted_message)
            else:
                encryption_indicator = " 🔒" if encrypted else ""
                formatted_message = f"[{timestamp}] {sender}{encryption_indicator}: {message}\n"
                self.chat_log_text.insert(tk.END, formatted_message)
            
            # Scroll to bottom
            self.chat_log_text.see(tk.END)
            self.chat_log_text.configure(state=tk.DISABLED)
            
        except Exception as e:
            print(f"Error adding chat log message: {e}")

    # Group Chat Methods
    def initialize_group_chat(self):
        """Initialize group chat system"""
        try:
            # Use absolute import instead of relative import
            import sys
            import os
            
            # Add the parent directory to sys.path if not already there
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            
            from chat.group_chat import GroupChatHandler
            
            if self.secure_chat:
                # Create group chat handler using the same PGP handler
                self.group_chat = GroupChatHandler(self.secure_chat.pgp_handler)
                
                # Copy IRC client from secure chat
                self.group_chat.irc_client = self.secure_chat.irc_client
                self.group_chat.connected = self.secure_chat.irc_client.connected if self.secure_chat.irc_client else False
                
                # Set up group chat callbacks
                self.group_chat.on_group_message_callback = self.on_group_message_received
                self.group_chat.on_group_join_callback = self.on_group_joined
                self.group_chat.on_group_leave_callback = self.on_group_left
                
                # Load existing groups
                groups_file = os.path.join(self.key_generator.gnupg_home, "groups.json")
                if os.path.exists(groups_file):
                    self.group_chat.load_groups_from_file(groups_file)
                
                # Refresh groups list
                self.refresh_groups_list()
                
                # Enable group chat controls
                self.group_send_button.config(state="normal" if self.group_chat.current_group else "disabled")
                
                return True
        except Exception as e:
            print(f"Warning: Could not initialize group chat: {e}")
            return False
    
    def create_group_dialog(self):
        """Show create group dialog"""
        if not self.group_chat:
            messagebox.showerror("Error", "Group chat not initialized. Please connect to IRC first.")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Group")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Group name
        ttk.Label(main_frame, text="Group Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(main_frame, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Description
        ttk.Label(main_frame, text="Description:").grid(row=1, column=0, sticky=tk.NW, pady=5)
        desc_text = tk.Text(main_frame, height=4, width=30)
        desc_text.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Privacy settings
        privacy_frame = ttk.LabelFrame(main_frame, text="Privacy Settings", padding="10")
        privacy_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        privacy_frame.columnconfigure(1, weight=1)
        
        is_private_var = tk.BooleanVar()
        ttk.Checkbutton(privacy_frame, text="Private Group", 
                       variable=is_private_var).grid(row=0, column=0, sticky=tk.W)
        
        ttk.Label(privacy_frame, text="Password (optional):").grid(row=1, column=0, sticky=tk.W, pady=5)
        password_var = tk.StringVar()
        password_entry = ttk.Entry(privacy_frame, textvariable=password_var, show="*", width=20)
        password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Max members
        ttk.Label(privacy_frame, text="Max Members:").grid(row=2, column=0, sticky=tk.W, pady=5)
        max_members_var = tk.StringVar(value="50")
        max_members_entry = ttk.Entry(privacy_frame, textvariable=max_members_var, width=10)
        max_members_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0))
        
        def create_group():
            name = name_var.get().strip()
            description = desc_text.get(1.0, tk.END).strip()
            is_private = is_private_var.get()
            password = password_var.get().strip() if is_private else None
            
            try:
                max_members = int(max_members_var.get())
                if max_members < 2 or max_members > 1000:
                    raise ValueError("Max members must be between 2 and 1000")
            except ValueError:
                messagebox.showerror("Error", "Invalid max members value")
                return
            
            if not name:
                messagebox.showerror("Error", "Please enter a group name")
                return
            
            # Create the group
            success, message = self.group_chat.create_group(name, description, is_private, password, max_members)
            if success:
                messagebox.showinfo("Success", f"Group '{name}' created successfully!")
                dialog.destroy()
                self.refresh_groups_list()
                self.save_groups_data()
            else:
                messagebox.showerror("Error", f"Failed to create group: {message}")
        
        ttk.Button(button_frame, text="Create Group", command=create_group).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT)
        
        # Focus on name entry
        name_entry.focus()
    
    def join_group_dialog(self):
        """Show join group dialog"""
        if not self.group_chat:
            messagebox.showerror("Error", "Group chat not initialized. Please connect to IRC first.")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Join Group")
        dialog.geometry("350x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Group name
        ttk.Label(main_frame, text="Group Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(main_frame, textvariable=name_var, width=25)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Password
        ttk.Label(main_frame, text="Password (if required):").grid(row=1, column=0, sticky=tk.W, pady=5)
        password_var = tk.StringVar()
        password_entry = ttk.Entry(main_frame, textvariable=password_var, show="*", width=25)
        password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(20, 0))
        
        def join_group():
            name = name_var.get().strip()
            password = password_var.get().strip()
            
            if not name:
                messagebox.showerror("Error", "Please enter a group name")
                return
            
            # Join the group
            success, message = self.group_chat.join_group(name, password if password else None)
            if success:
                messagebox.showinfo("Success", f"Joined group '{name}' successfully!")
                dialog.destroy()
                self.refresh_groups_list()
                self.switch_to_group_by_name(name)
                self.save_groups_data()
            else:
                messagebox.showerror("Error", f"Failed to join group: {message}")
        
        ttk.Button(button_frame, text="Join Group", command=join_group).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT)
        
        # Focus on name entry
        name_entry.focus()
    
    def leave_current_group(self):
        """Leave the current group"""
        if not self.group_chat or not self.group_chat.current_group:
            messagebox.showwarning("Warning", "No group selected")
            return
        
        group_name = self.group_chat.current_group
        
        # Confirm leaving
        result = messagebox.askyesno("Confirm Leave", f"Are you sure you want to leave group '{group_name}'?")
        if not result:
            return
        
        # Leave the group
        success, message = self.group_chat.leave_group(group_name)
        if success:
            messagebox.showinfo("Success", f"Left group '{group_name}' successfully!")
            self.refresh_groups_list()
            self.update_group_display()
            self.save_groups_data()
        else:
            messagebox.showerror("Error", f"Failed to leave group: {message}")
    
    def switch_to_group(self, event):
        """Switch to selected group"""
        selection = self.groups_listbox.curselection()
        if selection:
            group_name = self.groups_listbox.get(selection[0])
            self.switch_to_group_by_name(group_name)
    
    def switch_to_group_by_name(self, group_name):
        """Switch to a specific group"""
        if not self.group_chat:
            return
        
        self.group_chat.current_group = group_name
        self.update_group_display()
        self.load_group_message_history(group_name)
        
        # Enable/disable send button
        self.group_send_button.config(state="normal")
        self.group_message_entry.config(state="normal")
    
    def update_group_display(self):
        """Update group display information"""
        if not self.group_chat or not self.group_chat.current_group:
            self.current_group_var.set("None")
            self.group_member_count_var.set("0 members")
            self.group_creator_var.set("")
            self.group_chat_title_var.set("Select a group to start chatting")
            self.group_send_button.config(state="disabled")
            self.group_message_entry.config(state="disabled")
            return
        
        group_name = self.group_chat.current_group
        group_info = self.group_chat.get_group_info(group_name)
        
        if group_info:
            self.current_group_var.set(group_name)
            member_count = len(group_info['members'])
            self.group_member_count_var.set(f"{member_count} members")
            
            # Handle creator display for external vs internal groups
            creator = group_info.get('creator', '')
            is_external = group_info.get('is_external', False)
            
            if is_external:
                if creator:
                    self.group_creator_var.set(f"External IRC channel (Creator: {creator})")
                else:
                    self.group_creator_var.set("External IRC channel (Creator unknown)")
            else:
                if creator:
                    self.group_creator_var.set(f"Created by: {creator}")
                else:
                    self.group_creator_var.set("Creator: Unknown")
                    
            self.group_chat_title_var.set(f"Group: {group_name}")
        else:
            self.current_group_var.set(group_name)
            self.group_member_count_var.set("Unknown members")
            self.group_creator_var.set("")
            self.group_chat_title_var.set(f"Group: {group_name}")
    
    def refresh_groups_list(self):
        """Refresh the groups list"""
        self.groups_listbox.delete(0, tk.END)
        
        if self.group_chat:
            groups = self.group_chat.list_groups()
            for group_name in groups:
                self.groups_listbox.insert(tk.END, group_name)
    
    def send_group_message(self, event=None):
        """Send a message to the current group"""
        if not self.group_chat or not self.group_chat.current_group:
            messagebox.showwarning("Warning", "No group selected")
            return
        
        message = self.group_message_var.get().strip()
        if not message:
            return  # Don't send empty messages
        
        group_name = self.group_chat.current_group
        
        # Send the message
        success, result_message = self.group_chat.send_group_message(group_name, message)
        if success:
            # Add to group chat log
            self.add_group_chat_log_message("You", f"→ {group_name}: {message}")
            
            # Save to message history if enabled
            if self.chat_save_history_var.get():
                self.add_to_message_history(
                    msg_type="Group Chat Sent",
                    subject=f"Group: {group_name}",
                    recipient=group_name,
                    date=time.strftime("%Y-%m-%d %H:%M:%S"),
                    full_content=message
                )
            
            # Clear message input
            self.group_message_var.set("")
        else:
            messagebox.showerror("Error", f"Failed to send message: {result_message}")
    
    def on_group_message_received(self, group_message):
        """Handle received group message"""
        try:
            # Add to group chat log
            encryption_status = "🔒" if group_message.encrypted else "📝"
            verification_status = "✓" if group_message.verified else ""
            
            sender_display = f"{group_message.sender} {encryption_status}{verification_status}"
            self.add_group_chat_log_message(sender_display, group_message.content)
            
            # Save to message history if enabled
            if self.chat_save_history_var.get():
                self.add_to_message_history(
                    msg_type="Group Chat Received",
                    subject=f"Group: {group_message.group_name}",
                    recipient=group_message.sender,
                    date=time.strftime("%Y-%m-%d %H:%M:%S"),
                    full_content=group_message.content
                )
            
        except Exception as e:
            self.add_group_chat_log_message("ERROR", f"Failed to process group message: {str(e)}")
    
    def add_group_chat_log_message(self, sender, message):
        """Add message to group chat log"""
        try:
            self.group_chat_log_text.configure(state=tk.NORMAL)
            
            # Add timestamp
            timestamp = time.strftime("%H:%M:%S")
            
            # Format message
            if sender == "SYSTEM":
                formatted_message = f"[{timestamp}] SYSTEM: {message}\n"
                self.group_chat_log_text.insert(tk.END, formatted_message)
            elif sender == "ERROR":
                formatted_message = f"[{timestamp}] ERROR: {message}\n"
                self.group_chat_log_text.insert(tk.END, formatted_message)
            else:
                formatted_message = f"[{timestamp}] {sender}: {message}\n"
                self.group_chat_log_text.insert(tk.END, formatted_message)
            
            # Scroll to bottom
            self.group_chat_log_text.see(tk.END)
            self.group_chat_log_text.configure(state=tk.DISABLED)
            
        except Exception as e:
            print(f"Error adding group chat message: {e}")
    
    def load_group_message_history(self, group_name):
        """Load message history for a group"""
        if not self.group_chat:
            return
        
        # Clear current log
        self.group_chat_log_text.configure(state=tk.NORMAL)
        self.group_chat_log_text.delete(1.0, tk.END)
        
        # Load history
        messages = self.group_chat.get_group_message_history(group_name)
        for message in messages[-50:]:  # Show last 50 messages
            encryption_status = "🔒" if message.encrypted else "📝"
            verification_status = "✓" if message.verified else ""
            
            sender_display = f"{message.sender} {encryption_status}{verification_status}"
            timestamp = time.strftime("%H:%M:%S", time.localtime(message.timestamp))
            formatted_message = f"[{timestamp}] {sender_display}: {message.content}\n"
            
            self.group_chat_log_text.insert(tk.END, formatted_message)
        
        self.group_chat_log_text.configure(state=tk.DISABLED)
        self.group_chat_log_text.see(tk.END)
    
    def on_group_joined(self, group_name, user):
        """Handle user joining group"""
        self.add_group_chat_log_message("SYSTEM", f"{user} joined the group")
        self.update_group_display()
    
    def on_group_left(self, group_name, user):
        """Handle user leaving group"""
        self.add_group_chat_log_message("SYSTEM", f"{user} left the group")
        self.update_group_display()
    
    def show_group_context_menu(self, event):
        """Show context menu for group - ENHANCED WITH CREATOR INFO"""
        selection = self.groups_listbox.curselection()
        if not selection:
            return
        
        group_name = self.groups_listbox.get(selection[0])
        
        # Create context menu
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Switch to Group", command=lambda: self.switch_to_group_by_name(group_name))
        context_menu.add_command(label="Group Info", command=lambda: self.show_group_info_dialog(group_name))
        context_menu.add_command(label="Manage Members", command=lambda: self.manage_group_members_dialog(group_name))
        context_menu.add_separator()
        context_menu.add_command(label="Leave Group", command=lambda: self.leave_group_by_name(group_name))
        context_menu.add_command(label="Delete Group", command=lambda: self.delete_group_by_name(group_name))
        
        # Show menu
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def show_group_info_dialog(self, group_name):
        """Show detailed group information dialog - NEW METHOD"""
        if not self.group_chat:
            messagebox.showerror("Error", "Group chat not initialized")
            return
        
        group_info = self.group_chat.get_group_info(group_name)
        if not group_info:
            messagebox.showerror("Error", "Group information not found")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Group Info: {group_name}")
        dialog.geometry("450x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Group details
        info_frame = ttk.LabelFrame(main_frame, text="Group Details", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Group name
        ttk.Label(info_frame, text="Name:", font=('TkDefaultFont', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=group_info.get('name', 'Unknown')).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Creator (highlighted as per user preference)
        ttk.Label(info_frame, text="Creator:", font=('TkDefaultFont', 9, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=2)
        creator_label = ttk.Label(info_frame, text=group_info.get('creator', 'Unknown'), 
                                 font=('TkDefaultFont', 9, 'bold'), foreground='blue')
        creator_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Created date
        created_at = group_info.get('created_at', 0)
        created_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(created_at)) if created_at else "Unknown"
        ttk.Label(info_frame, text="Created:", font=('TkDefaultFont', 9, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=created_date).grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Privacy
        is_private = group_info.get('is_private', False)
        privacy_text = "Private" if is_private else "Public"
        ttk.Label(info_frame, text="Privacy:", font=('TkDefaultFont', 9, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=privacy_text).grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Member count
        members = group_info.get('members', [])
        max_members = group_info.get('max_members', 50)
        member_text = f"{len(members)}/{max_members}"
        ttk.Label(info_frame, text="Members:", font=('TkDefaultFont', 9, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=member_text).grid(row=4, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Description
        if group_info.get('description'):
            desc_frame = ttk.LabelFrame(main_frame, text="Description", padding="10")
            desc_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            desc_text = tk.Text(desc_frame, height=4, wrap=tk.WORD, state=tk.DISABLED)
            desc_text.pack(fill=tk.BOTH, expand=True)
            desc_text.config(state=tk.NORMAL)
            desc_text.insert(1.0, group_info.get('description', ''))
            desc_text.config(state=tk.DISABLED)
        
        # Members list
        members_frame = ttk.LabelFrame(main_frame, text="Members", padding="10")
        members_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create listbox with scrollbar
        listbox_frame = ttk.Frame(members_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        members_listbox = tk.Listbox(listbox_frame, height=6)
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=members_listbox.yview)
        members_listbox.configure(yscrollcommand=scrollbar.set)
        
        members_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate members list with role indicators
        admins = group_info.get('admins', [])
        creator = group_info.get('creator', '')
        
        for member in sorted(members):
            if member == creator:
                display_text = f"{member} (Creator)"
            elif member in admins:
                display_text = f"{member} (Admin)"
            else:
                display_text = member
            members_listbox.insert(tk.END, display_text)
        
        # Close button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(10, 0))
        
        ttk.Button(button_frame, text="Close", command=dialog.destroy).pack()
        
        # Configure grid weights for info frame
        info_frame.columnconfigure(1, weight=1)
    
    def leave_group_by_name(self, group_name):
        """Leave a specific group"""
        result = messagebox.askyesno("Confirm Leave", f"Are you sure you want to leave group '{group_name}'?")
        if not result:
            return
        
        success, message = self.group_chat.leave_group(group_name)
        if success:
            messagebox.showinfo("Success", f"Left group '{group_name}' successfully!")
            self.refresh_groups_list()
            if self.group_chat.current_group == group_name:
                self.group_chat.current_group = None
                self.update_group_display()
            self.save_groups_data()
        else:
            messagebox.showerror("Error", f"Failed to leave group: {message}")
    
    def delete_group_by_name(self, group_name):
        """Delete a specific group"""
        if not self.group_chat:
            messagebox.showerror("Error", "Group chat not initialized")
            return
        
        # Get group info to check permissions
        group_info = self.group_chat.get_group_info(group_name)
        if not group_info:
            messagebox.showerror("Error", "Group information not found")
            return
        
        current_user = self.group_chat.irc_client.nickname if self.group_chat.irc_client else "unknown"
        
        # Check if user has permission to delete
        if current_user != group_info.get('creator') and current_user not in group_info.get('admins', []):
            messagebox.showerror("Permission Denied", 
                               "Only the group creator or admins can delete this group.")
            return
        
        # Confirmation dialog
        result = messagebox.askyesno(
            "Delete Group", 
            f"Are you sure you want to permanently delete group '{group_name}'?\n\n"
            "This action cannot be undone and will:\n"
            "• Remove the group for all members\n"
            "• Delete all group message history\n"
            "• Leave the IRC channel\n\n"
            "All members will be notified of the deletion."
        )
        
        if result:
            success, message = self.group_chat.delete_group(group_name)
            if success:
                messagebox.showinfo("Success", f"Group '{group_name}' deleted successfully!")
                self.refresh_groups_list()
                self.update_group_display()
                self.save_groups_data()
            else:
                messagebox.showerror("Error", f"Failed to delete group: {message}")
    
    def manage_group_members_dialog(self, group_name=None):
        """Show group members management dialog"""
        if not self.group_chat:
            messagebox.showerror("Error", "Group chat not initialized")
            return
        
        if not group_name:
            group_name = self.group_chat.current_group
        
        if not group_name:
            messagebox.showwarning("Warning", "No group selected")
            return
        
        group_info = self.group_chat.get_group_info(group_name)
        if not group_info:
            messagebox.showerror("Error", "Group information not found")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Manage Members - {group_name}")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Group info
        info_frame = ttk.LabelFrame(main_frame, text="Group Information", padding="10")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        
        ttk.Label(info_frame, text="Name:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(info_frame, text=group_info['name'], font=('Arial', 9, 'bold')).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(info_frame, text="Description:").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(info_frame, text=group_info.get('description', 'No description')).grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(info_frame, text="Creator:").grid(row=2, column=0, sticky=tk.W)
        ttk.Label(info_frame, text=group_info.get('creator', 'Unknown')).grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        # Members list
        members_frame = ttk.LabelFrame(main_frame, text="Members", padding="10")
        members_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        members_frame.columnconfigure(0, weight=1)
        members_frame.rowconfigure(0, weight=1)
        
        # Members treeview
        columns = ("Nickname", "Role")
        members_tree = ttk.Treeview(members_frame, columns=columns, show="headings", height=10)
        members_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure columns
        members_tree.heading("Nickname", text="Nickname")
        members_tree.heading("Role", text="Role")
        members_tree.column("Nickname", width=200)
        members_tree.column("Role", width=100)
        
        # Scrollbar
        members_scroll = ttk.Scrollbar(members_frame, orient="vertical", command=members_tree.yview)
        members_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        members_tree.configure(yscrollcommand=members_scroll.set)
        
        # Populate members
        for member in group_info['members']:
            role = "Admin" if member in group_info['admins'] else "Member"
            if member == group_info['creator']:
                role = "Creator"
            members_tree.insert('', 'end', values=(member, role))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=(10, 0))
        
        ttk.Button(button_frame, text="Close", command=dialog.destroy).pack(side=tk.RIGHT)
    
    def export_key_as_contact_card(self):
        """Export selected key as encrypted contact card"""
        selection = self.key_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a key to export as contact card")
            return
        
        item = selection[0]
        values = self.key_tree.item(item, 'values')
        
        if len(values) < 4:
            messagebox.showerror("Error", "Invalid key selection")
            return
        
        key_type = values[0]
        key_name = values[1]
        key_id = values[3]
        
        # Only allow public keys or private keys to be exported as contact cards
        if key_type not in ['Public', 'Private']:
            messagebox.showwarning("Warning", "Only public keys and private keys can be exported as contact cards")
            return
        
        try:
            # Get key details - check both public and private keys
            all_keys = []
            
            # Add public keys
            public_keys = self.key_generator.list_keys(secret=False)
            all_keys.extend(public_keys)
            
            # Add private keys if we're looking for a private key
            if key_type == 'Private':
                private_keys = self.key_generator.list_keys(secret=True)
                all_keys.extend(private_keys)
            
            selected_key = None
            
            for key in all_keys:
                # Match by last 8 characters of key ID (as displayed in tree)
                if key['keyid'][-8:] == key_id or key['keyid'] == key_id or key['fingerprint'].endswith(key_id):
                    selected_key = key
                    break
            
            if not selected_key:
                messagebox.showerror("Error", "Could not find key details")
                return
            
            # Export the public key
            export_result = self.key_generator.export_public_key(selected_key['fingerprint'])
            if not export_result.get('success'):
                messagebox.showerror("Error", f"Could not export public key: {export_result.get('error', 'Unknown error')}")
                return
            
            public_key_data = export_result.get('public_key', '')
            if not public_key_data:
                messagebox.showerror("Error", "No public key data found")
                return
            
            # Create contact info structure
            contact_info = {
                'name': key_name if key_name != 'Imported Key' else f"Key_{key_id[-8:]}",
                'irc_nickname': '',
                'fingerprint': selected_key['fingerprint']
            }
            
            # Show export dialog
            self.show_export_key_contact_card_dialog(contact_info, public_key_data)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to prepare key export: {str(e)}")
    
    def show_export_key_contact_card_dialog(self, contact_info, public_key_data):
        """Show dialog for exporting key as contact card"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Export Key as Contact Card")
        dialog.geometry("500x450")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="Export Key as Contact Card", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 15))
        
        # Key info frame
        info_frame = ttk.LabelFrame(main_frame, text="Key Information", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(info_frame, text=f"Key Name: {contact_info['name']}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Key Fingerprint: {contact_info['fingerprint'][-16:]}").pack(anchor=tk.W)
        
        # Contact details frame
        details_frame = ttk.LabelFrame(main_frame, text="Contact Details", padding="10")
        details_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Name field
        ttk.Label(details_frame, text="Contact Name:").pack(anchor=tk.W)
        name_var = tk.StringVar(value=contact_info['name'])
        name_entry = ttk.Entry(details_frame, textvariable=name_var, width=40)
        name_entry.pack(fill=tk.X, pady=(0, 10))
        
        # IRC nickname field
        ttk.Label(details_frame, text="IRC Nickname (optional):").pack(anchor=tk.W)
        irc_var = tk.StringVar(value=contact_info.get('irc_nickname', ''))
        irc_entry = ttk.Entry(details_frame, textvariable=irc_var, width=40)
        irc_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Notes field
        ttk.Label(details_frame, text="Notes (optional):").pack(anchor=tk.W)
        notes_text = tk.Text(details_frame, height=3, width=40)
        notes_text.pack(fill=tk.X, pady=(0, 10))
        
        # Password frame
        password_frame = ttk.LabelFrame(main_frame, text="Encryption Options", padding="10")
        password_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Checkbox for password protection
        use_password_var = tk.BooleanVar(value=True)
        password_checkbox = ttk.Checkbutton(
            password_frame, 
            text="Encrypt contact card with password (recommended)", 
            variable=use_password_var,
            command=lambda: toggle_password_fields()
        )
        password_checkbox.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(password_frame, text="Password to encrypt contact card:").pack(anchor=tk.W)
        password_var = tk.StringVar()
        password_entry = ttk.Entry(password_frame, textvariable=password_var, show="*", width=40)
        password_entry.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(password_frame, text="Confirm password:").pack(anchor=tk.W)
        confirm_var = tk.StringVar()
        confirm_entry = ttk.Entry(password_frame, textvariable=confirm_var, show="*", width=40)
        confirm_entry.pack(fill=tk.X)
        
        def toggle_password_fields():
            """Enable/disable password fields based on checkbox"""
            if use_password_var.get():
                password_entry.config(state='normal')
                confirm_entry.config(state='normal')
            else:
                password_entry.config(state='disabled')
                confirm_entry.config(state='disabled')
                password_var.set('')
                confirm_var.set('')
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(15, 0))
        
        def export_card():
            name = name_var.get().strip()
            password = password_var.get() if use_password_var.get() else None
            confirm = confirm_var.get() if use_password_var.get() else None
            
            if not name:
                messagebox.showerror("Error", "Please enter a contact name")
                return
            
            # Validate password only if encryption is enabled
            if use_password_var.get():
                if not password:
                    messagebox.showerror("Error", "Please enter a password")
                    return
                
                if password != confirm:
                    messagebox.showerror("Error", "Passwords do not match")
                    return
                
                if len(password) < 6:
                    messagebox.showerror("Error", "Password must be at least 6 characters")
                    return
            
            try:
                from tkinter import filedialog
                from security.contact_card import ContactCardManager, ContactCard
                
                # Create contact card
                card_manager = ContactCardManager()
                contact_card = ContactCard(
                    name=name,
                    irc_nickname=irc_var.get().strip(),
                    public_key=public_key_data,
                    notes=notes_text.get("1.0", tk.END).strip()
                )
                
                # Choose save location
                file_path = filedialog.asksaveasfilename(
                    title="Save Contact Card",
                    defaultextension=".pgpcard",
                    filetypes=[
                        ("PGP Contact Cards", "*.pgpcard"),
                        ("All files", "*.*")
                    ],
                    initialfile=f"{name.replace(' ', '_')}_contact_card.pgpcard"
                )
                
                if file_path:
                    # Export contact card
                    card_manager.export_contact_card(contact_card, file_path, password)
                    
                    dialog.destroy()
                    encryption_status = "encrypted" if password else "unencrypted"
                    messagebox.showinfo("Success", 
                                      f"Contact card exported successfully!\n\n"
                                      f"File: {file_path}\n"
                                      f"Type: {encryption_status.title()} contact card\n\n"
                                      f"Share this {encryption_status} file with others to exchange your contact information.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export contact card: {str(e)}")
        
        ttk.Button(button_frame, text="Export", command=export_card).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT)
    
    def save_groups_data(self):
        """Save groups data to file"""
        if self.group_chat:
            try:
                groups_file = os.path.join(self.key_generator.gnupg_home, "groups.json")
                self.group_chat.save_groups_to_file(groups_file)
            except Exception as e:
                print(f"Warning: Failed to save groups data: {e}")
    
    def add_chat_contact_to_unified_system(self, name, irc_nickname, public_key=None, pgp_fingerprint=None):
        """Add a chat contact to the unified contacts system"""
        try:
            # Import the public key if provided
            if public_key:
                import_result = self.key_generator.import_key(public_key)
                if import_result.get('success'):
                    fingerprint = import_result.get('fingerprint')
                else:
                    print(f"Warning: Failed to import public key for chat contact {name}")
                    return
            elif pgp_fingerprint:
                fingerprint = pgp_fingerprint
            else:
                print(f"Warning: No public key or fingerprint provided for chat contact {name}")
                return
            
            # Add to unified contacts
            contacts = self.load_contacts()
            contacts[fingerprint] = {
                'name': name,
                'irc_nickname': irc_nickname,
                'email': '',  # Not provided in chat contact
                'notes': 'Added from chat tab',
                'date_added': time.strftime("%Y-%m-%d %H:%M:%S"),
                'added_from_chat': True
            }
            
            # Store public key if available
            if public_key:
                contacts[fingerprint]['public_key'] = public_key
            else:
                # Try to export public key from keyring
                try:
                    export_result = self.key_generator.export_public_key(fingerprint)
                    if export_result.get('success'):
                        contacts[fingerprint]['public_key'] = export_result.get('public_key')
                except Exception as e:
                    print(f"Warning: Could not export public key for contact: {e}")
            
            # Save contacts using encrypted storage
            if hasattr(self.key_generator, 'data_manager') and self.key_generator.data_manager:
                self.key_generator.data_manager.save_data("contacts.json", contacts)
            else:
                # Fallback to unencrypted storage if data manager not available
                import json
                contacts_file = os.path.join(self.key_generator.gnupg_home, "contacts.json")
                with open(contacts_file, 'w') as f:
                    json.dump(contacts, f, indent=2)
                    
        except Exception as e:
            print(f"Warning: Failed to add chat contact to unified system: {e}")
    
    def refresh_chat_profiles(self):
        """Refresh the chat profiles dropdown with available key pairs - ENCRYPTION FIX"""
        try:
            print("DEBUG: Starting refresh_chat_profiles...")
            
            # CRITICAL FIX: Ensure encryption is initialized before accessing keys
            if not hasattr(self.key_generator, 'pgp_handler') or not self.key_generator.pgp_handler:
                print("DEBUG: No PGP handler found")
                return
                
            # Check if data manager has encryption initialized
            if hasattr(self.key_generator.pgp_handler, 'handler') and hasattr(self.key_generator.pgp_handler.handler, 'data_manager'):
                data_manager = self.key_generator.pgp_handler.handler.data_manager
                if not data_manager.encryption:
                    print("DEBUG: Data manager encryption not initialized - keys are encrypted but can't be accessed")
                    # Try to initialize encryption if we can
                    # Note: In a real scenario, we'd need the master password here
                    # For now, we'll show a helpful message
                    self.chat_profiles = []
                    self.chat_profile_combo['values'] = []
                    print("DEBUG: Cannot access encrypted keys without master password")
                    return
                else:
                    print("DEBUG: Data manager encryption is initialized")
            
            # Get private keys (key pairs that can be used for chat)
            try:
                private_keys = self.key_generator.list_keys(secret=True)
                print(f"DEBUG: Found {len(private_keys)} private keys")
            except Exception as e:
                print(f"DEBUG: Error listing private keys: {e}")
                private_keys = []
            
            # Also try to get from PGP handler directly
            if not private_keys:
                try:
                    if hasattr(self.key_generator, 'pgp_handler'):
                        pgp_result = self.key_generator.pgp_handler.list_keys(secret=True)
                        if pgp_result and pgp_result.get('success'):
                            private_keys = pgp_result.get('keys', [])
                            print(f"DEBUG: Found {len(private_keys)} private keys from PGP handler")
                        else:
                            print(f"DEBUG: PGP handler returned: {pgp_result}")
                except Exception as e:
                    print(f"DEBUG: Error getting keys from PGP handler: {e}")
            
            profiles = []
            for key in private_keys:
                try:
                    # Extract name from user ID with better parsing
                    uids = key.get('uids', [])
                    if not uids:
                        uids = key.get('user_ids', [])
                    
                    if uids:
                        user_id = uids[0] if isinstance(uids, list) else str(uids)
                    else:
                        user_id = 'Unknown User'
                    
                    # Parse name from user ID (handle "Name <email>" format)
                    if '<' in user_id and '>' in user_id:
                        name = user_id.split('<')[0].strip()
                        if not name:
                            # If name part is empty, use email part
                            email_part = user_id.split('<')[1].split('>')[0]
                            name = email_part.split('@')[0] if '@' in email_part else email_part
                    else:
                        name = user_id.strip()
                    
                    # Get fingerprint
                    fingerprint = key.get('fingerprint', '')
                    if not fingerprint:
                        fingerprint = key.get('key_id', '')
                    
                    if not fingerprint:
                        print(f"DEBUG: Skipping key with no fingerprint: {key}")
                        continue
                    
                    # CRITICAL FIX: Create profile entry with correct key ID extraction
                    # The key ID should be the last 8 characters of the fingerprint
                    # But we need to handle fingerprints with spaces properly
                    fingerprint_clean = fingerprint.replace(' ', '')  # Remove spaces
                    if len(fingerprint_clean) >= 8:
                        # Get last 8 characters for short key ID
                        short_key_id = fingerprint_clean[-8:].upper()
                        # Format with space for readability: "57AE 941F"
                        formatted_key_id = f"{short_key_id[:4]} {short_key_id[4:]}"
                    else:
                        # Fallback for short fingerprints
                        formatted_key_id = fingerprint_clean.upper()
                    
                    profile_display = f"{name} ({formatted_key_id})"
                    
                    profiles.append({
                        'display': profile_display,
                        'name': name,
                        'fingerprint': fingerprint,
                        'key_info': key
                    })
                    
                    print(f"DEBUG: Added profile: {profile_display}")
                    
                except Exception as e:
                    print(f"DEBUG: Error processing key {key}: {e}")
                    continue
            
            # Update combo box
            profile_displays = [p['display'] for p in profiles]
            self.chat_profile_combo['values'] = profile_displays
            
            # Store profile data for lookup
            self.chat_profiles = profiles
            
            print(f"DEBUG: Set {len(profile_displays)} profiles in dropdown: {profile_displays}")
            
            # Auto-select first profile if none selected and profiles exist
            if profiles and not self.chat_profile_var.get():
                self.chat_profile_combo.current(0)
                self.on_chat_profile_changed()
                print(f"DEBUG: Auto-selected first profile: {profiles[0]['display']}")
            elif not profiles:
                print("DEBUG: No profiles found - dropdown will be empty")
                print("DEBUG: This could be because:")
                print("DEBUG: 1. No key pairs have been generated")
                print("DEBUG: 2. Keys are encrypted and encryption is not initialized")
                print("DEBUG: 3. Keys are stored in a different location")
                # Clear any existing selection
                self.chat_profile_var.set("")
            
            print(f"DEBUG: Completed refresh_chat_profiles with {len(profiles)} profiles")
                
        except Exception as e:
            print(f"ERROR: Failed to refresh chat profiles: {e}")
            import traceback
            traceback.print_exc()
    
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
                
                # CRITICAL FIX: Set the full fingerprint for decryption in secure chat
                if hasattr(self, 'secure_chat') and self.secure_chat:
                    self.secure_chat._current_profile_fingerprint = selected_profile['fingerprint']
                    print(f"DEBUG: Set profile fingerprint for decryption: {selected_profile['fingerprint']}")
                
                print(f"DEBUG: Selected profile {selected_profile['name']}, IRC nick: {irc_nick}")
                
        except Exception as e:
            print(f"Warning: Failed to handle profile change: {e}")
    
    def get_current_chat_identity(self):
        """Get current chat identity (profile + IRC nickname)"""
        if hasattr(self, 'selected_chat_profile') and self.selected_chat_profile:
            return {
                'profile': self.selected_chat_profile,
                'irc_nickname': self.chat_irc_nickname_var.get(),
                'fingerprint': self.selected_chat_profile['fingerprint']
            }
        return None

    def on_irc_nickname_changed(self, *args):
        """Handle IRC nickname field changes"""
        # This is called when the user types in the nickname field
        # We don't apply the change immediately to avoid spamming the IRC server
        # The user needs to click Apply or press Enter
        pass
    
    def apply_nickname_change(self):
        """Apply the nickname change to the IRC connection"""
        try:
            new_nickname = self.chat_irc_nickname_var.get().strip()
            
            if not new_nickname:
                messagebox.showerror("Error", "Nickname cannot be empty")
                return
            
            # Validate nickname (IRC-friendly characters only)
            if not all(c.isalnum() or c in '_-[]{}\\`|' for c in new_nickname):
                messagebox.showerror("Error", "Nickname contains invalid characters. Use only letters, numbers, and _-[]{}\\`|")
                return
            
            if len(new_nickname) > 30:
                messagebox.showerror("Error", "Nickname too long (max 30 characters)")
                return
            
            # Apply nickname change if connected
            if self.secure_chat and self.secure_chat.irc_client and self.secure_chat.irc_client.connected:
                try:
                    old_nickname = self.secure_chat.irc_client.nickname
                    self.secure_chat.irc_client.change_nickname(new_nickname)
                    
                    # Update UI to reflect the change
                    self.add_chat_log_message("SYSTEM", f"Nickname changed from {old_nickname} to {new_nickname}")
                    
                    # Update status display
                    network = self.chat_network_var.get()
                    self.chat_status_var.set(f"Connected to {network} as {new_nickname}")
                    
                    print(f"DEBUG: Successfully changed nickname from {old_nickname} to {new_nickname}")
                    
                except Exception as e:
                    print(f"DEBUG: Failed to change nickname: {e}")
                    messagebox.showerror("Error", f"Failed to change nickname: {str(e)}")
            else:
                print("DEBUG: Not connected to IRC, nickname will be used on next connection")
                messagebox.showinfo("Info", "Not connected to IRC. Nickname will be used when you connect.")
                
        except Exception as e:
            print(f"DEBUG: Error in apply_nickname_change: {e}")
            messagebox.showerror("Error", f"Failed to apply nickname change: {str(e)}")

def main():
    """Main entry point"""
    app = PGPToolMainWindow()
    app.run()


if __name__ == "__main__":
    main()
