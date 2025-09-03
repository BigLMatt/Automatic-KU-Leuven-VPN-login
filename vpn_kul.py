import sys
import webbrowser
import os
import _thread
from pynput import keyboard as kb
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
        "img_rel_x": 0.826,
        "img_rel_y": 0.414,
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
        for image in ["full_ivanti1.png","full_ivanti2.png","A_zone.png","I_zone.png"]:
            for confidence in [0.99, 0.85, 0.7, 0.55]:
                try:
                    ivanti_window = pyautogui.locateOnScreen(os.path.join(ASSETS_FOLDER, image), confidence=confidence)
                    if ivanti_window:
                        break
                except pyautogui.ImageNotFoundException:
                    continue
                except Exception:
                    pass

            # If we found a button, click it
            if ivanti_window:
                rel_x = config.get("img_rel_x")
                rel_y = config.get("img_rel_y")
                connect_button_x = ivanti_window.left + int(ivanti_window.width * rel_x)
                connect_button_y = ivanti_window.top + int(ivanti_window.height * rel_y)
                pyautogui.click(connect_button_x, connect_button_y)
                return
            
        if method == "both_image_first":
            pyautogui.click(config["manual_x"], config["manual_y"])
            return
        else:
            ctypes.windll.user32.MessageBoxW(0,"Failed to find the connect button.\nMake sure the whole window is visible and B-zone is selected." , "VPN Login Error", 0x10)
            sys.exit(1)
                
    elif method == "manual_coordinates":
        pyautogui.click(config["manual_x"], config["manual_y"])

def check_if_logged_in():
    '''Check if when the vpn page is loaded, the user is logged in.'''
    login = None
    for login_image in ["login_page_top1.png","login_page_middle1.png","login_page_middle2.png","login_page_bottom2.png"]:
        try:
            login = pyautogui.locateOnScreen(os.path.join(ASSETS_FOLDER, login_image), confidence=0.8)
        except Exception:
            continue
        if login:
            ctypes.windll.user32.MessageBoxW(0, "Please log into toledo or KUL services and try again.", "VPN Login Error", 0x10)
            sys.exit(1)

def start_esc_interrupt():
    def on_press(key):
        if key == kb.Key.esc:
            _thread.interrupt_main()
    listener = kb.Listener(on_press=on_press)
    listener.daemon = True
    listener.start()


if __name__ == "__main__":

    start_esc_interrupt()
    try:
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
        adjusted_sleep(1)
        check_if_logged_in()
        os.startfile(ivanti_path)
        time.sleep(1)
        find_and_activate_ivanti_window()
        adjusted_sleep(0.5)
        
        original_pos = pyautogui.position()
        pyautogui.moveTo(0, 1)   # Move out of the way, to not interfere with image recognition
        press_connect_button()
        pyautogui.moveTo(original_pos)
        adjusted_sleep(2)
        

        # Fill in credentials
        pyautogui.write(USERNAME)
        pyautogui.press('tab')
        pyautogui.write(PASSWORD)
        pyautogui.press('enter')
        adjusted_sleep(1.5)
        pyautogui.press('enter')  # Confirm login
        adjusted_sleep(6)

        # Open extra site
        webbrowser.open('https://uafw.icts.kuleuven.be')
        adjusted_sleep(3)

        # Close tabs and Ivanti if requested
        if config.get("close_tabs", True):
            pyautogui.hotkey('ctrl', 'w')
            pyautogui.hotkey('ctrl', 'w')

        if config.get("close_ivanti", True):
            os.system('powershell -command "(Get-Process | Where-Object {$_.MainWindowTitle -like \'*Ivanti*\'}) | ForEach-Object { $_.CloseMainWindow() }"')
    except(KeyboardInterrupt):
            try:
                ctypes.windll.user32.MessageBoxW(0, "Execution stopped by user (ESC).", "VPN KUL Connector", 0x30)
            except Exception:
                pass
            sys.exit(1)