import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from tkinter.font import Font

import keyring
import pyautogui
from pynput import mouse

import os
import json
import time
import sys

import ctypes
from ctypes import wintypes
import re

from translations import translations

# Windows API constants
SW_RESTORE = 9
SW_SHOW = 5

# Windows API functions
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

def resource_path(relative_path):
    """Get correct path, works both in development and PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

ENV_FILE = ".env"
SERVICE_NAME = "kuleuvenvpn"
CONFIG_FILE = "vpn_config.json"
ASSETS_FOLDER = resource_path("assets_settings")

def load_config():
    """Load configuration from file with defaults"""
    default_config = {
        "button_press_method": "image_recognition",
        "manual_x": 0,
        "manual_y": 0,
        "speed_multiplier": 1.0,
        "close_tabs": True,
        "close_ivanti": True,
        "ivanti_path": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Pulse Secure\Ivanti Secure Access Client.lnk",
        "img_rel_x": 0.826,
        "img_rel_x": 0.415,
        "language": "en"
    }
    
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            loaded_config = json.load(f)
        # Update loaded config with any missing keys from default config
        for key, value in default_config.items():
            if key not in loaded_config:
                loaded_config[key] = value
        return loaded_config
    return default_config

def save_config(config_data):
    """Save configuration to file"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_data, f)

# Load initial configuration
config = load_config()

def get_translation(key):
    """Get translation for given key"""
    return translations[config['language']].get(key, key)

def resize_icon(image, target_width, target_height):
    """Resize icon using subsample method"""
    original_width = image.width()
    original_height = image.height()
    x_factor = max(1, round(original_width / target_width))
    y_factor = max(1, round(original_height / target_height))
    return image.subsample(x_factor, y_factor)

def clear_frame():
    """Clear all widgets from root window"""
    root.unbind_all("<MouseWheel>")
    for widget in root.winfo_children():
        widget.destroy()

def load_username():
    """Load username from .env file"""
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r") as f:
            for line in f:
                if line.startswith("USERNAME="):
                    return line.strip().split("=", 1)[1]
    return ""

def save_credentials():
    """Save username and password"""
    username = username_entry.get().strip()
    password = password_entry.get()

    if not username or not password:
        messagebox.showwarning(get_translation("invalid_entry"), get_translation("empty_user"))
        return

    keyring.set_password(SERVICE_NAME, username, password)
    with open(ENV_FILE, "w") as f:
        f.write(f"USERNAME={username}\n")
    messagebox.showinfo(get_translation("saved"), get_translation("login_saved"))

def delete_credentials():
    """Delete saved credentials"""
    username = load_username()
    if not username:
        messagebox.showinfo(get_translation("nothing_to_delete"), get_translation("no_saved_username"))
        return

    try:
        keyring.delete_password(SERVICE_NAME, username)
    except keyring.errors.PasswordDeleteError:
        pass

    if os.path.exists(ENV_FILE):
        os.remove(ENV_FILE)
    messagebox.showinfo(get_translation("deleted"), get_translation("login_deleted"))

def find_and_activate_ivanti_window():
    """Find Ivanti window and bring it to the front"""
    def enum_windows_proc(hwnd, lParam):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buffer = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buffer, length + 1)
                window_title = buffer.value.lower()
                
                if any(keyword in window_title for keyword in ['ivanti', 'secure access client']):
                    user32.ShowWindow(hwnd, SW_RESTORE)
                    user32.SetForegroundWindow(hwnd)
                    user32.SetActiveWindow(hwnd)
                    return False
        return True

    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows(EnumWindowsProc(enum_windows_proc), 0)

def toggle_password_visibility(event):
    """Toggle password visibility"""
    if password_entry.cget('show') == '':
        password_entry.config(show="*")
        if use_icons:
            eye_button.config(image=eye_closed)
    else:
        password_entry.config(show="")
        if use_icons:
            eye_button.config(image=eye_open)

def change_language(lang_code):
    """Change application language"""
    config['language'] = lang_code
    save_config(config)
    root.title(get_translation("vpn_login_setup"))
    show_main_menu()

def show_main_menu():
    """Display the main menu"""
    clear_frame()

    main_frame = ttk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    scaled_icon = resize_icon(icon, 256, 256)
    icon_label = ttk.Label(main_frame, image=scaled_icon)
    icon_label.image = scaled_icon
    icon_label.pack(pady=(5, 0))

    center_frame = ttk.Frame(main_frame)
    center_frame.pack(expand=True)

    ttk.Label(center_frame, text=get_translation("what_to_do"), font=("", 12, "bold")).pack(pady=(0, 15))
    
    buttons = [
        ("✏️", "setup_login", show_modify_view),
        ("🗑️", "delete_login", show_delete_view),
        ("🖱️", "set_manual_click", show_manual_click_menu),
        ("⚙️", "options", show_options_menu),
        ("🌐", "language", show_language_menu),
        ("❓", "help", show_help),
        ("❌", "close", root.quit)
    ]
    
    for emoji, key, command in buttons:
        ttk.Button(center_frame, text=f"{emoji} {get_translation(key)}", 
                  width=30, command=command).pack(pady=5)

def show_help():
    """Display the README.md content with markdown formatting"""
    help_window = tk.Toplevel(root)
    help_window.title(get_translation("help"))
    help_window.geometry("900x700")
    help_window.resizable(True, True)
    
    main_frame = ttk.Frame(help_window)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    text_frame = ttk.Frame(main_frame)
    text_frame.pack(fill="both", expand=True)
    
    text_widget = tk.Text(text_frame, wrap="word", font=("Segoe UI", 11), bg="white", fg="black")
    v_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
    h_scrollbar = ttk.Scrollbar(text_frame, orient="horizontal", command=text_widget.xview)
    
    text_widget.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    
    # Configure formatting tags
    formatting_tags = {
        "h1": {"font": ("Segoe UI", 18, "bold"), "foreground": "#2c3e50", "spacing1": 10, "spacing3": 5},
        "h2": {"font": ("Segoe UI", 16, "bold"), "foreground": "#34495e", "spacing1": 8, "spacing3": 4},
        "h3": {"font": ("Segoe UI", 14, "bold"), "foreground": "#34495e", "spacing1": 6, "spacing3": 3},
        "h4": {"font": ("Segoe UI", 12, "bold"), "foreground": "#34495e", "spacing1": 4, "spacing3": 2},
        "bold": {"font": ("Segoe UI", 11, "bold")},
        "italic": {"font": ("Segoe UI", 11, "italic")},
        "code": {"font": ("Consolas", 10), "background": "#f8f9fa", "foreground": "#e74c3c"},
        "list_item": {"lmargin1": 20, "lmargin2": 40},
        "numbered_item": {"lmargin1": 20, "lmargin2": 40}
    }
    
    for tag, config in formatting_tags.items():
        text_widget.tag_configure(tag, **config)
    
    v_scrollbar.pack(side="right", fill="y")
    h_scrollbar.pack(side="bottom", fill="x")
    text_widget.pack(side="left", fill="both", expand=True)
    
    def parse_and_insert_markdown(content):
        """Parse basic markdown and insert with formatting"""
        lines = content.split('\n')
        
        for line in lines:
            line_start = text_widget.index(tk.INSERT)
            
            # Handle headers
            if line.startswith('#### '):
                text_widget.insert(tk.INSERT, line[5:] + '\n')
                text_widget.tag_add("h4", line_start, f"{line_start} lineend")
            elif line.startswith('### '):
                text_widget.insert(tk.INSERT, line[4:] + '\n')
                text_widget.tag_add("h3", line_start, f"{line_start} lineend")
            elif line.startswith('## '):
                text_widget.insert(tk.INSERT, line[3:] + '\n')
                text_widget.tag_add("h2", line_start, f"{line_start} lineend")
            elif line.startswith('# '):
                text_widget.insert(tk.INSERT, line[2:] + '\n')
                text_widget.tag_add("h1", line_start, f"{line_start} lineend")

            else:
                # Handle inline formatting
                formatted_line = line
                text_widget.insert(tk.INSERT, formatted_line + '\n')
                
                # Apply bold formatting
                bold_pattern = r'\*\*(.*?)\*\*'
                for match in re.finditer(bold_pattern, line):
                    start_idx = f"{line_start}+{match.start()}c"
                    end_idx = f"{line_start}+{match.end()}c"
                    # Replace the markdown syntax
                    text_widget.delete(start_idx, end_idx)
                    text_widget.insert(start_idx, match.group(1))
                    new_end = f"{start_idx}+{len(match.group(1))}c"
                    text_widget.tag_add("bold", start_idx, new_end)
    
    # Try to read and display README.md
    try:
        readme_path = os.path.join(os.path.dirname(__file__), "README.md")
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()
        parse_and_insert_markdown(readme_content)
    except FileNotFoundError:
        text_widget.insert("1.0", get_translation("readme_not_found"))
    except Exception as e:
        text_widget.insert("1.0", f"{get_translation('error_reading_readme')}: {str(e)}")
    
    text_widget.config(state="disabled")  # Make it read-only
    
    # Close button
    close_button = ttk.Button(main_frame, text=get_translation("close"), command=help_window.destroy)
    close_button.pack(pady=(10, 0))

def show_language_menu():
    clear_frame()

    ttk.Label(root, text=get_translation("select_language"), font=("", 12, "bold")).pack(pady=(20, 10))

    languages = [
        ("English", "en"),
        ("Nederlands", "nl")
    ]

    for lang_name, lang_code in languages:
        ttk.Button(root, text=lang_name, width=30, command=lambda lc=lang_code: change_language(lc)).pack(pady=5)

    ttk.Button(root, text=get_translation("back_to_menu"), command=show_main_menu).pack(pady=(0, 10), ipadx=5, ipady=3)

def show_modify_view():
    global username_entry, password_entry, eye_button

    clear_frame()

    # Username
    tk.Label(root, text=get_translation("username")).pack(pady=(10, 0))
    username_entry = tk.Entry(root, width=30)
    username_entry.insert(0, load_username())
    username_entry.pack()

    # Password + eye
    tk.Label(root, text=get_translation("password")).pack(pady=(10, 0))
    pw_frame = tk.Frame(root)
    pw_frame.pack()

    password_entry = tk.Entry(pw_frame, width=30, show="*")
    password_entry.pack(side=tk.LEFT)

    if use_icons:
        eye_button = tk.Button(pw_frame, image=eye_closed, width=25, height=25)
        eye_button.image = eye_closed
    else:
        eye_button = tk.Button(pw_frame, text="👁", width=3)
    
    eye_button.pack(side=tk.LEFT, padx=(5, 0))

    eye_button.bind("<ButtonPress-1>", toggle_password_visibility)
    eye_button.bind("<ButtonRelease-1>", toggle_password_visibility)

    # Action buttons
    tk.Button(root, text=get_translation("save"), command=save_credentials).pack(pady=10)
    tk.Button(root, text=get_translation("back_to_menu"), command=show_main_menu).pack(ipadx=5, ipady=3)

def show_delete_view():
    if messagebox.askyesno(get_translation("confirmation"), get_translation("delete_login_confirm")):
        delete_credentials()
    show_main_menu()

def show_options_menu():
    clear_frame()
    
    # Create a canvas with a scrollbar
    canvas = tk.Canvas(root, width=400, height=350)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    def resize_scrollable_frame(event):
        canvas.itemconfig("scrollable_frame", width=event.width)

    canvas.bind("<Configure>", resize_scrollable_frame)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", tags="scrollable_frame")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Styling
    title_font = Font(family="Helvetica", size=12, weight="bold")
    section_bg = "#f0f0f0"
    
    # Button Press Method
    method_frame = ttk.LabelFrame(scrollable_frame, text=get_translation("button_press_method"), padding=10)
    method_frame.pack(fill="x", padx=10, pady=10)
    
    method_var = tk.StringVar(value=config["button_press_method"])
    
    methods = [
        (get_translation("image_recognition"), "image_recognition"),
        (get_translation("manual_coordinates"), "manual_coordinates"),
        (get_translation("try_image_then_manual"), "both_image_first")
    ]
    
    for text, value in methods:
        ttk.Radiobutton(method_frame, text=text, variable=method_var, value=value).pack(anchor="w", pady=2)

    # Manual Click Position
    click_frame = ttk.LabelFrame(scrollable_frame, text=get_translation("manual_click_position"), padding=10)
    click_frame.pack(fill="x", padx=10, pady=10)
    
    x_frame = ttk.Frame(click_frame)
    x_frame.pack(fill="x")
    ttk.Label(x_frame, text=get_translation("x_coordinate")).pack(side="left")
    x_manual = ttk.Entry(x_frame, width=10)
    x_manual.insert(0, str(config["manual_x"]))
    x_manual.pack(side="left", padx=(5, 10))
    
    y_frame = ttk.Frame(click_frame)
    y_frame.pack(fill="x", pady=(5, 0))
    ttk.Label(y_frame, text=get_translation("y_coordinate")).pack(side="left")
    y_manual = ttk.Entry(y_frame, width=10)
    y_manual.insert(0, str(config["manual_y"]))
    y_manual.pack(side="left", padx=(5, 10))

    # Speed Multiplier
    speed_frame = ttk.LabelFrame(scrollable_frame, text=get_translation("speed_multiplier"), padding=10)
    speed_frame.pack(fill="x", padx=10, pady=10)
    
    speed_var = tk.DoubleVar(value=config["speed_multiplier"])
    speed_slider = ttk.Scale(speed_frame, from_=0.5, to=2.0, orient="horizontal", variable=speed_var, length=200)
    speed_slider.pack(fill="x")
    speed_label = ttk.Label(speed_frame, text=f"{get_translation('current')} {speed_var.get():.2f}x")
    speed_label.pack()

    def update_speed_label(event):
        speed_label.config(text=f"{get_translation('current')} {speed_var.get():.2f}x")

    speed_slider.bind("<Motion>", update_speed_label)

    # Closing Options
    closing_frame = ttk.LabelFrame(scrollable_frame, text=get_translation("closing_options"), padding=10)
    closing_frame.pack(fill="x", padx=10, pady=10)
    
    close_tabs_var = tk.BooleanVar(value=config.get("close_tabs", True))
    close_tabs_check = ttk.Checkbutton(closing_frame, text=get_translation("close_browser_tabs"), variable=close_tabs_var)
    close_tabs_check.pack(anchor="w", pady=2)

    close_ivanti_var = tk.BooleanVar(value=config.get("close_ivanti", True))
    close_ivanti_check = ttk.Checkbutton(closing_frame, text=get_translation("close_ivanti"), variable=close_ivanti_var)
    close_ivanti_check.pack(anchor="w", pady=2)

    # Ivanti Path
    ivanti_frame = ttk.LabelFrame(scrollable_frame, text=get_translation("ivanti_path"), padding=10)
    ivanti_frame.pack(fill="x", padx=10, pady=10)
    
    ivanti_path_var = tk.StringVar(value=config.get("ivanti_path", r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Pulse Secure\Ivanti Secure Access Client.lnk"))
    ivanti_path_entry = ttk.Entry(ivanti_frame, textvariable=ivanti_path_var, width=50)
    ivanti_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
    
    def browse_ivanti_path():
        path = filedialog.askopenfilename(filetypes=[("Shortcut files", "*.lnk"), ("All files", "*.*")])
        if path:
            ivanti_path_var.set(path)
    
    ttk.Button(ivanti_frame, text=get_translation("browse"), command=browse_ivanti_path).pack(side="right")

    # Relative position image click
    click_frame_rel = ttk.LabelFrame(scrollable_frame, text=get_translation("relative_click_position"), padding=10)
    click_frame_rel.pack(fill="x", padx=10, pady=10)
    
    x_frame_rel = ttk.Frame(click_frame_rel)
    x_frame_rel.pack(fill="x")
    ttk.Label(x_frame_rel, text=get_translation("relative_x")).pack(side="left")
    x_rel = ttk.Entry(x_frame_rel, width=10)
    x_rel.insert(0, str(config["img_rel_x"]))
    x_rel.pack(side="left", padx=(5, 10))
    
    y_frame_rel = ttk.Frame(click_frame_rel)
    y_frame_rel.pack(fill="x", pady=(5, 0))
    ttk.Label(y_frame_rel, text=get_translation("relative_y")).pack(side="left")
    y_rel = ttk.Entry(y_frame_rel, width=10)
    y_rel.insert(0, str(config["img_rel_y"]))
    y_rel.pack(side="left", padx=(5, 10))


    def save_options():
        config["button_press_method"] = method_var.get()
        try:
            x = int(x_manual.get())
            y = int(y_manual.get())

            if x < 0 or y < 0:
                raise ValueError("Negative coordinates")

            screen_width, screen_height = pyautogui.size()
            if x > screen_width or y > screen_height:
                raise ValueError("Coordinates out of screen bounds")

            config["manual_x"] = x
            config["manual_y"] = y

        except ValueError:
            messagebox.showerror(get_translation("error"), get_translation("invalid_coordinates_absolute"))
            return
        
        try:
            x = float(x_rel.get())
            y = float(y_rel.get())

            if x < 0 or y < 0 or x > 1 or y > 1:
                raise ValueError("Invalid coordinates")

            config["img_rel_x"] = x
            config["img_rel_y"] = y

        except ValueError:
            messagebox.showerror(get_translation("error"), get_translation("invalid_coordinates_relative"))
            return
        config["speed_multiplier"] = speed_var.get()
        config["close_tabs"] = close_tabs_var.get()
        config["close_ivanti"] = close_ivanti_var.get()
        config["ivanti_path"] = ivanti_path_var.get()
        save_config(config)
        messagebox.showinfo(get_translation("saved"), get_translation("options_saved"))
        show_main_menu()

    # Modify the back_to_menu button to unbind the mousewheel event
    def back_to_menu_with_unbind():
        canvas.unbind_all("<MouseWheel>")
        show_main_menu()
    
    ttk.Button(scrollable_frame, text=get_translation("save"), command=save_options).pack(pady=(20, 10))
    ttk.Button(scrollable_frame, text=get_translation("back_to_menu"), command=back_to_menu_with_unbind).pack(pady=(0, 10), ipadx=5, ipady=3)

    # Pack the canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Enable mousewheel scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

def show_manual_click_menu():
    clear_frame()
    
    tk.Label(root, text=get_translation("set_manual_click_position"), font=("", 12, "bold")).pack(pady=(20, 10))
    
    position_label = tk.Label(root, text=get_translation("move_mouse_instruction"))
    position_label.pack(pady=10)
    
    current_pos_label = tk.Label(root, text=f"{get_translation('current_position')} (0, 0)")
    current_pos_label.pack(pady=10)
    
    capture_active = False
    
    def update_position():
        if capture_active:
            x, y = pyautogui.position()
            current_pos_label.config(text=f"{get_translation('current_position')} ({x}, {y})")
            root.after(100, update_position)
    
    def start_capture():
        nonlocal capture_active
        capture_active = True
        
        # Open Ivanti Secure Access
        ivanti_path = config.get("ivanti_path", r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Pulse Secure\Ivanti Secure Access Client.lnk")
        os.startfile(ivanti_path)
        time.sleep(1.2)  # Wait for Ivanti to open
        
        # Find and activate Ivanti window
        find_and_activate_ivanti_window()
        time.sleep(0.5)  # Give it a moment to come to front
        
        start_button.config(state=tk.DISABLED)
        position_label.config(text=get_translation("click_desired_position"))
        
        def on_click(x, y, button, pressed):
            if pressed:
                config["manual_x"] = x
                config["manual_y"] = y
                save_config(config)
                messagebox.showinfo(get_translation("saved"), f"{get_translation('manual_click_set')} ({x}, {y})")
                nonlocal capture_active
                capture_active = False
                root.after(0, show_main_menu)
                return False  # Stop listener
        
        listener = mouse.Listener(on_click=on_click)
        listener.start()
        
        update_position()
    
    start_button = tk.Button(root, text=get_translation("start_position_capture"), command=start_capture)
    start_button.pack(pady=20)
    
    tk.Button(root, text=get_translation("back_to_menu"), command=lambda: [setattr(sys.modules[__name__], 'capture_active', False), show_main_menu()]).pack(ipadx=5, ipady=3)

def clear_frame():
    root.unbind_all("<MouseWheel>")
    for widget in root.winfo_children():
        widget.destroy()

def load_username():
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r") as f:
            for line in f:
                if line.startswith("USERNAME="):
                    return line.strip().split("=", 1)[1]
    return ""

# Windows API constants
SW_RESTORE = 9
SW_SHOW = 5

# Windows API functions
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

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

# Setup window
screen_width,screen_height = pyautogui.size()
screen_width *= 0.3
screen_height *= 0.42
root = tk.Tk()
root.geometry(str(int(screen_width))+"x"+str(int(screen_height)))
root.resizable(True,True)
root.title(get_translation("vpn_login_setup"))

# Set both window corner and taskbar icons
icon_path = os.path.join(ASSETS_FOLDER, "programicon.png")
icon = tk.PhotoImage(file=icon_path)
root.iconphoto(True, icon)

# Try loading icons
try:
    eye_open_original = tk.PhotoImage(file=os.path.join(ASSETS_FOLDER, "eye_open.png"))
    eye_closed_original = tk.PhotoImage(file=os.path.join(ASSETS_FOLDER, "eye_closed.png"))
    
    subsample_factor = max(eye_closed_original.width(), eye_closed_original.height()) // 20
    
    eye_open = eye_open_original.subsample(subsample_factor)
    eye_closed = eye_closed_original.subsample(subsample_factor)
    
    use_icons = True
except Exception as e:
    use_icons = False

# Start GUI
show_main_menu()
root.mainloop()