"""
Key Coordination Dialog for PGP Tool
Helps users identify and resolve key mismatch issues in chat
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class KeyCoordinationDialog:
    """Dialog to help coordinate keys between chat participants"""
    
    def __init__(self, parent, key_generator, current_profile_fingerprint=None):
        self.parent = parent
        self.key_generator = key_generator
        self.current_profile_fingerprint = current_profile_fingerprint
        self.result = None
        
    def show(self):
        """Show the key coordination dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Key Coordination Helper")
        self.dialog.geometry("600x500")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self.create_widgets()
        
        # Wait for dialog to close
        self.dialog.wait_window()
        return self.result
    
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🔑 Key Coordination Helper", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Explanation
        explanation = tk.Text(main_frame, height=4, wrap=tk.WORD, font=('Arial', 10))
        explanation.pack(fill=tk.X, pady=(0, 20))
        explanation.insert(tk.END, 
            "Key mismatch occurs when the sender encrypts messages for a different public key "
            "than the one you're using in your chat profile. This tool helps you identify "
            "which key to use and coordinate with other chat participants."
        )
        explanation.config(state=tk.DISABLED)
        
        # Current Profile Section
        profile_frame = ttk.LabelFrame(main_frame, text="Current Chat Profile", padding="10")
        profile_frame.pack(fill=tk.X, pady=(0, 20))
        
        if self.current_profile_fingerprint:
            # Show current profile info
            try:
                keys = self.key_generator.list_keys(secret=True)
                current_key = None
                for key in keys:
                    if key['fingerprint'] == self.current_profile_fingerprint:
                        current_key = key
                        break
                
                if current_key:
                    profile_info = f"Name: {current_key.get('uids', ['Unknown'])[0]}\\n"
                    profile_info += f"Fingerprint: {current_key['fingerprint']}\\n"
                    profile_info += f"Key ID: {current_key.get('keyid', 'Unknown')}"
                    
                    profile_text = tk.Text(profile_frame, height=3, wrap=tk.WORD, font=('Courier', 9))
                    profile_text.pack(fill=tk.X)
                    profile_text.insert(tk.END, profile_info)
                    profile_text.config(state=tk.DISABLED)
                else:
                    ttk.Label(profile_frame, text="Current profile not found in keyring", 
                             foreground="red").pack()
            except Exception as e:
                ttk.Label(profile_frame, text=f"Error loading profile: {str(e)}", 
                         foreground="red").pack()
        else:
            ttk.Label(profile_frame, text="No chat profile selected", 
                     foreground="orange").pack()
        
        # Available Profiles Section
        available_frame = ttk.LabelFrame(main_frame, text="Available Chat Profiles", padding="10")
        available_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Create treeview for available profiles
        columns = ('Name', 'Key ID', 'Fingerprint')
        self.profiles_tree = ttk.Treeview(available_frame, columns=columns, show='headings', height=6)
        
        # Configure columns
        self.profiles_tree.heading('Name', text='Name')
        self.profiles_tree.heading('Key ID', text='Key ID')
        self.profiles_tree.heading('Fingerprint', text='Fingerprint')
        
        self.profiles_tree.column('Name', width=200)
        self.profiles_tree.column('Key ID', width=100)
        self.profiles_tree.column('Fingerprint', width=250)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(available_frame, orient=tk.VERTICAL, command=self.profiles_tree.yview)
        self.profiles_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.profiles_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load available profiles
        self.load_available_profiles()
        
        # Action Buttons Section
        action_frame = ttk.LabelFrame(main_frame, text="Actions", padding="10")
        action_frame.pack(fill=tk.X, pady=(0, 20))
        
        button_frame = ttk.Frame(action_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Export Public Key", 
                  command=self.export_public_key).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Show Key Details", 
                  command=self.show_key_details).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Switch Profile", 
                  command=self.switch_profile).pack(side=tk.LEFT, padx=(0, 10))
        
        # Instructions
        instructions_frame = ttk.LabelFrame(main_frame, text="How to Resolve Key Mismatch", padding="10")
        instructions_frame.pack(fill=tk.X, pady=(0, 20))
        
        instructions_text = tk.Text(instructions_frame, height=4, wrap=tk.WORD, font=('Arial', 9))
        instructions_text.pack(fill=tk.X)
        instructions_text.insert(tk.END, 
            "1. Export your public key and share it with the sender\\n"
            "2. Ask the sender to import your public key and re-encrypt messages\\n"
            "3. Or try switching to a different chat profile that matches the sender's encryption\\n"
            "4. Coordinate with the sender to ensure you're both using the same public keys"
        )
        instructions_text.config(state=tk.DISABLED)
        
        # Bottom buttons
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X)
        
        ttk.Button(bottom_frame, text="Close", command=self.close_dialog).pack(side=tk.RIGHT)
    
    def load_available_profiles(self):
        """Load available key pairs into the treeview"""
        try:
            keys = self.key_generator.list_keys(secret=True)
            
            for key in keys:
                name = key.get('uids', ['Unknown'])[0]
                key_id = key.get('keyid', 'Unknown')
                fingerprint = key.get('fingerprint', 'Unknown')
                
                # Highlight current profile
                tags = ()
                if fingerprint == self.current_profile_fingerprint:
                    tags = ('current',)
                
                self.profiles_tree.insert('', tk.END, 
                                        values=(name, key_id, fingerprint),
                                        tags=tags)
            
            # Configure tag for current profile
            self.profiles_tree.tag_configure('current', background='lightblue')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load profiles: {str(e)}")
    
    def export_public_key(self):
        """Export the selected public key"""
        selection = self.profiles_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a profile to export")
            return
        
        item = self.profiles_tree.item(selection[0])
        fingerprint = item['values'][2]
        name = item['values'][0]
        
        try:
            # Export public key
            result = self.key_generator.export_public_key(fingerprint)
            if result['success']:
                # Save to file
                from tkinter import filedialog
                filename = filedialog.asksaveasfilename(
                    title="Save Public Key",
                    defaultextension=".asc",
                    filetypes=[("ASCII Armor", "*.asc"), ("Text File", "*.txt"), ("All Files", "*.*")],
                    initialvalue=f"{name.replace(' ', '_')}_public_key.asc"
                )
                
                if filename:
                    with open(filename, 'w') as f:
                        f.write(result['public_key'])
                    messagebox.showinfo("Success", f"Public key exported to {filename}")
            else:
                messagebox.showerror("Error", f"Failed to export key: {result['error']}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def show_key_details(self):
        """Show detailed information about the selected key"""
        selection = self.profiles_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a profile to view details")
            return
        
        item = self.profiles_tree.item(selection[0])
        fingerprint = item['values'][2]
        name = item['values'][0]
        key_id = item['values'][1]
        
        # Create details dialog
        details_dialog = tk.Toplevel(self.dialog)
        details_dialog.title(f"Key Details - {name}")
        details_dialog.geometry("500x400")
        details_dialog.transient(self.dialog)
        details_dialog.grab_set()
        
        # Center dialog
        details_dialog.update_idletasks()
        x = self.dialog.winfo_x() + 50
        y = self.dialog.winfo_y() + 50
        details_dialog.geometry(f"+{x}+{y}")
        
        # Content
        details_frame = ttk.Frame(details_dialog, padding="20")
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(details_frame, text=f"Key Details: {name}", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        details_text = tk.Text(details_frame, wrap=tk.WORD, font=('Courier', 10))
        details_text.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Add key information
        details_info = f"Name: {name}\\n"
        details_info += f"Key ID: {key_id}\\n"
        details_info += f"Fingerprint: {fingerprint}\\n\\n"
        
        # Try to get more details
        try:
            keys = self.key_generator.list_keys(secret=True)
            for key in keys:
                if key['fingerprint'] == fingerprint:
                    details_info += f"Algorithm: {key.get('algo', 'Unknown')}\\n"
                    details_info += f"Length: {key.get('length', 'Unknown')} bits\\n"
                    details_info += f"Created: {key.get('date', 'Unknown')}\\n"
                    details_info += f"Expires: {key.get('expires', 'Never')}\\n"
                    break
        except:
            pass
        
        details_text.insert(tk.END, details_info)
        details_text.config(state=tk.DISABLED)
        
        ttk.Button(details_frame, text="Close", 
                  command=details_dialog.destroy).pack()
    
    def switch_profile(self):
        """Switch to the selected profile"""
        selection = self.profiles_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a profile to switch to")
            return
        
        item = self.profiles_tree.item(selection[0])
        fingerprint = item['values'][2]
        name = item['values'][0]
        
        # Confirm switch
        if messagebox.askyesno("Confirm Profile Switch", 
                              f"Switch to profile '{name}'?\\n\\n"
                              f"This will change your chat profile to use this key pair."):
            self.result = {
                'action': 'switch_profile',
                'fingerprint': fingerprint,
                'name': name
            }
            self.dialog.destroy()
    
    def close_dialog(self):
        """Close the dialog"""
        self.dialog.destroy()

