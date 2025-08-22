#!/usr/bin/env python3
"""
Test script for Key Generation Dialog Navigation Fix
Tests that the navigation buttons are working properly
"""

import os
import sys
import tkinter as tk
from tkinter import ttk

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_dialog_navigation():
    """Test the key generation dialog navigation"""
    print("Testing Key Generation Dialog Navigation...")
    
    try:
        # Import required modules
        from crypto.key_generator import SecureKeyGenerator
        from gui.dialogs import KeyGenerationDialog
        
        print("✓ Successfully imported dialog classes")
        
        # Create a test window
        root = tk.Tk()
        root.title("Navigation Test")
        root.geometry("300x200")
        
        # Create a temporary key generator
        import tempfile
        test_dir = tempfile.mkdtemp(prefix="nav_test_")
        key_generator = SecureKeyGenerator(test_dir)
        
        def open_dialog():
            """Open the key generation dialog"""
            dialog = KeyGenerationDialog(root, key_generator)
            result = dialog.show()
            print(f"Dialog result: {result}")
        
        # Create test button
        test_button = ttk.Button(
            root, 
            text="Test Key Generation Dialog\n(Check Navigation Buttons)", 
            command=open_dialog
        )
        test_button.pack(expand=True)
        
        # Instructions
        instructions = tk.Label(
            root,
            text="Click the button to test the dialog.\nCheck that navigation buttons are visible\nand working at the bottom.",
            justify=tk.CENTER
        )
        instructions.pack(pady=10)
        
        print("✓ Test window created")
        print("\nInstructions:")
        print("1. Click 'Test Key Generation Dialog' button")
        print("2. Verify navigation buttons are visible at the bottom")
        print("3. Test that 'Next ▶' button works to move between tabs")
        print("4. Test that '◀ Previous' button works")
        print("5. Check status bar updates")
        print("\nExpected navigation buttons:")
        print("- ◀ Previous (left side)")
        print("- Cancel (center-right)")
        print("- Next ▶ (right side)")
        print("\nClose this window when done testing.")
        
        root.mainloop()
        
        # Cleanup
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        
        return True
        
    except Exception as e:
        print(f"✗ Navigation test failed: {e}")
        return False

def test_button_layout():
    """Test button layout independently"""
    print("\nTesting button layout...")
    
    try:
        root = tk.Tk()
        root.title("Button Layout Test")
        root.geometry("600x400")
        
        # Simulate the dialog layout
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Notebook (simulated)
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Add some tabs
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="Key Information")
        ttk.Label(tab1, text="This is tab 1 content").pack(pady=50)
        
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="Entropy Collection")
        ttk.Label(tab2, text="This is tab 2 content").pack(pady=50)
        
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="Generate Key")
        ttk.Label(tab3, text="This is tab 3 content").pack(pady=50)
        
        # Add separator
        separator = ttk.Separator(root, orient='horizontal')
        separator.pack(fill=tk.X, padx=10, pady=(5, 5))
        
        # Button frame
        button_frame = ttk.Frame(root)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Navigation buttons
        prev_button = ttk.Button(
            button_frame, 
            text="◀ Previous", 
            width=12
        )
        prev_button.pack(side=tk.LEFT, padx=5)
        
        # Center spacer
        spacer = ttk.Frame(button_frame)
        spacer.pack(side=tk.LEFT, expand=True)
        
        cancel_button = ttk.Button(
            button_frame, 
            text="Cancel", 
            width=10
        )
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        next_button = ttk.Button(
            button_frame, 
            text="Next ▶", 
            width=12
        )
        next_button.pack(side=tk.RIGHT, padx=5)
        
        # Status bar
        status_frame = ttk.Frame(root)
        status_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        status_var = tk.StringVar(value="Step 1 of 3: Enter key information")
        status_label = ttk.Label(status_frame, textvariable=status_var, font=('Arial', 9))
        status_label.pack(anchor=tk.W)
        
        print("✓ Button layout test window created")
        print("Check that buttons are properly positioned:")
        print("- Previous button on the left")
        print("- Cancel and Next buttons on the right")
        print("- Status bar at the bottom")
        
        root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"✗ Button layout test failed: {e}")
        return False

def main():
    """Run navigation tests"""
    print("PGP Tool - Navigation Fix Test Suite")
    print("=" * 40)
    
    tests = [
        ("Button Layout", test_button_layout),
        ("Dialog Navigation", test_dialog_navigation)
    ]
    
    for test_name, test_func in tests:
        print(f"\n{test_name} Test:")
        print("-" * (len(test_name) + 6))
        
        try:
            if test_func():
                print(f"✓ {test_name} test completed")
            else:
                print(f"✗ {test_name} test failed")
        except Exception as e:
            print(f"✗ {test_name} test failed with exception: {e}")
    
    print("\n" + "=" * 40)
    print("Navigation fix testing completed.")
    print("The dialog should now have visible navigation buttons at the bottom.")

if __name__ == "__main__":
    main()

