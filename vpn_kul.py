import webbrowser
import os
import time
import pyautogui
import keyring
import ctypes

SERVICE_NAME = "kuleuvenvpn"

# Load USERNAME from .env file
ENV_FILE = ".env"
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
time.sleep(1.7)

# Get screen size
screen_width, screen_height = pyautogui.size()

# Define the region where the buttons should be (adjust these values as needed)
region = (
    int(screen_width * 0.65),
    int(screen_height * 0.47),
    int(screen_width * 0.5),
    int(screen_height * 0.76)
)

# Try to find the button image in this region
button_location = pyautogui.locateOnScreen('connect_button.png', confidence=0.51, region=region)

if button_location:
    print(f"Found button image at position: {button_location}")
    
    # Calculate the center of the middle button
    middle_x = button_location.left + button_location.width // 2
    middle_y = button_location.top + button_location.height // 2
    
    print(f"Attempting to click the middle of the button image at: ({middle_x}, {middle_y})")
    pyautogui.click(middle_x, middle_y)
    print(f"Clicked the middle of the button image")
else:
    print("Could not find the button image. Taking screenshot for debugging.")
    debug_screenshot = pyautogui.screenshot("debug_screenshot.png")
    print(f"Debug screenshot saved as debug_screenshot.png")
    
    user_input = input("Do you want to continue with manual coordinates? (y/n): ")
    if user_input.lower() != 'y':
        print("Exiting program.")
        exit()
    else:
        x = int(input("Enter x coordinate: "))
        y = int(input("Enter y coordinate: "))
        pyautogui.click(x, y)
        print(f"Clicked at manual position ({x}, {y})")

# Add a small delay after clicking to ensure the click is registered
time.sleep(1)

# Wait for username and password fields to appear
time.sleep(0.7)

# Fill in credentials
pyautogui.write(USERNAME)  # Replace with your actual username
pyautogui.press('tab')
pyautogui.write(PASSWORD)  # Replace with your actual password
pyautogui.press('enter')

time.sleep(0.7)  # Wait for credential check to complete

# Manually find position of proceed button
#pyautogui.click(1673, 1170)  # Replace with your actual position

# Wait for VPN connection to establish
time.sleep(6)

webbrowser.open('https://uafw.icts.kuleuven.be')

# Kill every process including VScode
time.sleep(0.5)
# Works only in chrome
os.system('powershell -command "(Get-Process | Where-Object {$_.MainWindowTitle -like '*Ivanti*'}) | ForEach-Object { $_.CloseMainWindow() }"')
# Works only when using VS code
#os.system("taskkill /IM Code.exe /F")