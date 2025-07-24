import sys
import webbrowser
import os
import time
import pyautogui
import keyring
import json
import ctypes
from ctypes import wintypes

# Windows API constants
SW_RESTORE = 9
SW_SHOW = 5

# Windows API functions
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

def resource_path(relative_path):
    """ Get correct path, works both in development and PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

SERVICE_NAME = "kuleuvenvpn"
ENV_FILE = ".env"
CONFIG_FILE = "vpn_config.json"
ASSETS_FOLDER = resource_path("assets_connector")

def load_username():
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r") as f:
            for line in f:
                if line.startswith("USERNAME="):
                    return line.strip().split("=", 1)[1]
    return None

USERNAME = load_username()
if USERNAME:
    PASSWORD = keyring.get_password(SERVICE_NAME, USERNAME)
else:
    PASSWORD = None

if not USERNAME or not PASSWORD:
    ctypes.windll.user32.MessageBoxW(0, "Missing VPN credentials.\nPlease run the setup tool to configure them.", "VPN Login Error", 0x10)
    sys.exit(1)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        "button_press_method": "manual_coordinates",
        "manual_x": 0,
        "manual_y": 0,
        "speed_multiplier": 1.0,
        "close_tabs": True,
        "close_ivanti": True,
        "ivanti_path": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Pulse Secure\Ivanti Secure Access Client.lnk"
    }

config = load_config()

# Check for valid manual coordinates when required
if config["button_press_method"] in ["manual_coordinates", "both_image_first"]:
    if not config["manual_x"] or not config["manual_y"]:
        ctypes.windll.user32.MessageBoxW(0, "Missing or invalid manual click coordinates.\nPlease run the setup tool to configure the click coordinates.", "VPN Login Error", 0x10)
        sys.exit(1)

ivanti_path = config.get("ivanti_path", r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Pulse Secure\Ivanti Secure Access Client.lnk")
speed_multiplier = config.get("speed_multiplier", 1.0)

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

# Open KU Leuven VPN page and Ivanti
webbrowser.open("https://vpn.kuleuven.be")
adjusted_sleep(0.4)
os.startfile(ivanti_path)
adjusted_sleep(0.4)

# Find and activate Ivanti window
find_and_activate_ivanti_window()
adjusted_sleep(0.4)  # Give it a moment to come to front

# Define region to look for button
screen_width, screen_height = pyautogui.size()
region = (
    int(screen_width * 0.52),
    int(screen_height * 0.376),
    int(screen_width * 0.058),
    int(screen_height * 0.113)
)

def press_button():
    method = config["button_press_method"]

    if method in ("image_recognition", "both_image_first"):
        try:
            middle_button = pyautogui.locateOnScreen(os.path.join(ASSETS_FOLDER, 'middle_button.png'), confidence=0.7, region=region)

            if not middle_button:
                button_locations = list(pyautogui.locateAllOnScreen(os.path.join(ASSETS_FOLDER, 'connect_button.png'), confidence=0.6, region=region))
                if button_locations:
                    button_locations.sort(key=lambda x: x.top)
                    middle_index = (len(button_locations) - 1) // 2
                    middle_button = button_locations[middle_index]

            if middle_button:
                middle_x = middle_button.left + middle_button.width // 2
                middle_y = middle_button.top + middle_button.height // 2
                pyautogui.click(middle_x, middle_y)
            elif method == "both_image_first":
                pyautogui.click(config["manual_x"], config["manual_y"])
            else:
                # pyautogui.screenshot("debug_screenshot.png")  # Debug screenshot
                sys.exit()
        except Exception:
            # pyautogui.screenshot("error_screenshot.png")  # Error screenshot
            sys.exit()
    elif method == "manual_coordinates":
        pyautogui.click(config["manual_x"], config["manual_y"])

press_button()
adjusted_sleep(0.8)

# Fill in credentials
pyautogui.write(USERNAME)
pyautogui.press('tab')
pyautogui.write(PASSWORD)
pyautogui.press('enter')

adjusted_sleep(0.8)
pyautogui.press('enter')  # Confirm login
adjusted_sleep(6)

# Open extra site
webbrowser.open('https://uafw.icts.kuleuven.be')
adjusted_sleep(1.5)

if config.get("close_tabs", True):
    pyautogui.hotkey('ctrl', 'w')
    pyautogui.hotkey('ctrl', 'w')

if config.get("close_ivanti", True):
    os.system('powershell -command "(Get-Process | Where-Object {$_.MainWindowTitle -like \'*Ivanti*\'}) | ForEach-Object { $_.CloseMainWindow() }"')