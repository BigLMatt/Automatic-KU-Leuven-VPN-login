import webbrowser
import os
import time
import pyautogui
import keyring
import json

SERVICE_NAME = "kuleuvenvpn"
ENV_FILE = ".env"
CONFIG_FILE = "vpn_config.json"
ASSETS_FOLDER = "assets"

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
    import ctypes
    ctypes.windll.user32.MessageBoxW(0, "Missing VPN credentials.\nPlease run the setup tool to configure them.", "VPN Login Error", 0x10)
    exit(1)

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

config = load_config()
ivanti_path = config.get("ivanti_path", r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Pulse Secure\Ivanti Secure Access Client.lnk")

# Open KU Leuven VPN page and Ivanti
webbrowser.open("https://vpn.kuleuven.be")
time.sleep(0.3)
os.startfile(ivanti_path)
time.sleep(1.2)

# Define region to look for button
screen_width, screen_height = pyautogui.size()
region = (
    int(screen_width * 0.51),
    int(screen_height * 0.37),
    int(screen_width * 0.06),
    int(screen_height * 0.12)
)

def press_button():
    method = config["button_press_method"]

    if method in ("image_recognition", "both_image_first"):
        try:
            middle_button = pyautogui.locateOnScreen(os.path.join(ASSETS_FOLDER, 'middle_button.png'), confidence=0.5, region=region)

            if not middle_button:
                button_locations = list(pyautogui.locateAllOnScreen(os.path.join(ASSETS_FOLDER, 'connect_button.png'), confidence=0.5, region=region))
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
                exit()
        except Exception:
            # pyautogui.screenshot("error_screenshot.png")  # Error screenshot
            exit()
    elif method == "manual_coordinates":
        pyautogui.click(config["manual_x"], config["manual_y"])

press_button()
time.sleep(1)

# Fill in credentials
pyautogui.write(USERNAME)
pyautogui.press('tab')
pyautogui.write(PASSWORD)
pyautogui.press('enter')

time.sleep(1)
pyautogui.press('enter')  # Confirm login
time.sleep(6)

# Open extra site
webbrowser.open('https://uafw.icts.kuleuven.be')
time.sleep(1)

if config.get("close_tabs", True):
    pyautogui.hotkey('ctrl', 'w')
    pyautogui.hotkey('ctrl', 'w')

if config.get("close_ivanti", True):
    os.system('powershell -command "(Get-Process | Where-Object {$_.MainWindowTitle -like \'*Ivanti*\'}) | ForEach-Object { $_.CloseMainWindow() }"')
