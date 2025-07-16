import webbrowser
import os
import time
import pyautogui
import keyring
import ctypes
import traceback
import logging
import json

# Set up logging
logging.basicConfig(filename='vpn_kul.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

SERVICE_NAME = "kuleuvenvpn"
ENV_FILE = ".env"
CONFIG_FILE = "vpn_config.json"
ASSETS_FOLDER = "assets"

# Load USERNAME from .env file
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

# Define ivanti path etc
ivanti_path = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Pulse Secure\Ivanti Secure Access Client.lnk"
ivanti_process = os.path.basename(ivanti_path)

# Open everything
webbrowser.open("https://vpn.kuleuven.be")
time.sleep(0.3)
response = os.startfile(ivanti_path)
print(response)

# After waiting for Ivanti to open
time.sleep(1.2)

# Get screen size
screen_width, screen_height = pyautogui.size()

# Define the region where the buttons should be (adjust these values as needed)
region = (
    int(screen_width * 0.51),
    int(screen_height * 0.37),
    int(screen_width * 0.06),
    int(screen_height * 0.12)
)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        "button_press_method": "image_recognition",
        "manual_x": 0,
        "manual_y": 0
    }

config = load_config()

def press_button():
    method = config["button_press_method"]
    
    if method == "image_recognition" or method == "both_image_first":
        try:
            logging.info(f"Attempting to locate button images in region: {region}")
            
            # First, try to find the middle button specifically
            middle_button = pyautogui.locateOnScreen(os.path.join(ASSETS_FOLDER, 'middle_button.png'), confidence=0.5, region=region)
            
            if middle_button:
                logging.info("Found middle button directly")
                middle_x = middle_button.left + middle_button.width // 2
                middle_y = middle_button.top + middle_button.height // 2
            else:
                # If middle button not found, log the maximum confidence found
                max_confidence = 0
                for confidence in range(0, 101):  # Check from 0 to 1.00
                    if pyautogui.locateOnScreen(os.path.join(ASSETS_FOLDER, 'middle_button.png'), confidence=confidence/100, region=region):
                        max_confidence = confidence/100
                    else:
                        break
                logging.info(f"Middle button not found. Max confidence: {max_confidence:.2f}")

                # Fall back to finding all buttons
                button_locations = list(pyautogui.locateAllOnScreen(os.path.join(ASSETS_FOLDER, 'connect_button.png'), confidence=0.5, region=region))
                
                if button_locations:
                    logging.info(f"Found {len(button_locations)} general button images")
                    
                    # Sort buttons by vertical position (top to bottom)
                    button_locations.sort(key=lambda x: x.top)
                    
                    # Select the middle button
                    middle_index = (len(button_locations) - 1) // 2
                    middle_button = button_locations[middle_index]
                    middle_x = middle_button.left + middle_button.width // 2
                    middle_y = middle_button.top + middle_button.height // 2
                    logging.info(f"Selected middle button at index {middle_index}")
                else:
                    middle_button = None

            if middle_button:
                logging.info(f"Attempting to click the middle button at: ({middle_x}, {middle_y})")
                pyautogui.click(middle_x, middle_y)
                logging.info(f"Clicked the middle button")
            elif method == "both_image_first":
                logging.info("Image recognition failed, falling back to manual coordinates")
                pyautogui.click(config["manual_x"], config["manual_y"])
                logging.info(f"Clicked at manual position ({config['manual_x']}, {config['manual_y']})")
            else:
                logging.warning("Could not find any button images. Taking screenshot for debugging.")
                debug_screenshot = pyautogui.screenshot("debug_screenshot.png")
                logging.info(f"Debug screenshot saved as debug_screenshot.png")
                print("Could not find any button images. Please check the debug screenshot and update the script accordingly.")
                exit()
        except Exception as e:
            logging.error(f"An error occurred while trying to find or click the button: {str(e)}")
            logging.error(traceback.format_exc())
            print(f"An error occurred: {str(e)}. Check the log file for more details.")
            debug_screenshot = pyautogui.screenshot("error_screenshot.png")
            logging.info(f"Error screenshot saved as error_screenshot.png")
            exit()
    elif method == "manual_coordinates":
        logging.info(f"Using manual coordinates: ({config['manual_x']}, {config['manual_y']})")
        pyautogui.click(config["manual_x"], config["manual_y"])
        logging.info(f"Clicked at manual position ({config['manual_x']}, {config['manual_y']})")

# Use the press_button function where you need to click the button
press_button()

# Add a small delay after clicking to ensure the click is registered
time.sleep(1)

# Fill in credentials
pyautogui.write(USERNAME)  # Replace with your actual username
pyautogui.press('tab')
pyautogui.write(PASSWORD)  # Replace with your actual password
pyautogui.press('enter')

time.sleep(1)  # Wait for credential check to complete

pyautogui.press('enter')  # Press proceed button

# Wait for VPN connection to establish
time.sleep(6)

webbrowser.open('https://uafw.icts.kuleuven.be')

# Kill every process including VScode
time.sleep(0.5)
# Works only in chrome
os.system('powershell -command "(Get-Process | Where-Object {$_.MainWindowTitle -like \'*Ivanti*\'}) | ForEach-Object { $_.CloseMainWindow() }"')
# Works only when using VS code
#os.system("taskkill /IM Code.exe /F")