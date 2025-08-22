"""
Entropy Collection Module
Collects entropy from user interactions for secure key generation
"""

import time
import hashlib
import secrets
import threading
from typing import List, Callable, Optional
from collections import deque


class EntropyCollector:
    """Collects entropy from various user interactions"""
    
    def __init__(self, target_bits: int = 256):
        """
        Initialize entropy collector
        
        Args:
            target_bits: Target number of entropy bits to collect
        """
        self.target_bits = target_bits
        self.entropy_data = deque(maxlen=1000)  # Store recent entropy events
        self.is_collecting = False
        self.collection_start_time = None
        self.callbacks = []  # Progress callbacks
        
        # Add missing attributes for compatibility
        self.text_input_count = 0
        self.mouse_movement_time = 0
        
        # Initialize with system entropy
        self._add_system_entropy()
    
    def _add_system_entropy(self):
        """Add initial system entropy"""
        system_entropy = secrets.token_bytes(32)
        timestamp = time.time_ns()
        
        # Combine system entropy with timestamp
        entropy_hash = hashlib.sha256(
            system_entropy + timestamp.to_bytes(8, 'big')
        ).digest()
        
        for byte in entropy_hash:
            self.entropy_data.append(byte)
    
    def start_collection(self):
        """Start entropy collection"""
        self.is_collecting = True
        self.collection_start_time = time.time()
        # Reset counters
        self.text_input_count = 0
        self.mouse_movement_time = 0
        self._notify_callbacks()
    
    def stop_collection(self):
        """Stop entropy collection"""
        self.is_collecting = False
        self._notify_callbacks()
    
    def add_mouse_movement(self, x: int, y: int):
        """
        Add entropy from mouse movement
        
        Args:
            x: Mouse X coordinate
            y: Mouse Y coordinate
        """
        if not self.is_collecting:
            return
        
        timestamp = time.time_ns()
        
        # Create entropy from coordinates and timing
        entropy_bytes = hashlib.sha256(
            x.to_bytes(4, 'big') + 
            y.to_bytes(4, 'big') + 
            timestamp.to_bytes(8, 'big')
        ).digest()
        
        # Add to entropy pool
        for byte in entropy_bytes[:4]:  # Use first 4 bytes
            self.entropy_data.append(byte)
        
        self._notify_callbacks()
    
    def add_key_press(self, key_code: int, press_time: float):
        """
        Add entropy from key press timing
        
        Args:
            key_code: Key code that was pressed
            press_time: Time when key was pressed
        """
        if not self.is_collecting:
            return
        
        timestamp = time.time_ns()
        
        # Create entropy from key timing
        entropy_bytes = hashlib.sha256(
            key_code.to_bytes(4, 'big') + 
            int(press_time * 1000000).to_bytes(8, 'big') + 
            timestamp.to_bytes(8, 'big')
        ).digest()
        
        # Add to entropy pool
        for byte in entropy_bytes[:3]:  # Use first 3 bytes
            self.entropy_data.append(byte)
        
        self._notify_callbacks()
    
    def add_random_text(self, text: str):
        """
        Add entropy from random text input
        
        Args:
            text: Random text typed by user
        """
        if not self.is_collecting:
            return
        
        # Update character count for compatibility
        self.text_input_count += len(text)
        
        timestamp = time.time_ns()
        
        # Create entropy from text and timing
        entropy_bytes = hashlib.sha256(
            text.encode('utf-8') + 
            timestamp.to_bytes(8, 'big')
        ).digest()
        
        # Add to entropy pool
        for byte in entropy_bytes[:4]:  # Use first 4 bytes
            self.entropy_data.append(byte)
        
        self._notify_callbacks()
    
    def get_entropy_bits(self) -> int:
        """
        Estimate collected entropy bits
        
        Returns:
            Estimated entropy bits collected
        """
        if len(self.entropy_data) == 0:
            return 0
        
        # Simple entropy estimation based on data collected
        # In practice, this would use more sophisticated entropy estimation
        unique_bytes = len(set(self.entropy_data))
        total_bytes = len(self.entropy_data)
        
        # Estimate entropy (simplified)
        if total_bytes == 0:
            return 0
        
        entropy_per_byte = min(8, unique_bytes / total_bytes * 8)
        estimated_bits = int(total_bytes * entropy_per_byte * 0.5)  # Conservative estimate
        
        return min(estimated_bits, self.target_bits)
    
    def get_progress_percentage(self) -> float:
        """
        Get collection progress as percentage
        
        Returns:
            Progress percentage (0.0 to 100.0)
        """
        if self.target_bits == 0:
            return 100.0
        
        current_bits = self.get_entropy_bits()
        return min(100.0, (current_bits / self.target_bits) * 100.0)
    
    def is_sufficient(self) -> bool:
        """
        Check if sufficient entropy has been collected
        
        Returns:
            True if sufficient entropy collected
        """
        return self.get_entropy_bits() >= self.target_bits
    
    def get_requirements_status(self) -> dict:
        """
        Get detailed status of requirements (simplified version for compatibility)
        
        Returns:
            Dictionary with requirement status
        """
        return {
            'entropy_bits': {
                'current': self.get_entropy_bits(),
                'required': self.target_bits,
                'satisfied': self.get_entropy_bits() >= self.target_bits
            }
        }
    
    def get_entropy_bytes(self) -> bytes:
        """
        Get collected entropy as bytes
        
        Returns:
            Entropy data as bytes
        """
        if len(self.entropy_data) == 0:
            return b''
        
        # Convert entropy data to bytes
        entropy_bytes = bytes(self.entropy_data)
        
        # Hash to ensure uniform distribution
        final_entropy = hashlib.sha256(entropy_bytes).digest()
        
        # Extend if needed
        while len(final_entropy) < (self.target_bits // 8):
            final_entropy += hashlib.sha256(final_entropy + entropy_bytes).digest()
        
        return final_entropy[:self.target_bits // 8]
    
    def add_progress_callback(self, callback: Callable[[], None]):
        """
        Add a callback to be called when progress changes
        
        Args:
            callback: Function to call on progress update
        """
        self.callbacks.append(callback)
    
    def remove_progress_callback(self, callback: Callable[[], None]):
        """
        Remove a progress callback
        
        Args:
            callback: Function to remove
        """
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def _notify_callbacks(self):
        """Notify all registered callbacks"""
        for callback in self.callbacks:
            try:
                callback()
            except Exception:
                pass  # Ignore callback errors
    
    def reset(self):
        """Reset entropy collection"""
        self.entropy_data.clear()
        self.is_collecting = False
        self.collection_start_time = None
        self.text_input_count = 0
        self.mouse_movement_time = 0
        self.mouse_start_time = None
        self.text_entropy_data = []
        self._add_system_entropy()
        self._notify_callbacks()
    
    def clear(self):
        """Clear entropy data (alias for reset)"""
        self.reset()
    
    def get_collection_stats(self) -> dict:
        """
        Get detailed collection statistics
        
        Returns:
            Dictionary with collection statistics
        """
        stats = {
            'is_collecting': self.is_collecting,
            'entropy_bits': self.get_entropy_bits(),
            'target_bits': self.target_bits,
            'progress_percentage': self.get_progress_percentage(),
            'is_sufficient': self.is_sufficient(),
            'data_points': len(self.entropy_data),
            'collection_time': 0,
            'text_characters': self.text_input_count,
            'mouse_time': self.mouse_movement_time,
            'requirements': self.get_requirements_status()
        }
        
        if self.collection_start_time:
            stats['collection_time'] = time.time() - self.collection_start_time
        
        return stats


class MouseEntropyWidget:
    """Helper class for GUI mouse entropy collection"""
    
    def __init__(self, entropy_collector: EntropyCollector):
        """
        Initialize mouse entropy widget
        
        Args:
            entropy_collector: EntropyCollector instance
        """
        self.entropy_collector = entropy_collector
        self.last_mouse_time = 0
        self.mouse_move_count = 0
    
    def on_mouse_move(self, event):
        """
        Handle mouse move events for entropy collection
        
        Args:
            event: Mouse move event (tkinter event)
        """
        current_time = time.time()
        
        # Throttle mouse events to avoid overwhelming the collector
        if current_time - self.last_mouse_time > 0.01:  # 10ms minimum interval
            self.entropy_collector.add_mouse_movement(event.x, event.y)
            self.last_mouse_time = current_time
            self.mouse_move_count += 1


class KeyboardEntropyWidget:
    """Helper class for GUI keyboard entropy collection"""
    
    def __init__(self, entropy_collector: EntropyCollector):
        """
        Initialize keyboard entropy widget
        
        Args:
            entropy_collector: EntropyCollector instance
        """
        self.entropy_collector = entropy_collector
        self.last_key_times = {}
    
    def on_key_press(self, event):
        """
        Handle key press events for entropy collection
        
        Args:
            event: Key press event (tkinter event)
        """
        current_time = time.time()
        key_code = event.keycode if hasattr(event, 'keycode') else hash(event.char)
        
        # Calculate time since last key press
        last_time = self.last_key_times.get(key_code, 0)
        time_diff = current_time - last_time
        
        self.entropy_collector.add_key_press(key_code, time_diff)
        self.last_key_times[key_code] = current_time
    
    def on_text_input(self, text: str):
        """
        Handle text input for entropy collection
        
        Args:
            text: Text input by user
        """
        if text and len(text.strip()) > 0:
            self.entropy_collector.add_random_text(text)

