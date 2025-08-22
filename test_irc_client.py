"""
IRC Client Test Interface
Simple GUI to test IRC connectivity before PGP integration
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chat.irc_client import PGPIRCClient, IRCNetworks


class IRCTestWindow:
    """Simple test window for IRC client"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("IRC Client Test - PGP Tool v4.2.0")
        self.root.geometry("800x600")
        
        self.irc_client = PGPIRCClient()
        self.setup_callbacks()
        self.create_interface()
        
    def setup_callbacks(self):
        """Setup IRC client callbacks"""
        self.irc_client.set_connect_callback(self.on_irc_connect)
        self.irc_client.set_disconnect_callback(self.on_irc_disconnect)
        self.irc_client.set_message_callback(self.on_irc_message)
        self.irc_client.set_error_callback(self.on_irc_error)
        
    def create_interface(self):
        """Create the test interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Connection section
        self.create_connection_section(main_frame)
        
        # Status section
        self.create_status_section(main_frame)
        
        # Message section
        self.create_message_section(main_frame)
        
        # Chat section
        self.create_chat_section(main_frame)
        
    def create_connection_section(self, parent):
        """Create connection controls"""
        # Connection frame
        conn_frame = ttk.LabelFrame(parent, text="IRC Connection", padding="5")
        conn_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        conn_frame.columnconfigure(1, weight=1)
        
        # Network selection
        ttk.Label(conn_frame, text="Network:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.network_var = tk.StringVar(value="libera")
        self.network_combo = ttk.Combobox(
            conn_frame, 
            textvariable=self.network_var,
            values=list(IRCNetworks.NETWORKS.keys()),
            state="readonly",
            width=15
        )
        self.network_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        # Nickname
        ttk.Label(conn_frame, text="Nickname:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        self.nickname_var = tk.StringVar()
        self.nickname_entry = ttk.Entry(conn_frame, textvariable=self.nickname_var, width=15)
        self.nickname_entry.grid(row=0, column=3, sticky=tk.W, padx=(0, 10))
        
        # Random nickname button
        ttk.Button(
            conn_frame, 
            text="Random", 
            command=self.generate_random_nick,
            width=8
        ).grid(row=0, column=4, padx=(0, 10))
        
        # Connect/Disconnect button
        self.connect_button = ttk.Button(
            conn_frame, 
            text="Connect", 
            command=self.toggle_connection,
            width=10
        )
        self.connect_button.grid(row=0, column=5)
        
        # Custom server section
        ttk.Label(conn_frame, text="Custom Server:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.custom_server_var = tk.StringVar()
        self.custom_server_entry = ttk.Entry(conn_frame, textvariable=self.custom_server_var, width=30)
        self.custom_server_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0), padx=(0, 10))
        
        ttk.Label(conn_frame, text="Port:").grid(row=1, column=3, sticky=tk.W, pady=(5, 0), padx=(10, 5))
        self.custom_port_var = tk.StringVar(value="6697")
        self.custom_port_entry = ttk.Entry(conn_frame, textvariable=self.custom_port_var, width=8)
        self.custom_port_entry.grid(row=1, column=4, sticky=tk.W, pady=(5, 0))
        
        ttk.Button(
            conn_frame, 
            text="Add Custom", 
            command=self.add_custom_server,
            width=10
        ).grid(row=1, column=5, pady=(5, 0))
        
    def create_status_section(self, parent):
        """Create status display"""
        status_frame = ttk.LabelFrame(parent, text="Status", padding="5")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        # Status labels
        ttk.Label(status_frame, text="Connection:").grid(row=0, column=0, sticky=tk.W)
        self.status_label = ttk.Label(status_frame, text="Disconnected", foreground="red")
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        ttk.Label(status_frame, text="Network:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        self.network_label = ttk.Label(status_frame, text="None")
        self.network_label.grid(row=0, column=3, sticky=tk.W, padx=(5, 0))
        
        ttk.Label(status_frame, text="Nickname:").grid(row=0, column=4, sticky=tk.W, padx=(20, 0))
        self.nick_label = ttk.Label(status_frame, text="None")
        self.nick_label.grid(row=0, column=5, sticky=tk.W, padx=(5, 0))
        
    def create_message_section(self, parent):
        """Create message sending controls"""
        msg_frame = ttk.LabelFrame(parent, text="Send Message", padding="5")
        msg_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        msg_frame.columnconfigure(1, weight=1)
        
        # Target nickname
        ttk.Label(msg_frame, text="To:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.target_var = tk.StringVar()
        self.target_entry = ttk.Entry(msg_frame, textvariable=self.target_var, width=20)
        self.target_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        # Message text
        ttk.Label(msg_frame, text="Message:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        self.message_var = tk.StringVar()
        self.message_entry = ttk.Entry(msg_frame, textvariable=self.message_var)
        self.message_entry.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(0, 10))
        self.message_entry.bind('<Return>', lambda e: self.send_message())
        
        # Send button
        self.send_button = ttk.Button(
            msg_frame, 
            text="Send", 
            command=self.send_message,
            state="disabled"
        )
        self.send_button.grid(row=0, column=4)
        
    def create_chat_section(self, parent):
        """Create chat display"""
        chat_frame = ttk.LabelFrame(parent, text="Chat Log", padding="5")
        chat_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
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
        
        # Clear button
        ttk.Button(
            chat_frame, 
            text="Clear Log", 
            command=self.clear_chat
        ).grid(row=1, column=0, pady=(5, 0))
        
    def generate_random_nick(self):
        """Generate a random nickname"""
        random_nick = self.irc_client.generate_random_nickname()
        self.nickname_var.set(random_nick)
        
    def add_custom_server(self):
        """Add a custom server"""
        server = self.custom_server_var.get().strip()
        port_str = self.custom_port_var.get().strip()
        
        if not server:
            messagebox.showerror("Error", "Please enter a server address")
            return
            
        try:
            port = int(port_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid port number")
            return
            
        # Add to IRC client
        custom_name = f"custom_{len(self.irc_client.custom_servers) + 1}"
        self.irc_client.add_custom_server(custom_name, server, port, port == 6697)
        
        # Update combo box
        networks = list(IRCNetworks.NETWORKS.keys()) + list(self.irc_client.custom_servers.keys())
        self.network_combo['values'] = networks
        self.network_var.set(custom_name)
        
        self.log_message("SYSTEM", f"Added custom server: {server}:{port}")
        
    def toggle_connection(self):
        """Connect or disconnect from IRC"""
        if self.irc_client.connected:
            self.disconnect_irc()
        else:
            self.connect_irc()
            
    def connect_irc(self):
        """Connect to IRC"""
        network = self.network_var.get()
        nickname = self.nickname_var.get().strip()
        
        if not nickname:
            nickname = self.irc_client.generate_random_nickname()
            self.nickname_var.set(nickname)
            
        self.log_message("SYSTEM", f"Connecting to {network} as {nickname}...")
        
        try:
            success = self.irc_client.connect_to_network(network, nickname)
            if not success:
                self.log_message("ERROR", "Failed to initiate connection")
        except Exception as e:
            self.log_message("ERROR", f"Connection error: {str(e)}")
            
    def disconnect_irc(self):
        """Disconnect from IRC"""
        self.log_message("SYSTEM", "Disconnecting...")
        self.irc_client.disconnect()
        
    def send_message(self):
        """Send a message"""
        if not self.irc_client.connected:
            messagebox.showerror("Error", "Not connected to IRC")
            return
            
        target = self.target_var.get().strip()
        message = self.message_var.get().strip()
        
        if not target or not message:
            messagebox.showerror("Error", "Please enter target nickname and message")
            return
            
        try:
            self.irc_client.send_private_message(target, message)
            self.log_message(f"TO {target}", message)
            self.message_var.set("")  # Clear message field
        except Exception as e:
            self.log_message("ERROR", f"Failed to send message: {str(e)}")
            
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
        
    def update_status(self):
        """Update status display"""
        status = self.irc_client.get_connection_status()
        
        if status["connected"]:
            self.status_label.config(text="Connected", foreground="green")
            self.connect_button.config(text="Disconnect")
            self.send_button.config(state="normal")
        else:
            self.status_label.config(text="Disconnected", foreground="red")
            self.connect_button.config(text="Connect")
            self.send_button.config(state="disabled")
            
        self.network_label.config(text=status["network"] or "None")
        self.nick_label.config(text=status["nickname"] or "None")
        
    # IRC Event Callbacks
    def on_irc_connect(self, network, nickname):
        """Handle IRC connection"""
        self.log_message("SYSTEM", f"Connected to {network} as {nickname}")
        self.root.after(0, self.update_status)
        
    def on_irc_disconnect(self):
        """Handle IRC disconnection"""
        self.log_message("SYSTEM", "Disconnected from IRC")
        self.root.after(0, self.update_status)
        
    def on_irc_message(self, sender, message):
        """Handle incoming IRC message"""
        self.log_message(f"FROM {sender}", message)
        
    def on_irc_error(self, error):
        """Handle IRC error"""
        self.log_message("ERROR", error)
        
    def run(self):
        """Start the test interface"""
        # Generate initial random nickname
        self.generate_random_nick()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start GUI
        self.root.mainloop()
        
    def on_closing(self):
        """Handle window closing"""
        if self.irc_client.connected:
            self.irc_client.disconnect()
        self.root.destroy()


def main():
    """Run IRC client test"""
    import datetime
    
    # Fix datetime import for log_message
    tk.datetime = datetime
    
    print("Starting IRC Client Test...")
    app = IRCTestWindow()
    app.run()


if __name__ == "__main__":
    main()

