#!/usr/bin/env python3
"""
PGP Encryption Tool - Main Entry Point
A secure offline PGP encryption and decryption tool with GUI
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []
    
    try:
        import tkinter
    except ImportError:
        missing_deps.append("tkinter")
    
    try:
        import cryptography
    except ImportError:
        missing_deps.append("cryptography")
    
    try:
        import PIL
    except ImportError:
        missing_deps.append("pillow")
    
    # IRC is optional for chat functionality
    try:
        import irc
    except ImportError:
        print("Warning: IRC library not available - chat functionality will be disabled")
    
    return missing_deps

def show_error_dialog(title, message):
    """Show error dialog"""
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showerror(title, message)
        root.destroy()
    except:
        print(f"ERROR: {title}")
        print(message)

def main():
    """Main application entry point"""
    print("Starting PGP Encryption Tool v4.2.0...")
    
    # Check dependencies
    missing_deps = check_dependencies()
    if missing_deps:
        error_msg = (
            "Missing required dependencies:\n\n" +
            "\n".join(f"• {dep}" for dep in missing_deps) +
            "\n\nPlease install the missing packages and try again.\n\n" +
            "You can install them using:\n" +
            f"pip install {' '.join(missing_deps)}"
        )
        show_error_dialog("Missing Dependencies", error_msg)
        return 1
    
    # Import and start the GUI (login will be handled by MainWindow)
    try:
        from gui.main_window import PGPToolMainWindow
        
        # Create and run the application
        app = PGPToolMainWindow()
        app.run()
        
        return 0
        
    except ImportError as e:
        error_msg = (
            f"Failed to import GUI modules: {str(e)}\n\n"
            "Please ensure all application files are present and try again."
        )
        show_error_dialog("Import Error", error_msg)
        return 1
    
    except Exception as e:
        error_msg = (
            f"An unexpected error occurred: {str(e)}\n\n"
            "Please check the console for more details."
        )
        show_error_dialog("Application Error", error_msg)
        print(f"Full error details: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

