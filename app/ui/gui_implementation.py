#!/usr/bin/env python3

import os
import tkinter as tk
from tkinter import scrolledtext
from queue import Queue

from ui_interface import WhisperHotkeyUI

# This will be imported from the main module
message_queue = Queue()

class WhisperHotkeyGUI(WhisperHotkeyUI):
    """
    GUI implementation of the WhisperHotkeyUI interface.
    Provides a graphical user interface for the WhisperHotkey application.
    """
    
    def __init__(self, app_name, env_file):
        """
        Initialize the GUI.
        
        Args:
            app_name (str): The name of the application
            env_file (str): Path to the environment file
        """
        self.app_name = app_name
        self.env_file = env_file
        self.root = None
        
    def setup(self):
        """Set up the GUI components."""
        self.root = tk.Tk()
        self.root.title(f"{self.app_name} - Speech-to-Text Tool")
        self.root.geometry("700x400")
        self.root.minsize(500, 300)

        # Create a frame for the log display
        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Status label
        self.status_label = tk.Label(frame, text="Ready. Press and hold left Ctrl to record.")
        self.status_label.pack(side="top", fill="x", pady=(0, 10))

        # Create a scrolled text widget for logs
        self.log_display = scrolledtext.ScrolledText(frame, wrap="word")
        self.log_display.pack(fill="both", expand=True)
        self.log_display.config(state="disabled")

        # Create a frame for buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack_configure(fill="x", padx=10, pady=10)

        # Button to open a configuration file
        self.config_button = tk.Button(
            button_frame, 
            text="Edit Configuration", 
            command=self.open_config_file
        )
        self.config_button.pack(side="left", padx=5)

        # Status indicator
        self.status_indicator = tk.Label(
            button_frame,
            text="⚪ Idle",
            font=("Arial", 10)
        )
        self.status_indicator.pack(side="right", padx=5)

        # Start polling for messages
        self.poll_messages()
        
    def poll_messages(self):
        """Check for new messages in the queue and update the display."""
        try:
            while not message_queue.empty():
                message = message_queue.get_nowait()
                self.update_log(message)
        except Exception as e:
            self.update_log(f"Error polling messages: {e}")

        # Schedule the next poll
        if self.root:
            self.root.after(100, self.poll_messages)

    def update_log(self, message):
        """
        Add a message to the log display.
        
        Args:
            message (str): The message to display in the log
        """
        if self.log_display:
            self.log_display.config(state="normal")
            self.log_display.insert("end", f"{message}\n")
            self.log_display.see("end")  # Scroll to bottom
            self.log_display.config(state="disabled")

    def update_status(self, status):
        """
        Update the status indicator.
        
        Args:
            status (str): The status message to display
        """
        if self.status_label:
            self.status_label.config(text=status)

            if "recording" in status.lower():
                self.status_indicator.config(text="🔴 Recording", fg="red")
            elif "transcribing" in status.lower():
                self.status_indicator.config(text="🔄 Processing", fg="blue")
            else:
                self.status_indicator.config(text="⚪ Idle", fg="black")

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
            
    def start(self):
        """Start the GUI main loop."""
        if not self.root:
            self.setup()
        self.root.mainloop()