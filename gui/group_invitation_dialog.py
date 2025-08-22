#!/usr/bin/env python3
"""
Group Invitation Dialog for PGP Tool
Provides GUI for managing group invitations and access control
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import time
from datetime import datetime
from typing import List, Dict, Optional, Callable


class GroupInvitationDialog:
    """Dialog for viewing and managing group invitations"""
    
    def __init__(self, parent, group_chat_handler, current_user_fingerprint: str):
        self.parent = parent
        self.group_chat_handler = group_chat_handler
        self.current_user_fingerprint = current_user_fingerprint
        self.dialog = None
        self.invitation_listbox = None
        self.invitation_details = None
        self.selected_invitation = None
        
        # Callbacks
        self.on_invitation_accepted = None
        self.on_invitation_declined = None
    
    def show_pending_invitations(self):
        """Show dialog with pending invitations"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Group Invitations")
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        self._create_invitation_widgets()
        self._load_pending_invitations()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def _create_invitation_widgets(self):
        """Create the invitation dialog widgets"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Pending Group Invitations", 
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)
        
        # Invitation list frame
        list_frame = ttk.LabelFrame(main_frame, text="Invitations", padding="5")
        list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Invitation listbox with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_container.columnconfigure(0, weight=1)
        list_container.rowconfigure(0, weight=1)
        
        self.invitation_listbox = tk.Listbox(list_container, height=8)
        self.invitation_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.invitation_listbox.bind('<<ListboxSelect>>', self._on_invitation_select)
        
        # Scrollbar for listbox
        list_scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, 
                                      command=self.invitation_listbox.yview)
        list_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.invitation_listbox.configure(yscrollcommand=list_scrollbar.set)
        
        # Details frame
        details_frame = ttk.LabelFrame(main_frame, text="Invitation Details", padding="5")
        details_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(0, weight=1)
        
        # Details text widget with scrollbar
        details_container = ttk.Frame(details_frame)
        details_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        details_container.columnconfigure(0, weight=1)
        details_container.rowconfigure(0, weight=1)
        
        self.invitation_details = tk.Text(details_container, height=8, wrap=tk.WORD, 
                                         state=tk.DISABLED)
        self.invitation_details.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for details
        details_scrollbar = ttk.Scrollbar(details_container, orient=tk.VERTICAL,
                                         command=self.invitation_details.yview)
        details_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.invitation_details.configure(yscrollcommand=details_scrollbar.set)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Buttons
        accept_button = ttk.Button(button_frame, text="Accept Invitation", 
                                  command=self._accept_invitation)
        accept_button.grid(row=0, column=0, padx=(0, 5))
        
        decline_button = ttk.Button(button_frame, text="Decline Invitation", 
                                   command=self._decline_invitation)
        decline_button.grid(row=0, column=1, padx=(0, 5))
        
        refresh_button = ttk.Button(button_frame, text="Refresh", 
                                   command=self._load_pending_invitations)
        refresh_button.grid(row=0, column=2, padx=(0, 5))
        
        close_button = ttk.Button(button_frame, text="Close", 
                                 command=self.dialog.destroy)
        close_button.grid(row=0, column=3)
        
        # Spacer to push buttons to the left
        button_frame.columnconfigure(4, weight=1)
    
    def _load_pending_invitations(self):
        """Load and display pending invitations"""
        try:
            # Clear current list
            self.invitation_listbox.delete(0, tk.END)
            self.selected_invitation = None
            self._update_invitation_details(None)
            
            # Get pending invitations from enhanced group chat handler
            if hasattr(self.group_chat_handler, 'get_pending_invitations'):
                invitations = self.group_chat_handler.get_pending_invitations(
                    self.current_user_fingerprint
                )
            else:
                invitations = []
            
            if not invitations:
                self.invitation_listbox.insert(0, "No pending invitations")
                return
            
            # Add invitations to listbox
            for invitation in invitations:
                # Format invitation display
                group_name = invitation.get('group_name', 'Unknown Group')
                inviter_name = invitation.get('inviter_name', 'Unknown')
                created_date = datetime.fromtimestamp(
                    invitation.get('created_at', time.time())
                ).strftime('%Y-%m-%d %H:%M')
                
                display_text = f"{group_name} (from {inviter_name}) - {created_date}"
                self.invitation_listbox.insert(tk.END, display_text)
            
            # Store invitation data for reference
            self.invitation_data = invitations
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load invitations: {e}")
    
    def _on_invitation_select(self, event):
        """Handle invitation selection"""
        try:
            selection = self.invitation_listbox.curselection()
            if not selection:
                return
            
            index = selection[0]
            
            # Check if there are actual invitations
            if (hasattr(self, 'invitation_data') and 
                index < len(self.invitation_data)):
                self.selected_invitation = self.invitation_data[index]
                self._update_invitation_details(self.selected_invitation)
            else:
                self.selected_invitation = None
                self._update_invitation_details(None)
                
        except Exception as e:
            print(f"ERROR: Failed to handle invitation selection: {e}")
    
    def _update_invitation_details(self, invitation: Optional[Dict]):
        """Update the invitation details display"""
        try:
            self.invitation_details.configure(state=tk.NORMAL)
            self.invitation_details.delete(1.0, tk.END)
            
            if not invitation:
                self.invitation_details.insert(tk.END, "Select an invitation to view details.")
                self.invitation_details.configure(state=tk.DISABLED)
                return
            
            # Format invitation details
            details = []
            details.append(f"Group Name: {invitation.get('group_name', 'Unknown')}")
            details.append(f"Description: {invitation.get('group_description', 'No description')}")
            details.append(f"Invited by: {invitation.get('inviter_name', 'Unknown')}")
            
            # Format dates
            created_date = datetime.fromtimestamp(
                invitation.get('created_at', time.time())
            ).strftime('%Y-%m-%d %H:%M:%S')
            details.append(f"Invitation sent: {created_date}")
            
            expires_date = datetime.fromtimestamp(
                invitation.get('expires_at', time.time())
            ).strftime('%Y-%m-%d %H:%M:%S')
            details.append(f"Expires: {expires_date}")
            
            # Check if expired
            if invitation.get('expires_at', time.time()) < time.time():
                details.append("\n⚠️ This invitation has EXPIRED")
            
            # Add message if present
            message = invitation.get('message', '').strip()
            if message:
                details.append(f"\nMessage from inviter:\n{message}")
            
            # Display details
            self.invitation_details.insert(tk.END, "\n".join(details))
            self.invitation_details.configure(state=tk.DISABLED)
            
        except Exception as e:
            print(f"ERROR: Failed to update invitation details: {e}")
    
    def _accept_invitation(self):
        """Accept the selected invitation"""
        try:
            if not self.selected_invitation:
                messagebox.showwarning("No Selection", "Please select an invitation to accept.")
                return
            
            # Check if invitation is expired
            if self.selected_invitation.get('expires_at', time.time()) < time.time():
                messagebox.showerror("Expired", "This invitation has expired and cannot be accepted.")
                return
            
            # Get passphrase for decrypting group key
            passphrase = simpledialog.askstring(
                "Passphrase Required",
                "Enter your PGP passphrase to decrypt the group key:",
                show='*'
            )
            
            if passphrase is None:  # User cancelled
                return
            
            # Accept the invitation
            invitation_id = self.selected_invitation['invitation_id']
            
            if hasattr(self.group_chat_handler, 'accept_group_invitation'):
                success = self.group_chat_handler.accept_group_invitation(
                    invitation_id, self.current_user_fingerprint, passphrase
                )
            else:
                success = False
            
            if success:
                messagebox.showinfo("Success", 
                    f"Successfully joined group '{self.selected_invitation['group_name']}'!")
                
                # Trigger callback if set
                if self.on_invitation_accepted:
                    self.on_invitation_accepted(self.selected_invitation)
                
                # Refresh the invitation list
                self._load_pending_invitations()
            else:
                messagebox.showerror("Error", "Failed to accept invitation. Please check your passphrase.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to accept invitation: {e}")
    
    def _decline_invitation(self):
        """Decline the selected invitation"""
        try:
            if not self.selected_invitation:
                messagebox.showwarning("No Selection", "Please select an invitation to decline.")
                return
            
            # Confirm decline
            result = messagebox.askyesno(
                "Confirm Decline",
                f"Are you sure you want to decline the invitation to join "
                f"'{self.selected_invitation['group_name']}'?"
            )
            
            if not result:
                return
            
            # Decline the invitation
            invitation_id = self.selected_invitation['invitation_id']
            
            if hasattr(self.group_chat_handler, 'access_controller'):
                success = self.group_chat_handler.access_controller.decline_invitation(
                    invitation_id, self.current_user_fingerprint
                )
            else:
                success = False
            
            if success:
                messagebox.showinfo("Declined", 
                    f"Declined invitation to join '{self.selected_invitation['group_name']}'.")
                
                # Trigger callback if set
                if self.on_invitation_declined:
                    self.on_invitation_declined(self.selected_invitation)
                
                # Refresh the invitation list
                self._load_pending_invitations()
            else:
                messagebox.showerror("Error", "Failed to decline invitation.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to decline invitation: {e}")


class CreateSecureGroupDialog:
    """Dialog for creating new secure groups"""
    
    def __init__(self, parent, group_chat_handler, current_user_fingerprint: str, current_user_name: str):
        self.parent = parent
        self.group_chat_handler = group_chat_handler
        self.current_user_fingerprint = current_user_fingerprint
        self.current_user_name = current_user_name
        self.dialog = None
        self.result = None
        
        # Callbacks
        self.on_group_created = None
    
    def show_create_group_dialog(self) -> Optional[Dict]:
        """Show dialog to create a new secure group"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Create Secure Group")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        self._create_group_widgets()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Wait for dialog to close
        self.dialog.wait_window()
        
        return self.result
    
    def _create_group_widgets(self):
        """Create the group creation dialog widgets"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Create Secure Group", 
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky=tk.W)
        
        # Group name
        ttk.Label(main_frame, text="Group Name:").grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        self.group_name_var = tk.StringVar()
        group_name_entry = ttk.Entry(main_frame, textvariable=self.group_name_var, width=30)
        group_name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        group_name_entry.focus()
        
        # Description
        ttk.Label(main_frame, text="Description:").grid(row=2, column=0, sticky=(tk.W, tk.N), pady=(0, 10))
        self.description_text = tk.Text(main_frame, height=4, width=30, wrap=tk.WORD)
        self.description_text.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Security info
        security_frame = ttk.LabelFrame(main_frame, text="Security Settings", padding="10")
        security_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        security_frame.columnconfigure(0, weight=1)
        
        security_info = (
            "• Invitation-only access control\n"
            "• End-to-end encryption with shared group key\n"
            "• Only invited members can join and decrypt messages\n"
            "• You will be the group creator and admin"
        )
        
        ttk.Label(security_frame, text=security_info, justify=tk.LEFT).grid(row=0, column=0, sticky=tk.W)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Buttons
        create_button = ttk.Button(button_frame, text="Create Group", 
                                  command=self._create_group)
        create_button.grid(row=0, column=0, padx=(0, 10))
        
        cancel_button = ttk.Button(button_frame, text="Cancel", 
                                  command=self._cancel)
        cancel_button.grid(row=0, column=1)
        
        # Spacer
        button_frame.columnconfigure(2, weight=1)
        
        # Bind Enter key to create
        self.dialog.bind('<Return>', lambda e: self._create_group())
        self.dialog.bind('<Escape>', lambda e: self._cancel())
    
    def _create_group(self):
        """Create the secure group"""
        try:
            group_name = self.group_name_var.get().strip()
            description = self.description_text.get(1.0, tk.END).strip()
            
            if not group_name:
                messagebox.showerror("Error", "Please enter a group name.")
                return
            
            # Validate group name (basic validation)
            if len(group_name) < 3:
                messagebox.showerror("Error", "Group name must be at least 3 characters long.")
                return
            
            if len(group_name) > 50:
                messagebox.showerror("Error", "Group name must be 50 characters or less.")
                return
            
            # Check if group already exists
            existing_groups = self.group_chat_handler.get_user_groups(self.current_user_fingerprint)
            for group in existing_groups:
                if group['name'].lower() == group_name.lower():
                    messagebox.showerror("Error", f"You already have a group named '{group_name}'.")
                    return
            
            # Create the secure group
            if hasattr(self.group_chat_handler, 'create_secure_group'):
                success = self.group_chat_handler.create_secure_group(
                    group_name, self.current_user_name, 
                    self.current_user_fingerprint, description
                )
            else:
                success = False
            
            if success:
                self.result = {
                    'name': group_name,
                    'description': description,
                    'creator': self.current_user_name
                }
                
                messagebox.showinfo("Success", f"Secure group '{group_name}' created successfully!")
                
                # Trigger callback if set
                if self.on_group_created:
                    self.on_group_created(self.result)
                
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to create secure group.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create group: {e}")
    
    def _cancel(self):
        """Cancel group creation"""
        self.result = None
        self.dialog.destroy()


class InviteMemberDialog:
    """Dialog for inviting members to a secure group"""
    
    def __init__(self, parent, group_chat_handler, current_user_fingerprint: str, group_name: str):
        self.parent = parent
        self.group_chat_handler = group_chat_handler
        self.current_user_fingerprint = current_user_fingerprint
        self.group_name = group_name
        self.dialog = None
        self.result = None
        
        # Callbacks
        self.on_member_invited = None
    
    def show_invite_dialog(self) -> Optional[Dict]:
        """Show dialog to invite a member to the group"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(f"Invite Member to {self.group_name}")
        self.dialog.geometry("450x350")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        self._create_invite_widgets()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Wait for dialog to close
        self.dialog.wait_window()
        
        return self.result
    
    def _create_invite_widgets(self):
        """Create the member invitation dialog widgets"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text=f"Invite Member to '{self.group_name}'", 
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky=tk.W)
        
        # Member name
        ttk.Label(main_frame, text="Member Name:").grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        self.member_name_var = tk.StringVar()
        member_name_entry = ttk.Entry(main_frame, textvariable=self.member_name_var, width=30)
        member_name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        member_name_entry.focus()
        
        # PGP fingerprint
        ttk.Label(main_frame, text="PGP Fingerprint:").grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        self.fingerprint_var = tk.StringVar()
        fingerprint_entry = ttk.Entry(main_frame, textvariable=self.fingerprint_var, width=30)
        fingerprint_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Fingerprint help
        help_text = "Enter the full PGP fingerprint (40 characters) of the person you want to invite."
        ttk.Label(main_frame, text=help_text, font=("Arial", 8), 
                 foreground="gray").grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Invitation message
        ttk.Label(main_frame, text="Message (optional):").grid(row=4, column=0, sticky=(tk.W, tk.N), pady=(0, 10))
        self.message_text = tk.Text(main_frame, height=4, width=30, wrap=tk.WORD)
        self.message_text.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Security info
        security_frame = ttk.LabelFrame(main_frame, text="Security Note", padding="10")
        security_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        security_frame.columnconfigure(0, weight=1)
        
        security_info = (
            "The invitation will be encrypted with the member's public key.\n"
            "Only they will be able to decrypt and accept the invitation.\n"
            "Make sure you have their correct PGP fingerprint."
        )
        
        ttk.Label(security_frame, text=security_info, justify=tk.LEFT, 
                 font=("Arial", 8)).grid(row=0, column=0, sticky=tk.W)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Buttons
        invite_button = ttk.Button(button_frame, text="Send Invitation", 
                                  command=self._send_invitation)
        invite_button.grid(row=0, column=0, padx=(0, 10))
        
        cancel_button = ttk.Button(button_frame, text="Cancel", 
                                  command=self._cancel)
        cancel_button.grid(row=0, column=1)
        
        # Spacer
        button_frame.columnconfigure(2, weight=1)
        
        # Bind Enter key to invite
        self.dialog.bind('<Return>', lambda e: self._send_invitation())
        self.dialog.bind('<Escape>', lambda e: self._cancel())
    
    def _send_invitation(self):
        """Send the group invitation"""
        try:
            member_name = self.member_name_var.get().strip()
            fingerprint = self.fingerprint_var.get().strip().replace(" ", "").upper()
            message = self.message_text.get(1.0, tk.END).strip()
            
            if not member_name:
                messagebox.showerror("Error", "Please enter the member's name.")
                return
            
            if not fingerprint:
                messagebox.showerror("Error", "Please enter the member's PGP fingerprint.")
                return
            
            # Validate fingerprint format (basic validation)
            if len(fingerprint) != 40:
                messagebox.showerror("Error", "PGP fingerprint must be exactly 40 characters long.")
                return
            
            if not all(c in '0123456789ABCDEF' for c in fingerprint):
                messagebox.showerror("Error", "PGP fingerprint must contain only hexadecimal characters (0-9, A-F).")
                return
            
            # Send the invitation
            if hasattr(self.group_chat_handler, 'invite_member_to_group'):
                success = self.group_chat_handler.invite_member_to_group(
                    self.group_name, self.current_user_fingerprint,
                    fingerprint, member_name, message
                )
            else:
                success = False
            
            if success:
                self.result = {
                    'member_name': member_name,
                    'fingerprint': fingerprint,
                    'message': message
                }
                
                messagebox.showinfo("Success", f"Invitation sent to {member_name}!")
                
                # Trigger callback if set
                if self.on_member_invited:
                    self.on_member_invited(self.result)
                
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to send invitation. Please check the fingerprint and try again.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send invitation: {e}")
    
    def _cancel(self):
        """Cancel invitation"""
        self.result = None
        self.dialog.destroy()

