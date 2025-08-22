"""
Dialog Boxes Module
Contains all dialog boxes for key management, entropy collection, and other operations
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto.key_generator import SecureKeyGenerator
from crypto.entropy import EntropyCollector, MouseEntropyWidget, KeyboardEntropyWidget

class KeyGenerationDialog:
    """Dialog for generating new PGP key pairs with entropy collection"""
    
    def __init__(self, parent, key_generator: SecureKeyGenerator):
        """
        Initialize key generation dialog
        
        Args:
            parent: Parent window
            key_generator: SecureKeyGenerator instance
        """
        self.parent = parent
        self.key_generator = key_generator
        self.entropy_collector = None
        self.mouse_widget = None
        self.keyboard_widget = None
        self.generation_thread = None
        self.result = None
        
        self.create_dialog()
    
    def create_dialog(self):
        """Create the key generation dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Generate New PGP Key Pair")
        self.dialog.geometry("600x750")  # Increased height for buttons
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.center_dialog()
        
        # Create main container
        main_container = ttk.Frame(self.dialog)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for steps
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create tabs
        self.create_info_tab()
        self.create_entropy_tab()
        self.create_generation_tab()
        
        # Initially disable other tabs
        self.notebook.tab(1, state="disabled")
        self.notebook.tab(2, state="disabled")
        
        # Add a separator line above buttons
        separator = ttk.Separator(main_container, orient='horizontal')
        separator.pack(fill=tk.X, pady=(5, 10))
        
        # Button frame with more height
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Navigation buttons with better styling - using tkinter buttons for better control
        self.prev_button = tk.Button(
            button_frame, 
            text="◀ Previous", 
            command=self.prev_step,
            width=12,
            height=2,  # Make buttons taller
            font=('Arial', 10),
            relief='raised',
            borderwidth=1,
            bg='#f8f9fa',
            fg='#495057',
            activebackground='#e9ecef'
        )
        self.prev_button.pack(side=tk.LEFT, padx=5)
        
        # Center spacer
        spacer = ttk.Frame(button_frame)
        spacer.pack(side=tk.LEFT, expand=True)
        
        self.cancel_button = tk.Button(
            button_frame, 
            text="Cancel", 
            command=self.cancel,
            width=10,
            height=2,  # Make buttons taller
            font=('Arial', 10),
            relief='raised',
            borderwidth=1,
            bg='#f8f9fa',
            fg='#495057',
            activebackground='#e9ecef'
        )
        self.cancel_button.pack(side=tk.RIGHT, padx=5)
        
        self.next_button = tk.Button(
            button_frame, 
            text="Next ▶", 
            command=self.next_step,
            width=12,
            height=2,  # Make buttons taller
            font=('Arial', 10, 'bold'),
            relief='raised',
            borderwidth=1,
            bg='#007bff',  # Blue background for primary action
            fg='white',
            activebackground='#0056b3'
        )
        self.next_button.pack(side=tk.RIGHT, padx=5)
        
        # Initially disable previous button
        self.prev_button.config(state="disabled")
        
        # Add status bar at the bottom
        status_frame = ttk.Frame(main_container)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.status_var = tk.StringVar(value="Step 1 of 3: Enter key information")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, font=('Arial', 9))
        status_label.pack(anchor=tk.W)
    
    def center_dialog(self):
        """Center the dialog on parent window"""
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def create_info_tab(self):
        """Create the key information tab"""
        info_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(info_frame, text="Key Information")
        
        # Title
        title_label = ttk.Label(info_frame, text="PGP Key Generation", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Form fields
        form_frame = ttk.Frame(info_frame)
        form_frame.pack(fill=tk.X)
        
        # Name
        ttk.Label(form_frame, text="Full Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(form_frame, textvariable=self.name_var, width=40)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Passphrase
        ttk.Label(form_frame, text="Passphrase:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.passphrase_var = tk.StringVar()
        passphrase_entry = ttk.Entry(form_frame, textvariable=self.passphrase_var, show="*", width=40)
        passphrase_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Confirm passphrase
        ttk.Label(form_frame, text="Confirm Passphrase:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.confirm_passphrase_var = tk.StringVar()
        confirm_entry = ttk.Entry(form_frame, textvariable=self.confirm_passphrase_var, show="*", width=40)
        confirm_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Key size
        ttk.Label(form_frame, text="Key Size:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.key_size_var = tk.StringVar(value="2048")
        key_size_combo = ttk.Combobox(
            form_frame, 
            textvariable=self.key_size_var,
            values=["2048", "3072", "4096"],
            state="readonly",
            width=37
        )
        key_size_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)
        
        # Passphrase strength indicator
        self.strength_frame = ttk.Frame(info_frame)
        self.strength_frame.pack(fill=tk.X, pady=20)
        
        ttk.Label(self.strength_frame, text="Passphrase Strength:").pack(anchor=tk.W)
        self.strength_var = tk.StringVar(value="Enter a passphrase")
        self.strength_label = ttk.Label(self.strength_frame, textvariable=self.strength_var)
        self.strength_label.pack(anchor=tk.W)
        
        # Bind passphrase change event
        self.passphrase_var.trace('w', self.update_passphrase_strength)
        
        # Instructions
        instructions = tk.Text(info_frame, height=8, wrap=tk.WORD)
        instructions.pack(fill=tk.BOTH, expand=True, pady=20)
        instructions.insert(tk.END, 
            "Instructions:\n\n"
            "1. Enter your full name\n"
            "2. Choose a strong passphrase (at least 8 characters)\n"
            "3. Select your preferred key size:\n"
            "   • 2048 bits: Standard security, fast\n"
            "   • 3072 bits: Enhanced security, moderate speed\n"
            "   • 4096 bits: Maximum security, slower\n\n"
            "Your passphrase protects your private key. Choose something secure but memorable."
        )
        instructions.config(state=tk.DISABLED)
    
    def create_entropy_tab(self):
        """Create the entropy collection tab"""
        entropy_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(entropy_frame, text="Entropy Collection")
        
        # Title
        title_label = ttk.Label(entropy_frame, text="Collect Randomness", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Instructions
        instructions_text = (
            "To generate a secure key, we need to collect random data.\n"
            "Please help by moving your mouse around and typing random text below.\n\n"
            "The more random your movements and typing, the more secure your key will be."
        )
        instructions_label = ttk.Label(entropy_frame, text=instructions_text, justify=tk.CENTER)
        instructions_label.pack(pady=(0, 20))
        
        # Progress frame
        progress_frame = ttk.LabelFrame(entropy_frame, text="Collection Progress", padding="10")
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Progress bar
        self.entropy_progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.entropy_progress.pack(fill=tk.X, pady=5)
        
        # Progress label
        self.entropy_progress_var = tk.StringVar(value="Click 'Start Collection' to begin")
        ttk.Label(progress_frame, textvariable=self.entropy_progress_var).pack()
        
        # Collection controls
        control_frame = ttk.Frame(progress_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        self.start_collection_button = ttk.Button(
            control_frame, 
            text="Start Collection", 
            command=self.start_entropy_collection
        )
        self.start_collection_button.pack(side=tk.LEFT)
        
        self.stop_collection_button = ttk.Button(
            control_frame, 
            text="Stop Collection", 
            command=self.stop_entropy_collection,
            state="disabled"
        )
        self.stop_collection_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # Mouse movement area
        mouse_frame = ttk.LabelFrame(entropy_frame, text="Mouse Movement Area", padding="10")
        mouse_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.mouse_canvas = tk.Canvas(mouse_frame, bg="lightgray", height=150)
        self.mouse_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Random text input
        text_frame = ttk.LabelFrame(entropy_frame, text="Random Text Input", padding="10")
        text_frame.pack(fill=tk.X)
        
        self.random_text = tk.Text(text_frame, height=4, wrap=tk.WORD)
        self.random_text.pack(fill=tk.X)
        
        # Bind events for entropy collection
        self.mouse_canvas.bind('<Motion>', self.on_mouse_move)
        self.random_text.bind('<KeyPress>', self.on_key_press)
        self.random_text.bind('<KeyRelease>', self.on_text_change)
    
    def create_generation_tab(self):
        """Create the key generation tab"""
        generation_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(generation_frame, text="Generate Key")
        
        # Title
        title_label = ttk.Label(generation_frame, text="Key Generation", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Summary frame
        summary_frame = ttk.LabelFrame(generation_frame, text="Key Details", padding="10")
        summary_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.summary_text = tk.Text(summary_frame, height=6, wrap=tk.WORD)
        self.summary_text.pack(fill=tk.X)
        self.summary_text.config(state=tk.DISABLED)
        
        # Generation progress
        progress_frame = ttk.LabelFrame(generation_frame, text="Generation Progress", padding="10")
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.generation_progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.generation_progress.pack(fill=tk.X, pady=5)
        
        self.generation_status_var = tk.StringVar(value="Ready to generate key")
        ttk.Label(progress_frame, textvariable=self.generation_status_var).pack()
        
        # Generate button
        self.generate_button = ttk.Button(
            generation_frame, 
            text="Generate Key Pair", 
            command=self.generate_key,
            style='Action.TButton'
        )
        self.generate_button.pack(pady=20)
        
        # Result area
        result_frame = ttk.LabelFrame(generation_frame, text="Generation Result", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        self.result_text = tk.Text(result_frame, height=8, wrap=tk.WORD)
        result_scroll = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=result_scroll.set)
        
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        result_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.result_text.config(state=tk.DISABLED)
    
    def update_passphrase_strength(self, *args):
        """Update passphrase strength indicator"""
        passphrase = self.passphrase_var.get()
        
        if not passphrase:
            self.strength_var.set("Enter a passphrase")
            return
        
        # Calculate strength
        score = 0
        feedback = []
        
        if len(passphrase) >= 8:
            score += 1
        else:
            feedback.append("at least 8 characters")
        
        if len(passphrase) >= 12:
            score += 1
        
        if any(c.islower() for c in passphrase):
            score += 1
        else:
            feedback.append("lowercase letters")
        
        if any(c.isupper() for c in passphrase):
            score += 1
        else:
            feedback.append("uppercase letters")
        
        if any(c.isdigit() for c in passphrase):
            score += 1
        else:
            feedback.append("numbers")
        
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in passphrase):
            score += 1
        else:
            feedback.append("special characters")
        
        # Set strength text
        if score <= 2:
            strength_text = "Weak"
            color = "red"
        elif score <= 4:
            strength_text = "Moderate"
            color = "orange"
        else:
            strength_text = "Strong"
            color = "green"
        
        if feedback:
            strength_text += f" (add: {', '.join(feedback[:2])})"
        
        self.strength_var.set(strength_text)
    
    def start_entropy_collection(self):
        """Start entropy collection"""
        if not self.entropy_collector:
            self.entropy_collector = self.key_generator.start_entropy_collection(256)
            self.mouse_widget = MouseEntropyWidget(self.entropy_collector)
            self.keyboard_widget = KeyboardEntropyWidget(self.entropy_collector)
        
        self.entropy_collector.start_collection()
        self.start_collection_button.config(state="disabled")
        self.stop_collection_button.config(state="normal")
        
        # Start progress updates
        self.update_entropy_progress()
    
    def stop_entropy_collection(self):
        """Stop entropy collection"""
        if self.entropy_collector:
            self.entropy_collector.stop_collection()
        
        self.start_collection_button.config(state="normal")
        self.stop_collection_button.config(state="disabled")
    
    def update_entropy_progress(self):
        """Update entropy collection progress"""
        if self.entropy_collector and self.entropy_collector.is_collecting:
            stats = self.entropy_collector.get_collection_stats()
            progress = stats['progress_percentage']
            
            self.entropy_progress['value'] = progress
            self.entropy_progress_var.set(
                f"Collected {stats['entropy_bits']}/{stats['target_bits']} bits ({progress:.1f}%)"
            )
            
            if stats['is_sufficient']:
                self.entropy_progress_var.set("Sufficient entropy collected! ✓")
                self.stop_entropy_collection()
            else:
                # Schedule next update
                self.dialog.after(100, self.update_entropy_progress)
    
    def on_mouse_move(self, event):
        """Handle mouse movement for entropy"""
        if self.mouse_widget and self.entropy_collector and self.entropy_collector.is_collecting:
            self.mouse_widget.on_mouse_move(event)
            
            # Draw a small dot where the mouse moved
            x, y = event.x, event.y
            self.mouse_canvas.create_oval(x-1, y-1, x+1, y+1, fill="blue", outline="")
    
    def on_key_press(self, event):
        """Handle key press for entropy"""
        if self.keyboard_widget and self.entropy_collector and self.entropy_collector.is_collecting:
            self.keyboard_widget.on_key_press(event)
    
    def on_text_change(self, event):
        """Handle text change for entropy"""
        if self.keyboard_widget and self.entropy_collector and self.entropy_collector.is_collecting:
            text = self.random_text.get(1.0, tk.END)
            self.keyboard_widget.on_text_input(text)
    
    def validate_info(self):
        """Validate the key information"""
        name = self.name_var.get().strip()
        passphrase = self.passphrase_var.get()
        confirm = self.confirm_passphrase_var.get()
        
        if not name:
            messagebox.showerror("Error", "Please enter your full name")
            return False
        
        if len(passphrase) < 8:
            messagebox.showerror("Error", "Passphrase must be at least 8 characters long")
            return False
        
        if passphrase != confirm:
            messagebox.showerror("Error", "Passphrases do not match")
            return False
        
        return True
    
    def next_step(self):
        """Move to next step"""
        current_tab = self.notebook.index(self.notebook.select())
        
        if current_tab == 0:  # Info tab
            if self.validate_info():
                self.notebook.tab(1, state="normal")
                self.notebook.select(1)
                self.prev_button.config(state="normal")
                if hasattr(self, 'status_var'):
                    self.status_var.set("Step 2 of 3: Collect entropy for secure key generation")
            
        elif current_tab == 1:  # Entropy tab
            if self.entropy_collector and self.entropy_collector.is_sufficient():
                self.update_generation_summary()
                self.notebook.tab(2, state="normal")
                self.notebook.select(2)
                self.next_button.config(text="Generate Key", command=self.generate_key)
                if hasattr(self, 'status_var'):
                    self.status_var.set("Step 3 of 3: Generate your PGP key pair")
            else:
                messagebox.showwarning("Warning", "Please collect sufficient entropy before proceeding")
    
    def prev_step(self):
        """Move to previous step"""
        current_tab = self.notebook.index(self.notebook.select())
        
        if current_tab == 1:  # Entropy tab
            self.notebook.select(0)
            self.prev_button.config(state="disabled")
            if hasattr(self, 'status_var'):
                self.status_var.set("Step 1 of 3: Enter key information")
        
        elif current_tab == 2:  # Generation tab
            self.notebook.select(1)
            self.next_button.config(text="Next ▶", command=self.next_step)
            if hasattr(self, 'status_var'):
                self.status_var.set("Step 2 of 3: Collect entropy for secure key generation")
    
    def update_generation_summary(self):
        """Update the generation summary"""
        name = self.name_var.get()
        key_size = self.key_size_var.get()
        
        summary = f"Name: {name}\n"
        summary += f"Key Size: {key_size} bits\n"
        summary += f"Algorithm: RSA\n"
        summary += f"Entropy: {self.entropy_collector.get_entropy_bits()} bits collected"
        
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, summary)
        self.summary_text.config(state=tk.DISABLED)
    
    def generate_key(self):
        """Generate the PGP key pair"""
        self.generate_button.config(state="disabled")
        self.generation_progress.start()
        
        # Start generation in a separate thread
        self.generation_thread = threading.Thread(target=self._generate_key_thread)
        self.generation_thread.daemon = True
        self.generation_thread.start()
    
    def _generate_key_thread(self):
        """Key generation thread"""
        try:
            def progress_callback(message):
                self.dialog.after(0, lambda: self.generation_status_var.set(message))
            
            result = self.key_generator.generate_key_with_entropy(
                name=self.name_var.get(),
                email="",  # Empty email since it's not required
                passphrase=self.passphrase_var.get(),
                key_length=int(self.key_size_var.get()),
                progress_callback=progress_callback
            )
            
            # Update UI in main thread
            self.dialog.after(0, lambda: self._generation_complete(result))
            
        except Exception as e:
            error_result = {'success': False, 'error': str(e)}
            self.dialog.after(0, lambda: self._generation_complete(error_result))
    
    def _generation_complete(self, result):
        """Handle generation completion"""
        self.generation_progress.stop()
        self.generate_button.config(state="normal")
        
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        
        if result['success']:
            self.result = result
            result_message = "✓ Key pair generated successfully!\n\n"
            result_message += f"Fingerprint: {result['fingerprint']}\n"
            if 'key_id' in result:
                result_message += f"Key ID: {result['key_id']}\n"
            result_message += "\nYour new PGP key pair has been created and added to your keyring."
            
            self.generation_status_var.set("Generation completed successfully!")
            
            # Update navigation buttons for completion
            self.next_button.config(text="Close", command=self.close_dialog)
            self.status_var.set("Key generation completed successfully!")
        else:
            result_message = "✗ Key generation failed!\n\n"
            result_message += f"Error: {result['error']}\n\n"
            result_message += "Please try again or check your settings."
            
            self.generation_status_var.set("Generation failed!")
            self.status_var.set("Key generation failed - please try again")
        
        self.result_text.insert(tk.END, result_message)
        self.result_text.config(state=tk.DISABLED)
    
    def cancel(self):
        """Cancel the dialog"""
        if self.generation_thread and self.generation_thread.is_alive():
            if messagebox.askyesno("Cancel", "Key generation is in progress. Are you sure you want to cancel?"):
                self.close_dialog()
        else:
            self.close_dialog()
    
    def close_dialog(self):
        """Close the dialog"""
        if self.entropy_collector:
            self.entropy_collector.stop_collection()
        
        self.dialog.destroy()
    
    def show(self):
        """Show the dialog and return result"""
        self.dialog.wait_window()
        return self.result


class ImportKeyDialog:
    """Dialog for importing PGP keys"""
    
    def __init__(self, parent, key_generator: SecureKeyGenerator):
        """Initialize import key dialog"""
        self.parent = parent
        self.key_generator = key_generator
        self.result = None
        
        self.create_dialog()
    
    def create_dialog(self):
        """Create the import dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Import PGP Key")
        self.dialog.geometry("500x400")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.center_dialog()
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Import PGP Key", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Instructions
        instructions = ttk.Label(
            main_frame, 
            text="Import a PGP key by pasting it below or loading from a file:",
            justify=tk.CENTER
        )
        instructions.pack(pady=(0, 10))
        
        # Import method selection
        method_frame = ttk.Frame(main_frame)
        method_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.import_method = tk.StringVar(value="text")
        
        ttk.Radiobutton(
            method_frame, 
            text="Paste Key Text", 
            variable=self.import_method, 
            value="text",
            command=self.on_method_changed
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Radiobutton(
            method_frame, 
            text="Import from File", 
            variable=self.import_method, 
            value="file",
            command=self.on_method_changed
        ).pack(side=tk.LEFT)
        
        # File selection frame (initially hidden)
        self.file_frame = ttk.Frame(main_frame)
        self.file_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.selected_file_var = tk.StringVar()
        self.file_entry = ttk.Entry(self.file_frame, textvariable=self.selected_file_var, state="readonly")
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(
            self.file_frame, 
            text="Browse...", 
            command=self.browse_file
        ).pack(side=tk.RIGHT)
        
        # Key input area
        self.text_frame = ttk.Frame(main_frame)
        self.text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.key_text = tk.Text(self.text_frame, wrap=tk.WORD)
        key_scroll = ttk.Scrollbar(self.text_frame, orient="vertical", command=self.key_text.yview)
        self.key_text.configure(yscrollcommand=key_scroll.set)
        
        self.key_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        key_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initially show text input method
        self.on_method_changed()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # Left side buttons (Paste)
        ttk.Button(button_frame, text="Paste from Clipboard", command=self.paste_from_clipboard).pack(side=tk.LEFT)
        
        # Right side buttons (Cancel, Import)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Import", command=self.import_key).pack(side=tk.RIGHT, padx=(0, 10))
    
    def on_method_changed(self):
        """Handle import method change"""
        if self.import_method.get() == "file":
            self.file_frame.pack(fill=tk.X, pady=(0, 10), before=self.text_frame)
            self.text_frame.pack_forget()
        else:
            self.file_frame.pack_forget()
            self.text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
    
    def paste_from_clipboard(self):
        """Paste content from clipboard into the text area"""
        try:
            # Get clipboard content
            clipboard_content = self.dialog.clipboard_get()
            
            if clipboard_content:
                # Switch to text input mode if not already
                self.import_method.set("text")
                self.on_method_changed()
                
                # Clear existing content and paste new content
                self.key_text.delete(1.0, tk.END)
                self.key_text.insert(tk.END, clipboard_content)
                
                # Show success message
                messagebox.showinfo("Success", f"Pasted {len(clipboard_content)} characters from clipboard")
            else:
                messagebox.showwarning("Warning", "Clipboard is empty")
                
        except tk.TclError:
            messagebox.showerror("Error", "Failed to access clipboard")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste from clipboard: {str(e)}")
    
    def browse_file(self):
        """Browse for a key file"""
        filename = filedialog.askopenfilename(
            title="Select PGP Key File",
            filetypes=[
                ("PGP Key Files", "*.asc *.pgp *.gpg"),
                ("Text Files", "*.txt"),
                ("All Files", "*.*")
            ]
        )
        
        if filename:
            self.selected_file_var.set(filename)
            # Also load the content for preview
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    key_data = f.read()
                
                # Switch to text view to show the loaded content
                self.import_method.set("text")
                self.on_method_changed()
                self.key_text.delete(1.0, tk.END)
                self.key_text.insert(tk.END, key_data)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
                self.selected_file_var.set("")
    
    def center_dialog(self):
        """Center the dialog on parent window"""
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def import_key(self):
        """Import the key"""
        key_data = ""
        
        if self.import_method.get() == "file":
            # Import from file
            filename = self.selected_file_var.get()
            if not filename:
                messagebox.showerror("Error", "Please select a file to import")
                return
            
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    key_data = f.read()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read file: {str(e)}")
                return
        else:
            # Import from text
            key_data = self.key_text.get(1.0, tk.END).strip()
        
        if not key_data:
            messagebox.showerror("Error", "Please enter or load a PGP key")
            return
        
        # Validate key format
        if not ("-----BEGIN PGP" in key_data and "-----END PGP" in key_data):
            messagebox.showerror("Error", "Invalid PGP key format. Please ensure the key is in ASCII armor format.")
            return
        
        try:
            result = self.key_generator.import_key(key_data)
            
            if result['success']:
                self.result = result
                messagebox.showinfo(
                    "Success", 
                    f"Key imported successfully!\n\n"
                    f"Imported {result['imported_count']} key(s)"
                )
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", f"Failed to import key: {result['error']}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Import failed: {str(e)}")
    
    def cancel(self):
        """Cancel the dialog"""
        self.dialog.destroy()
    
    def show(self):
        """Show the dialog and return result"""
        self.dialog.wait_window()
        return self.result

