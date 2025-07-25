import unittest
from unittest.mock import patch, mock_open, MagicMock, call
import json
import os
import sys

"""
Mock data and fixtures for VPN KUL tests
"""

# Sample configuration data
SAMPLE_CONFIG = {
    "button_press_method": "manual_coordinates",
    "manual_x": 100,
    "manual_y": 200,
    "speed_multiplier": 1.0,
    "close_tabs": True,
    "close_ivanti": True,
    "ivanti_path": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Pulse Secure\Ivanti Secure Access Client.lnk"
}

SAMPLE_CONFIG_IMAGE_RECOGNITION = {
    "button_press_method": "image_recognition",
    "manual_x": 0,
    "manual_y": 0,
    "speed_multiplier": 2.0,
    "close_tabs": False,
    "close_ivanti": False,
    "ivanti_path": r"C:\Custom\Path\Ivanti.lnk"
}

SAMPLE_CONFIG_BOTH_METHODS = {
    "button_press_method": "both_image_first",
    "manual_x": 150,
    "manual_y": 250,
    "speed_multiplier": 0.5,
    "close_tabs": True,
    "close_ivanti": True,
    "ivanti_path": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Pulse Secure\Ivanti Secure Access Client.lnk"
}

# Sample environment file content
SAMPLE_ENV_CONTENT = "USERNAME=r1234567\nPASSWORD=mySecurePassword123"

# Invalid configurations for testing error cases
INVALID_CONFIG_NO_COORDINATES = {
    "button_press_method": "manual_coordinates",
    "manual_x": 0,
    "manual_y": 0,
    "speed_multiplier": 1.
}

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestVpnKul(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.sample_config = {
            "button_press_method": "manual_coordinates",
            "manual_x": 100,
            "manual_y": 200,
            "speed_multiplier": 1.0,
            "close_tabs": True,
            "close_ivanti": True,
            "ivanti_path": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Pulse Secure\Ivanti Secure Access Client.lnk"
        }
        
        self.sample_env_content = "USERNAME=testuser\nPASSWORD=testpass"
    
    @patch('vpn_kul.os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_config_file_exists(self, mock_file, mock_exists):
        """Test loading configuration when config file exists."""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps(self.sample_config)
        
        # Import here to avoid issues with mocking
        with patch.dict('sys.modules', {'vpn_kul': MagicMock()}):
            from vpn_kul import load_config
            result = load_config()
            
        self.assertEqual(result, self.sample_config)
        mock_file.assert_called_once_with('vpn_config.json', 'r')
    
    @patch('vpn_kul.os.path.exists')
    def test_load_config_file_not_exists(self, mock_exists):
        """Test loading configuration when config file doesn't exist."""
        mock_exists.return_value = False
        
        with patch.dict('sys.modules', {'vpn_kul': MagicMock()}):
            from vpn_kul import load_config
            result = load_config()
            
        expected_default = {
            "button_press_method": "manual_coordinates",
            "manual_x": 0,
            "manual_y": 0,
            "speed_multiplier": 1.0,
            "close_tabs": True,
            "close_ivanti": True,
            "ivanti_path": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Pulse Secure\Ivanti Secure Access Client.lnk"
        }
        self.assertEqual(result, expected_default)
    
    @patch('vpn_kul.os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_username_success(self, mock_file, mock_exists):
        """Test successful username loading from .env file."""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = self.sample_env_content
        
        with patch.dict('sys.modules', {'vpn_kul': MagicMock()}):
            from vpn_kul import load_username
            result = load_username()
            
        self.assertEqual(result, "testuser")
    
    @patch('vpn_kul.os.path.exists')
    def test_load_username_file_not_exists(self, mock_exists):
        """Test username loading when .env file doesn't exist."""
        mock_exists.return_value = False
        
        with patch.dict('sys.modules', {'vpn_kul': MagicMock()}):
            from vpn_kul import load_username
            result = load_username()
            
        self.assertIsNone(result)
    
    @patch('vpn_kul.time.sleep')
    def test_adjusted_sleep(self, mock_sleep):
        """Test the adjusted_sleep function with different speed multipliers."""
        with patch('vpn_kul.speed_multiplier', 2.0):
            from vpn_kul import adjusted_sleep
            adjusted_sleep(4.0)
            mock_sleep.assert_called_with(2.0)  # 4.0 / 2.0 = 2.0


class TestVpnKulIntegration(unittest.TestCase):
    """Integration tests that test the main workflow with mocked external dependencies."""
    
    @patch('vpn_kul.os.system')
    @patch('vpn_kul.pyautogui.hotkey')
    @patch('vpn_kul.pyautogui.press')
    @patch('vpn_kul.pyautogui.write')
    @patch('vpn_kul.pyautogui.click')
    @patch('vpn_kul.pyautogui.locateOnScreen')
    @patch('vpn_kul.pyautogui.size')
    @patch('vpn_kul.os.startfile')
    @patch('vpn_kul.webbrowser.open')
    @patch('vpn_kul.time.sleep')
    @patch('vpn_kul.load_config')
    @patch('vpn_kul.load_username')
    @patch('vpn_kul.ctypes.windll.user32.MessageBoxW')
    def test_main_workflow_manual_coordinates(self, mock_msgbox, mock_load_username, 
                                            mock_load_config, mock_sleep, mock_browser,
                                            mock_startfile, mock_size, mock_locate,
                                            mock_click, mock_write, mock_press,
                                            mock_hotkey, mock_system):
        """Test the main workflow using manual coordinates method."""
        # Setup mocks
        mock_load_username.return_value = "testuser"
        mock_load_config.return_value = {
            "button_press_method": "manual_coordinates",
            "manual_x": 100,
            "manual_y": 200,
            "speed_multiplier": 1.0,
            "close_tabs": True,
            "close_ivanti": True,
            "ivanti_path": "test_path.lnk"
        }
        mock_size.return_value = (1920, 1080)
        
        # Mock environment variables
        with patch.dict('os.environ', {'USERNAME': 'testuser', 'PASSWORD': 'testpass'}):
            with patch('builtins.open', mock_open(read_data="USERNAME=testuser\nPASSWORD=testpass")):
                with patch('os.path.exists', return_value=True):
                    # Import and run the main script logic
                    import vpn_kul
        
        # Verify the workflow
        mock_browser.assert_has_calls([
            call("https://vpn.kuleuven.be"),
            call('https://uafw.icts.kuleuven.be')
        ])
        mock_startfile.assert_called_once()
        mock_click.assert_called_with(100, 200)  # Manual coordinates
        mock_write.assert_has_calls([call("testuser"), call("testpass")])
        mock_press.assert_has_calls([call('tab'), call('enter'), call('enter')])
        mock_hotkey.assert_has_calls([call('ctrl', 'w'), call('ctrl', 'w')])
        mock_system.assert_called_once()
    
    @patch('vpn_kul.sys.exit')
    @patch('vpn_kul.ctypes.windll.user32.MessageBoxW')
    @patch('vpn_kul.load_username')
    def test_missing_credentials_exit(self, mock_load_username, mock_msgbox, mock_exit):
        """Test that the script exits when credentials are missing."""
        mock_load_username.return_value = None
        
        with patch('builtins.open', mock_open(read_data="")):
            with patch('os.path.exists', return_value=False):
                try:
                    import vpn_kul
                except SystemExit:
                    pass
        
        mock_msgbox.assert_called_once()
        mock_exit.assert_called_once_with(1)
    
    @patch('vpn_kul.sys.exit')
    @patch('vpn_kul.ctypes.windll.user32.MessageBoxW')
    @patch('vpn_kul.load_config')
    @patch('vpn_kul.load_username')
    def test_missing_manual_coordinates_exit(self, mock_load_username, mock_load_config, 
                                           mock_msgbox, mock_exit):
        """Test that the script exits when manual coordinates are missing."""
        mock_load_username.return_value = "testuser"
        mock_load_config.return_value = {
            "button_press_method": "manual_coordinates",
            "manual_x": 0,  # Invalid coordinate
            "manual_y": 0,  # Invalid coordinate
        }
        
        with patch.dict('os.environ', {'PASSWORD': 'testpass'}):
            with patch('builtins.open', mock_open(read_data="USERNAME=testuser\nPASSWORD=testpass")):
                with patch('os.path.exists', return_value=True):
                    try:
                        import vpn_kul
                    except SystemExit:
                        pass
        
        mock_msgbox.assert_called_once()
        mock_exit.assert_called_once_with(1)


class TestPressButton(unittest.TestCase):
    """Test the press_button function with different methods."""
    
    def setUp(self):
        self.mock_config = {
            "button_press_method": "manual_coordinates",
            "manual_x": 100,
            "manual_y": 200
        }
    
    @patch('vpn_kul.pyautogui.click')
    @patch('vpn_kul.config', {"button_press_method": "manual_coordinates", "manual_x": 100, "manual_y": 200})
    def test_press_button_manual_coordinates(self, mock_click):
        """Test press_button with manual coordinates method."""
        from vpn_kul import press_connect_button
        press_connect_button()
        mock_click.assert_called_once_with(100, 200)
    
    @patch('vpn_kul.sys.exit')
    @patch('vpn_kul.pyautogui.locateAllOnScreen')
    @patch('vpn_kul.pyautogui.locateOnScreen')
    @patch('vpn_kul.config', {"button_press_method": "image_recognition"})
    def test_press_button_image_recognition_not_found(self, mock_locate, mock_locate_all, mock_exit):
        """Test press_button with image recognition when button is not found."""
        mock_locate.return_value = None
        mock_locate_all.return_value = []
        
        from vpn_kul import press_connect_button
        press_connect_button()
        
        mock_exit.assert_called_once()
    
    @patch('vpn_kul.pyautogui.click')
    @patch('vpn_kul.pyautogui.locateOnScreen')
    @patch('vpn_kul.config', {"button_press_method": "image_recognition"})
    def test_press_button_image_recognition_found(self, mock_locate, mock_click):
        """Test press_button with image recognition when button is found."""
        # Mock a button location
        mock_button = MagicMock()
        mock_button.left = 50
        mock_button.top = 100
        mock_button.width = 100
        mock_button.height = 50
        mock_locate.return_value = mock_button
        
        from vpn_kul import press_connect_button
        press_connect_button()
        
        # Should click at the center of the button (50 + 100//2, 100 + 50//2)
        mock_click.assert_called_once_with(100, 125)


if __name__ == '__main__':
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTest(unittest.makeSuite(TestVpnKul))
    test_suite.addTest(unittest.makeSuite(TestVpnKulIntegration))
    test_suite.addTest(unittest.makeSuite(TestPressButton))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\nTests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")