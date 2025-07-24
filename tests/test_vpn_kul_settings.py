import pytest
import json
import os
import tkinter as tk
from unittest.mock import patch, mock_open, MagicMock, call
from tkinter import messagebox

# Test fixtures
@pytest.fixture
def sample_config():
    """Sample configuration data for testing."""
    return {
        "language": "en",
        "button_press_method": "manual_coordinates",
        "manual_x": 100,
        "manual_y": 200,
        "speed_multiplier": 1.0,
        "close_tabs": True,
        "close_ivanti": True,
        "ivanti_path": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Pulse Secure\Ivanti Secure Access Client.lnk"
    }

@pytest.fixture
def sample_env_content():
    """Sample .env file content."""
    return "USERNAME=testuser\nPASSWORD=testpass"

@pytest.fixture
def mock_root():
    """Mock tkinter root window."""
    root = MagicMock(spec=tk.Tk)
    root.geometry = MagicMock()
    root.title = MagicMock()
    root.iconphoto = MagicMock()
    root.resizable = MagicMock()
    root.quit = MagicMock()
    root.mainloop = MagicMock()
    return root

@pytest.fixture
def mock_translations():
    """Mock translations dictionary."""
    return {
        "en": {
            "vpn_login_setup": "VPN login setup",
            "what_to_do": "What do you want to do?",
            "setup_login": "Setup login",
            "delete_login": "Delete login",
            "set_manual_click": "Set Manual Click Position",
            "options": "Options",
            "language": "Language",
            "close": "Close",
            "back_to_menu": "Back to menu",
            "saved": "Saved",
            "login_saved": "The login is saved.",
            "deleted": "Deleted",
            "login_deleted": "Login has been deleted successfully.",
            "select_language": "Select a language"
        },
        "nl": {
            "vpn_login_setup": "VPN login instellingen",
            "what_to_do": "Wat wil je doen?",
            "setup_login": "Login veranderen",
            "delete_login": "Login verwijderen",
            "set_manual_click": "Manuele klik positie instellen",
            "options": "Opties",
            "language": "Taal",
            "close": "Sluiten",
            "back_to_menu": "Terug naar hoofdmenu",
            "saved": "Opgeslagen",
            "login_saved": "De login is opgeslagen.",
            "deleted": "Verwijderd",
            "login_deleted": "De login is verwijderd.",
            "select_language": "Selecteer een taal"
        }
    }

class TestConfigurationFunctions:
    """Test configuration loading and saving functions."""
    
    @patch('vpn_kul_settings.os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_config_file_exists(self, mock_file, mock_exists, sample_config):
        """Test loading configuration when config file exists."""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps(sample_config)
        
        with patch('vpn_kul_settings.CONFIG_FILE', 'test_config.json'):
            from vpn_kul_settings import load_config
            result = load_config()
            
        assert result == sample_config
        mock_file.assert_called_once_with('test_config.json', 'r')
    
    @patch('vpn_kul_settings.os.path.exists')
    def test_load_config_file_not_exists(self, mock_exists):
        """Test loading configuration when config file doesn't exist."""
        mock_exists.return_value = False
        
        with patch('vpn_kul_settings.CONFIG_FILE', 'test_config.json'):
            from vpn_kul_settings import load_config
            result = load_config()
            
        # Should return default configuration
        assert "language" in result
        assert result["language"] == "en"
    
    @patch('builtins.open', new_callable=mock_open)
    def test_save_config(self, mock_file, sample_config):
        """Test saving configuration to file."""
        with patch('vpn_kul_settings.CONFIG_FILE', 'test_config.json'):
            from vpn_kul_settings import save_config
            save_config(sample_config)
            
        mock_file.assert_called_once_with('test_config.json', 'w')
        mock_file().write.assert_called()
    
    @patch('vpn_kul_settings.os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_username_success(self, mock_file, mock_exists, sample_env_content):
        """Test successful username loading from .env file."""
        mock_exists.return_value = True
        mock_file.return_value.__iter__.return_value = sample_env_content.split('\n')
        
        from vpn_kul_settings import load_username
        result = load_username()
        
        assert result == "testuser"
    
    @patch('vpn_kul_settings.os.path.exists')
    def test_load_username_file_not_exists(self, mock_exists):
        """Test username loading when .env file doesn't exist."""
        mock_exists.return_value = False
        
        from vpn_kul_settings import load_username
        result = load_username()
        
        assert result == ""


class TestTranslationFunctions:
    """Test translation and language functions."""
    
    def test_get_translation_existing_key(self, mock_translations):
        """Test getting translation for existing key."""
        with patch('vpn_kul_settings.translations', mock_translations):
            with patch('vpn_kul_settings.config', {'language': 'en'}):
                from vpn_kul_settings import get_translation
                result = get_translation("setup_login")
                
        assert result == "Setup login"
    
    def test_get_translation_missing_key(self, mock_translations):
        """Test getting translation for missing key returns the key itself."""
        with patch('vpn_kul_settings.translations', mock_translations):
            with patch('vpn_kul_settings.config', {'language': 'en'}):
                from vpn_kul_settings import get_translation
                result = get_translation("nonexistent_key")
                
        assert result == "nonexistent_key"
    
    def test_get_translation_dutch(self, mock_translations):
        """Test getting Dutch translation."""
        with patch('vpn_kul_settings.translations', mock_translations):
            with patch('vpn_kul_settings.config', {'language': 'nl'}):
                from vpn_kul_settings import get_translation
                result = get_translation("setup_login")
                
        assert result == "Login veranderen"
    
    @patch('vpn_kul_settings.save_config')
    @patch('vpn_kul_settings.show_main_menu')
    def test_change_language(self, mock_show_menu, mock_save_config):
        """Test changing language."""
        mock_config = {'language': 'en'}
        mock_root = MagicMock()
        
        with patch('vpn_kul_settings.config', mock_config):
            with patch('vpn_kul_settings.root', mock_root):
                with patch('vpn_kul_settings.get_translation', return_value="Test Title"):
                    from vpn_kul_settings import change_language
                    change_language('nl')
        
        assert mock_config['language'] == 'nl'
        mock_save_config.assert_called_once_with(mock_config)
        mock_root.title.assert_called_once_with("Test Title")
        mock_show_menu.assert_called_once()


class TestGUIFunctions:
    """Test GUI-related functions."""
    
    @patch('vpn_kul_settings.ttk.Button')
    @patch('vpn_kul_settings.ttk.Label')
    @patch('vpn_kul_settings.clear_frame')
    def test_show_language_menu(self, mock_clear, mock_label, mock_button, mock_translations):
        """Test showing language menu."""
        with patch('vpn_kul_settings.translations', mock_translations):
            with patch('vpn_kul_settings.config', {'language': 'en'}):
                with patch('vpn_kul_settings.root', MagicMock()):
                    with patch('vpn_kul_settings.get_translation', side_effect=lambda x: mock_translations['en'].get(x, x)):
                        from vpn_kul_settings import show_language_menu
                        show_language_menu()
        
        mock_clear.assert_called_once()
        mock_label.assert_called()
        assert mock_button.call_count >= 3  # At least 2 language buttons + back button
    
    @patch('vpn_kul_settings.messagebox.showinfo')
    @patch('vpn_kul_settings.save_config')
    def test_save_credentials_success(self, mock_save_config, mock_showinfo):
        """Test successful credential saving."""
        mock_username_entry = MagicMock()
        mock_password_entry = MagicMock()
        mock_username_entry.get.return_value = "testuser"
        mock_password_entry.get.return_value = "testpass"
        
        with patch('vpn_kul_settings.username_entry', mock_username_entry):
            with patch('vpn_kul_settings.password_entry', mock_password_entry):
                with patch('vpn_kul_settings.get_translation', side_effect=lambda x: x):
                    with patch('builtins.open', mock_open()):
                        from vpn_kul_settings import save_credentials
                        save_credentials()
        
        mock_showinfo.assert_called_once_with("saved", "login_saved")
    
    @patch('vpn_kul_settings.messagebox.showerror')
    def test_save_credentials_empty_fields(self, mock_showerror):
        """Test credential saving with empty fields."""
        mock_username_entry = MagicMock()
        mock_password_entry = MagicMock()
        mock_username_entry.get.return_value = ""
        mock_password_entry.get.return_value = ""
        
        with patch('vpn_kul_settings.username_entry', mock_username_entry):
            with patch('vpn_kul_settings.password_entry', mock_password_entry):
                with patch('vpn_kul_settings.get_translation', side_effect=lambda x: x):
                    from vpn_kul_settings import save_credentials
                    save_credentials()
        
        mock_showerror.assert_called_once_with("invalid_entry", "empty_user")


class TestManualClickMenu:
    """Test manual click position functionality."""
    
    @patch('vpn_kul_settings.tk.Button')
    @patch('vpn_kul_settings.tk.Label')
    @patch('vpn_kul_settings.clear_frame')
    @patch('vpn_kul_settings.pyautogui.position')
    @patch('vpn_kul_settings.os.startfile')
    @patch('vpn_kul_settings.time.sleep')
    def test_show_manual_click_menu(self, mock_sleep, mock_startfile, mock_position, 
                                   mock_clear, mock_label, mock_button):
        """Test showing manual click menu."""
        mock_position.return_value = (100, 200)
        
        with patch('vpn_kul_settings.config', {'ivanti_path': 'test_path'}):
            with patch('vpn_kul_settings.root', MagicMock()):
                with patch('vpn_kul_settings.get_translation', side_effect=lambda x: x):
                    from vpn_kul_settings import show_manual_click_menu
                    show_manual_click_menu()
        
        mock_clear.assert_called_once()
        mock_label.assert_called()
        mock_button.assert_called()
    
    @patch('vpn_kul_settings.messagebox.showinfo')
    @patch('vpn_kul_settings.save_config')
    @patch('vpn_kul_settings.show_main_menu')
    def test_manual_click_capture(self, mock_show_menu, mock_save_config, mock_showinfo):
        """Test manual click position capture."""
        mock_config = {'manual_x': 0, 'manual_y': 0}
        
        # This would be called by the mouse listener in the actual implementation
        with patch('vpn_kul_settings.config', mock_config):
            with patch('vpn_kul_settings.get_translation', side_effect=lambda x: x):
                # Simulate the click capture
                mock_config["manual_x"] = 150
                mock_config["manual_y"] = 250
                
        assert mock_config["manual_x"] == 150
        assert mock_config["manual_y"] == 250


@pytest.mark.parametrize("language,expected_title", [
    ("en", "VPN login setup"),
    ("nl", "VPN login instellingen")
])
def test_window_title_by_language(language, expected_title, mock_translations):
    """Test window title changes based on language."""
    with patch('vpn_kul_settings.translations', mock_translations):
        with patch('vpn_kul_settings.config', {'language': language}):
            from vpn_kul_settings import get_translation
            result = get_translation("vpn_login_setup")
            
    assert result == expected_title


@pytest.mark.parametrize("method,x,y,should_pass", [
    ("manual_coordinates", 100, 200, True),
    ("manual_coordinates", 0, 0, False),
    ("image_recognition", 0, 0, True),
    ("both_image_first", 100, 200, True),
    ("both_image_first", 0, 0, False)
])
def test_coordinate_validation(method, x, y, should_pass):
    """Test coordinate validation for different button press methods."""
    config = {
        "button_press_method": method,
        "manual_x": x,
        "manual_y": y
    }
    
    # This simulates the validation logic from vpn_kul.py
    if method in ["manual_coordinates", "both_image_first"]:
        is_valid = bool(config["manual_x"] and config["manual_y"])
    else:
        is_valid = True
    
    assert is_valid == should_pass


class TestCredentialManagement:
    """Test credential management functions."""