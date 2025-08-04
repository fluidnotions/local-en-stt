#!/usr/bin/env python3

import os
import sys
import threading
from queue import Queue

from ui_interface import WhisperHotkeyUI

class WhisperHotkeyTerminal(WhisperHotkeyUI):
    """
    Terminal implementation of the WhisperHotkeyUI interface.
    Provides a text-based interface for the WhisperHotkey application.
    """
    
    def __init__(self, app_name, env_file):
        """
        Initialize the terminal UI.
        
        Args:
            app_name (str): The name of the application
            env_file (str): Path to the environment file
        """
        self.app_name = app_name
        self.env_file = env_file
        self.current_status = "Ready. Press and hold left Ctrl to record."
        self.message_queue = Queue()
        self.running = False
        self.log_thread = None
        
    def update_log(self, message):
        """
        Add a message to the log display.
        
        Args:
            message (str): The message to display in the log
        """
        # In terminal mode, we just print the message directly
        # We don't use the overridden print function to avoid recursion
        sys.stdout.write(f"{message}\n")
        sys.stdout.flush()
        
    def update_status(self, status):
        """
        Update the status indicator.
        
        Args:
            status (str): The status message to display
        """
        self.current_status = status
        
        # Display status with appropriate indicator
        if "recording" in status.lower():
            indicator = "🔴 Recording"
        elif "transcribing" in status.lower():
            indicator = "🔄 Processing"
        else:
            indicator = "⚪ Idle"
            
        # Print the status update
        sys.stdout.write(f"\n--- Status: {indicator} - {status} ---\n")
        sys.stdout.flush()
        
    def open_config_file(self):
        """Open the configuration file for editing."""
        print(f"Opening configuration file: {self.env_file}")
        try:
            # On macOS, use the 'open' command
            if os.name == 'posix':
                os.system(f"open {self.env_file}")
            # On Windows, use the default editor
            elif os.name == 'nt':
                os.system(f"start {self.env_file}")
            else:
                print(f"Please manually edit the config file at: {self.env_file}")
        except Exception as e:
            print(f"Error opening config file: {e}")
    
    def _print_header(self):
        """Print the application header."""
        print("\n" + "=" * 60)
        print(f"{self.app_name} - Speech-to-Text Tool (Terminal Mode)")
        print("=" * 60)
        print(f"Current status: {self.current_status}")
        print("-" * 60)
        print("Press and hold left Ctrl to record speech.")
        print("Speech will be transcribed and typed when you release the key.")
        print("-" * 60 + "\n")
    
    def start(self):
        """Start the terminal UI."""
        self._print_header()
        
        # In terminal mode, we don't need a main loop like in GUI
        # We just need to keep the application running
        self.running = True
        
        # We could add a simple command loop here if needed
        # For now, we just keep the application running
        # The main thread will handle keyboard events