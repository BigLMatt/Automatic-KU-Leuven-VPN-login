import sys
import webbrowser
import os
import time
import pyautogui
import keyring
import json
import ctypes
from ctypes import wintypes

def resource_path(relative_path):
    """ Get correct path, works both in development and PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_username():
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r") as f:
            for line in f:
                if line.startswith("USERNAME="):
                    return line.strip().split("=", 1)[1]
    return None

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        "button_press_method": "image_recognition",
        "manual_x": 0,
        "manual_y": 0,
        "speed_multiplier": 1.0,
        "close_tabs": True,
        "close_ivanti": True,
        "ivanti_path": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Pulse Secure\Ivanti Secure Access Client.lnk"
    }

def adjusted_sleep(duration):
    time.sleep(duration / speed_multiplier)

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

def press_connect_button():
    method = config["button_press_method"]

    if method in ("image_recognition", "both_image_first"):
        ivanti_window = None
    
        # Start with highest confidence and work down
        for confidence in [0.99, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65]:
            try:
                ivanti_window = pyautogui.locateOnScreen(os.path.join(ASSETS_FOLDER, 'full_ivanti.png'), confidence=confidence)
                if ivanti_window:
                    break
            except Exception:
                continue

        # If we found a button, click it
        if ivanti_window:
            rel_x, rel_y = 0.826, 0.398     # Relative coordinates for the connect button in the full Ivanti window
            connect_button_x = ivanti_window.left + int(ivanti_window.width * rel_x)
            connect_button_y = ivanti_window.top + int(ivanti_window.height * rel_y)
            pyautogui.click(connect_button_x, connect_button_y)
            return
            
        # If no button found, use manual coordinates
        if method == "both_image_first":
            pyautogui.click(config["manual_x"], config["manual_y"])
            return
        else:
            ctypes.windll.user32.MessageBoxW(0,"Failed to find the connect button.\nMake sure the whole window is visible and B-zone is selected." , "VPN Login Error", 0x10)
            sys.exit(1)
                
    elif method == "manual_coordinates":
        pyautogui.click(config["manual_x"], config["manual_y"])


if __name__ == "__main__":

    SERVICE_NAME = "kuleuvenvpn"
    ENV_FILE = ".env"
    CONFIG_FILE = "vpn_config.json"
    ASSETS_FOLDER = resource_path("assets_connector")

    config = load_config()

    # Windows API constants
    SW_RESTORE = 9
    SW_SHOW = 5

    # Windows API functions
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    USERNAME = load_username()
    ivanti_path = config.get("ivanti_path", r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Pulse Secure\Ivanti Secure Access Client.lnk")
    speed_multiplier = config.get("speed_multiplier", 1.0)

    # Check if nessecary information is available
    if USERNAME:
        PASSWORD = keyring.get_password(SERVICE_NAME, USERNAME)
    else:
        PASSWORD = None

    if not USERNAME or not PASSWORD:
        ctypes.windll.user32.MessageBoxW(0, "Missing VPN credentials.\nPlease run the setup tool to configure them.", "VPN Login Error", 0x10)
        sys.exit(1)

    # Check for valid manual coordinates when required
    if config["button_press_method"] in ["manual_coordinates", "both_image_first"]:
        if not config["manual_x"] or not config["manual_y"]:
            ctypes.windll.user32.MessageBoxW(0, "Missing or invalid manual click coordinates.\nPlease run the setup tool to configure the click coordinates.", "VPN Login Error", 0x10)
            sys.exit(1)

    # Start up actual login process
    # Open KU Leuven VPN page and Ivanti
    webbrowser.open("https://vpn.kuleuven.be")
    adjusted_sleep(0.3)
    os.startfile(ivanti_path)
    find_and_activate_ivanti_window()
    adjusted_sleep(0.4)
    
    original_pos = pyautogui.position()
    pyautogui.moveTo(0, 1)   # Move out of the way, to not interfere with image recognition
    press_connect_button()
    pyautogui.moveTo(original_pos)
    adjusted_sleep(0.8)
    

    # Fill in credentials
    pyautogui.write(USERNAME)
    pyautogui.press('tab')
    pyautogui.write(PASSWORD)
    pyautogui.press('enter')
    adjusted_sleep(0.8)
    pyautogui.press('enter')  # Confirm login
    adjusted_sleep(5.2)

    # Open extra site
    webbrowser.open('https://uafw.icts.kuleuven.be')
    adjusted_sleep(1.5)

    # Close tabs and Ivanti if requested
    if config.get("close_tabs", True):
        pyautogui.hotkey('ctrl', 'w')
        pyautogui.hotkey('ctrl', 'w')

    if config.get("close_ivanti", True):
        os.system('powershell -command "(Get-Process | Where-Object {$_.MainWindowTitle -like \'*Ivanti*\'}) | ForEach-Object { $_.CloseMainWindow() }"')