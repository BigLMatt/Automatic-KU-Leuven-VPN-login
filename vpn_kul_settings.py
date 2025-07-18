import tkinter as tk
from tkinter import messagebox, ttk, filedialog, PhotoImage
from tkinter.font import Font

import keyring
import pyautogui
from pynput import mouse

import os
import json
import time
import sys

from translations import translations

def get_translation(key):
    return translations[config['language']].get(key, key)

def resource_path(relative_path):
    """ Get correct path, works both in development and PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

ENV_FILE = ".env"
SERVICE_NAME = "kuleuvenvpn"
CONFIG_FILE = "vpn_config.json"
ASSETS_FOLDER = resource_path("assets_settings")

# Load configuration
def load_config():
    default_config = {
        "button_press_method": "manual_coordinates",
        "manual_x": 0,
        "manual_y": 0,
        "speed_multiplier": 1.0,
        "close_tabs": True,
        "close_ivanti": True,
        "ivanti_path": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Pulse Secure\Ivanti Secure Access Client.lnk",
        "language": "en"
    }
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            loaded_config = json.load(f)
        # Update the loaded config with any missing keys from the default config
        for key, value in default_config.items():
            if key not in loaded_config:
                loaded_config[key] = value
        return loaded_config
    return default_config

# Save configuration
def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

# Load initial configuration
config = load_config()

def resize_icon(image, target_width, target_height):
    # Bepaal originele grootte
    original_width = image.width()
    original_height = image.height()

    # Bereken subsample-factor
    x_factor = max(1, round(original_width / target_width))
    y_factor = max(1, round(original_height / target_height))

    # Pas subsample toe (alleen verkleinen!)
    resized = image.subsample(x_factor, y_factor)
    return resized

def show_main_menu():
    clear_frame()

    # Create a main frame to hold all content
    main_frame = ttk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    # Add program icon
    scaled_icon = resize_icon(icon, 256, 256)
    
    icon_label = ttk.Label(main_frame, image=scaled_icon)
    icon_label.image = scaled_icon  # Keep a reference
    icon_label.pack(pady=(5, 0))

    # Center frame for text and buttons
    center_frame = ttk.Frame(main_frame)
    center_frame.pack(expand=True)

    # Main menu content
    ttk.Label(center_frame, text=get_translation("what_to_do"), font=("", 12, "bold")).pack(pady=(0, 15))
    ttk.Button(center_frame, text=f"✏️  {get_translation('setup_login')}", width=30, command=show_modify_view).pack(pady=5)
    ttk.Button(center_frame, text=f"🗑️  {get_translation('delete_login')}", width=30, command=show_delete_view).pack(pady=5)
    ttk.Button(center_frame, text=f"🖱️  {get_translation('set_manual_click')}", width=30, command=show_manual_click_menu).pack(pady=5)
    ttk.Button(center_frame, text=f"⚙️  {get_translation('options')}", width=30, command=show_options_menu).pack(pady=5)
    ttk.Button(center_frame, text=f"🌐  {get_translation('language')}", width=30, command=show_language_menu).pack(pady=5)
    ttk.Button(center_frame, text=f"❌ {get_translation('close')}", width=30, command=root.quit).pack(pady=5)

def show_language_menu():
    clear_frame()

    ttk.Label(root, text=get_translation("select_language"), font=("", 12, "bold")).pack(pady=(20, 10))

    languages = [
        ("English", "en"),
        ("Nederlands", "nl")
    ]

    for lang_name, lang_code in languages:
        ttk.Button(root, text=lang_name, width=30, command=lambda lc=lang_code: change_language(lc)).pack(pady=5)

    ttk.Button(root, text=get_translation("back_to_menu"), command=show_main_menu).pack(pady=20)

def change_language(lang_code):
    config['language'] = lang_code
    save_config(config)
    root.title(get_translation("vpn_login_setup"))
    show_main_menu()

def save_credentials():
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

password_visible = False

def toggle_password_visibility(event):
    if password_entry.cget('show') == '':
        password_entry.config(show="*")
        if use_icons:
            eye_button.config(image=eye_closed)
    else:
        password_entry.config(show="")
        if use_icons:
            eye_button.config(image=eye_open)

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
    tk.Button(root, text=get_translation("back_to_menu"), command=show_main_menu).pack()

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

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
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
    x_entry = ttk.Entry(x_frame, width=10)
    x_entry.insert(0, str(config["manual_x"]))
    x_entry.pack(side="left", padx=(5, 10))
    
    y_frame = ttk.Frame(click_frame)
    y_frame.pack(fill="x", pady=(5, 0))
    ttk.Label(y_frame, text=get_translation("y_coordinate")).pack(side="left")
    y_entry = ttk.Entry(y_frame, width=10)
    y_entry.insert(0, str(config["manual_y"]))
    y_entry.pack(side="left", padx=(5, 10))

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

    def save_options():
        config["button_press_method"] = method_var.get()
        try:
            config["manual_x"] = int(x_entry.get())
            config["manual_y"] = int(y_entry.get())
        except ValueError:
            messagebox.showerror(get_translation("error"), get_translation("invalid_coordinates"))
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
    ttk.Button(scrollable_frame, text=get_translation("back_to_menu"), command=back_to_menu_with_unbind).pack(pady=(0, 10))

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
    
    tk.Button(root, text=get_translation("back_to_menu"), command=lambda: [setattr(sys.modules[__name__], 'capture_active', False), show_main_menu()]).pack()

def clear_frame():
    root.unbind_all("<MouseWheel>")  # Unbind mousewheel event
    for widget in root.winfo_children():
        widget.destroy()

def load_username():
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r") as f:
            for line in f:
                if line.startswith("USERNAME="):
                    return line.strip().split("=", 1)[1]
    return ""

# Setup window
root = tk.Tk()
root.title(get_translation("vpn_login_setup"))
root.geometry("700x600")

# Set both window corner and taskbar icons
icon_path = os.path.join(ASSETS_FOLDER, "programicon.png")
icon = tk.PhotoImage(file=icon_path)
root.iconphoto(True, icon)

root.resizable(False, False)

# Try loading icons
try:
    eye_open_original = tk.PhotoImage(file=os.path.join(ASSETS_FOLDER, "eye_open.png"))
    eye_closed_original = tk.PhotoImage(file=os.path.join(ASSETS_FOLDER, "eye_closed.png"))
    
    subsample_factor = max(eye_closed_original.width(), eye_closed_original.height()) // 20
    
    eye_open = eye_open_original.subsample(subsample_factor)
    eye_closed = eye_closed_original.subsample(subsample_factor)
    
    use_icons = True
except Exception as e:
    print(f"Error loading icons: {e}")
    use_icons = False

# Start GUI
show_main_menu()
root.mainloop()