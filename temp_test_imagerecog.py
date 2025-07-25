import pyautogui
import os
from vpn_kul import find_and_activate_ivanti_window

ASSETS_FOLDER = os.path.join(os.path.dirname(__file__), 'assets_connector')

def press_button():
    # First, try to find the middle_button across the entire screen
    middle_button = None
    
    # Search entire screen without region constraint
    for confidence in [0.9, 0.8, 0.7, 0.6]:
        try:
            middle_button = pyautogui.locateOnScreen(os.path.join(ASSETS_FOLDER, 'middle_button.png'), confidence=confidence)
            if middle_button:
                break
        except pyautogui.ImageNotFoundException:
            pass
    
    # If middle_button not found, try connect_button with multiple confidence levels
    if not middle_button:
        button_locations = []
        
        # Try different confidence levels for better detection
        # Start with highest confidence and work down
        for confidence in [0.9, 0.8, 0.7, 0.6]:
            try:
                button_locations = list(pyautogui.locateAllOnScreen(os.path.join(ASSETS_FOLDER, 'connect_button.png'), confidence=confidence))
                if button_locations:
                    print(f"Found {len(button_locations)} button(s) with confidence {confidence}")
                    break
            except pyautogui.ImageNotFoundException:
                print(f"No buttons found with confidence {confidence}")
                continue
            except Exception as e:
                print(f"Error at confidence {confidence}: {e}")
                continue
        
        if button_locations:
            # Sort by vertical position and select middle button
            button_locations.sort(key=lambda x: x.top)
            middle_index = (len(button_locations) - 1) // 2
            middle_button = button_locations[middle_index]
            print(f"Selected button at position ({middle_button.left}, {middle_button.top})")

    # If we found a button, click it
    if middle_button:
        middle_x = middle_button.left + middle_button.width // 2
        middle_y = middle_button.top + middle_button.height // 2
        print(f"Clicking button at ({middle_x}, {middle_y})")
        pyautogui.click(middle_x, middle_y)
        return  # Success, exit function
    else:
        print("No button found. Exiting.")
        return  # Failure, exit function

find_and_activate_ivanti_window()
#press_button()