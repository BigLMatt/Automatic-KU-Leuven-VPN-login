import webbrowser
import os
import time
import pyautogui
from dotenv import load_dotenv
import ctypes

load_dotenv()
USERNAME = os.getenv("KUL_USERNAME")
PASSWORD = os.getenv("KUL_PASSWORD")

if not USERNAME or not PASSWORD:
    ctypes.windll.user32.MessageBoxW(0, ".env file is not filled in!\n\nFill KUL_USERNAME and KUL_PASSWORD in.", "Error", 0x10)
    exit(1)

# Define ivanti path etc
ivanti_path = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Pulse Secure\Ivanti Secure Access Client.lnk"
ivanti_process = os.path.basename(ivanti_path)

# Open everything
webbrowser.open("https://vpn.kuleuven.be")
time.sleep(0.2)
response = os.startfile(ivanti_path)
print(response)

# After waiting for Ivanti to open
time.sleep(0.7)

# Get screen size
screen_width, screen_height = pyautogui.size()
'''
# Define the region where the buttons should be (adjust these values as needed)
region = (
    int(screen_width * 0.7),
    int(screen_height * 0.3),
    int(screen_width * 0.3),
    int(screen_height * 0.4)
)

# Try to find buttons in this region
connect_buttons = list(pyautogui.locateAllOnScreen('connect_button.png', confidence=0.5, region=region))

if connect_buttons:
    print(f"Found {len(connect_buttons)} buttons. Positions: {connect_buttons}")
    # Sort buttons by y-coordinate (top to bottom)
    connect_buttons.sort(key=lambda x: x[1])
    
    # Select the middle button (B-Zone)
    target = connect_buttons[1] if len(connect_buttons) >= 2 else connect_buttons[0]
    pyautogui.click(target)
    print(f"Clicked button at position {target}")
else:
    print("Could not find any connect buttons. Taking screenshot for debugging.")
    pyautogui.screenshot("debug_screenshot.png")
    exit()
'''
# Manually find position of connect button
pyautogui.click(1429, 698)  # Replace with your actual position

# Wait for username and password fields to appear
time.sleep(0.7)

# Fill in credentials
pyautogui.write(USERNAME)  # Replace with your actual username
pyautogui.press('tab')
pyautogui.write(PASSWORD)  # Replace with your actual password
pyautogui.press('enter')

time.sleep(0.7)  # Wait for credential chekck to complete

# Manually find position of proceed button
pyautogui.click(1673, 1170)  # Replace with your actual position

# Wait for VPN connection to establish
time.sleep(6)

webbrowser.open('https://uafw.icts.kuleuven.be')

# Kill every process including VScode
time.sleep(0.5)
# Works only in chrome
os.system('powershell -command "(Get-Process | Where-Object {$_.MainWindowTitle -like \'*Ivanti*\'}) | ForEach-Object { $_.CloseMainWindow() }"')
# Works only when using VS code
#os.system("taskkill /IM Code.exe /F")