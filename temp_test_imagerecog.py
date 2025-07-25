import pyautogui
import os
import ctypes
from ctypes import wintypes
import time

# Windows API constants
SW_RESTORE = 9
SW_SHOW = 5

# Windows API functions
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

ASSETS_FOLDER = os.path.join(os.path.dirname(__file__), 'assets_connector')

def find_and_activate_ivanti_window():
    """Find Ivanti window and bring it to the front"""
    def enum_windows_proc(hwnd, lParam):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buffer = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buffer, length + 1)
                window_title = buffer.value.lower()
                
                # Check for Ivanti-related window titles
                if any(keyword in window_title for keyword in ['ivanti', 'secure access client']):
                    # Restore window if minimized
                    user32.ShowWindow(hwnd, SW_RESTORE)
                    # Bring to front
                    user32.SetForegroundWindow(hwnd)
                    # Activate the window
                    user32.SetActiveWindow(hwnd)
                    return False  # Stop enumeration
        return True

    # Define the callback function type
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    
    # Enumerate all windows
    user32.EnumWindows(EnumWindowsProc(enum_windows_proc), 0)

def press_button():
    ivanti_window = None
    
    # Start with highest confidence and work down
    for confidence in [0.99, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65]:
        try:
            ivanti_window = pyautogui.locateOnScreen(os.path.join(ASSETS_FOLDER, 'full_ivanti.png'), confidence=confidence)
            if ivanti_window:
                print(f"Found ivanti window with confidence {confidence}")
                break
        except pyautogui.ImageNotFoundException:
            print(f"No ivanti window found with confidence {confidence}")
            continue
        except Exception as e:
            print(f"Error finding ivanti window at confidence {confidence}: {e}")
            continue

    # If we found a button, click it
    if ivanti_window:
        rel_x, rel_y = 0.826, 0.398
        connect_button_x = ivanti_window.left + int(ivanti_window.width * rel_x)
        connect_button_y = ivanti_window.top + int(ivanti_window.height * rel_y)
        print(f"Clicking ivanti window at ({connect_button_x}, {connect_button_y})")
        pyautogui.click(connect_button_x, connect_button_y)
        return  # Success, exit function
    else:
        print("No button found. Exiting.")
        return  # Failure, exit function

find_and_activate_ivanti_window()
time.sleep(0.5)  # Give it a moment to come to front
press_button()