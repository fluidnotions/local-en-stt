#!/usr/bin/env python3

from abc import ABC, abstractmethod

class WhisperHotkeyUI(ABC):
    """
    Interface for WhisperHotkey UI implementations.
    This abstract base class defines the methods that must be implemented
    by any UI implementation (GUI or terminal).
    """
    
    @abstractmethod
    def update_log(self, message):
        """
        Add a message to the log display.
        
        Args:
            message (str): The message to display in the log
        """
        pass
    
    @abstractmethod
    def update_status(self, status):
        """
        Update the status indicator.
        
        Args:
            status (str): The status message to display
        """
        pass
    
    @abstractmethod
    def open_config_file(self):
        """
        Open the configuration file for editing.
        """
        pass
    
    @abstractmethod
    def start(self):
        """
        Start the UI. This might involve starting a main loop for GUI
        or just initializing for terminal UI.
        """
        pass