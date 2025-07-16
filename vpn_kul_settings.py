import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from tkinter.font import Font
import keyring
import os
import json
import pyautogui
import time
import threading
import sys
from pynput import mouse

ENV_FILE = ".env"
SERVICE_NAME = "kuleuvenvpn"
CONFIG_FILE = "vpn_config.json"
ASSETS_FOLDER = "assets"

# Load configuration
def load_config():
    default_config = {
        "button_press_method": "image_recognition",
        "manual_x": 0,
        "manual_y": 0,
        "speed_multiplier": 1.0,
        "close_tabs": True,
        "close_ivanti": True,
        "ivanti_path": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Pulse Secure\Ivanti Secure Access Client.lnk"
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
    default_config = {
        "button_press_method": "image_recognition",
        "manual_x": 0,
        "manual_y": 0,
        "speed_multiplier": 1.0,
        "close_tabs": True,
        "close_ivanti": True,
        "ivanti_path": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Pulse Secure\Ivanti Secure Access Client.lnk"
    }
    # Ensure all keys are present in the config before saving
    for key in default_config:
        if key not in config:
            config[key] = default_config[key]
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

# Load initial configuration
config = load_config()

def load_username():
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r") as f:
            for line in f:
                if line.startswith("USERNAME="):
                    return line.strip().split("=", 1)[1]
    return ""

def save_credentials():
    username = username_entry.get().strip()
    password = password_entry.get()

    if not username or not password:
        messagebox.showwarning("Invalid entry", "Username and password cannot be empty.")
        return

    keyring.set_password(SERVICE_NAME, username, password)

    with open(ENV_FILE, "w") as f:
        f.write(f"USERNAME={username}\n")

    messagebox.showinfo("Saved", "The login is saved.")

def delete_credentials():
    username = load_username()
    if not username:
        messagebox.showinfo("Nothing to be deleted", "There is no saved username.")
        return

    try:
        keyring.delete_password(SERVICE_NAME, username)
    except keyring.errors.PasswordDeleteError:
        pass

    if os.path.exists(ENV_FILE):
        os.remove(ENV_FILE)

    messagebox.showinfo("Deleted", "Login has been deleted successfully.")

password_visible = False

def toggle_password_visibility(event):
    global password_visible
    password_visible = not password_visible
    
    if password_visible:
        password_entry.config(show="")
        if use_icons:
            eye_button.config(image=eye_open)
            eye_button.image = eye_open
    else:
        password_entry.config(show="*")
        if use_icons:
            eye_button.config(image=eye_closed)
            eye_button.image = eye_closed

def show_main_menu():
    clear_frame()
    tk.Label(root, text="What do you want to do?").pack(pady=20)
    tk.Button(root, text="✏️  Setup login", width=30, command=show_modify_view).pack(pady=5)
    tk.Button(root, text="🗑️  Delete login", width=30, command=show_delete_view).pack(pady=5)
    tk.Button(root, text="🖱️  Set Manual Click Position", width=30, command=show_manual_click_menu).pack(pady=5)
    tk.Button(root, text="⚙️  Options", width=30, command=show_options_menu).pack(pady=5)
    tk.Button(root, text="❌ Close", width=30, command=root.quit).pack(pady=5)

def show_modify_view():
    global username_entry, password_entry, eye_button

    clear_frame()

    # Username
    tk.Label(root, text="Username:").pack(pady=(10, 0))
    username_entry = tk.Entry(root, width=30)
    username_entry.insert(0, load_username())
    username_entry.pack()

    # Password + eye
    tk.Label(root, text="Password:").pack(pady=(10, 0))
    pw_frame = tk.Frame(root)
    pw_frame.pack()

    password_entry = tk.Entry(pw_frame, width=30, show="*")
    password_entry.pack(side=tk.LEFT)

    if use_icons:
        eye_button = tk.Button(pw_frame, image=eye_closed, width=25, height=25)
        eye_button.image = eye_closed  # Keep a reference
    else:
        eye_button = tk.Button(pw_frame, text="👁", width=3)
    
    eye_button.pack(side=tk.LEFT, padx=(5, 0))
    eye_button.bind("<Button-1>", toggle_password_visibility)

    # Action buttons
    tk.Button(root, text="Save", command=save_credentials).pack(pady=10)
    tk.Button(root, text="Back to menu", command=show_main_menu).pack()

def show_delete_view():
    if messagebox.askyesno("Confirmation", "Are you sure you want to delete your login?"):
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
    method_frame = ttk.LabelFrame(scrollable_frame, text="Button Press Method", padding=10)
    method_frame.pack(fill="x", padx=10, pady=10)
    
    method_var = tk.StringVar(value=config["button_press_method"])
    
    methods = [
        ("Image Recognition", "image_recognition"),
        ("Manual Coordinates", "manual_coordinates"),
        ("Try Image Recognition, then Manual", "both_image_first")
    ]
    
    for text, value in methods:
        ttk.Radiobutton(method_frame, text=text, variable=method_var, value=value).pack(anchor="w", pady=2)

    # Manual Click Position
    click_frame = ttk.LabelFrame(scrollable_frame, text="Manual Click Position", padding=10)
    click_frame.pack(fill="x", padx=10, pady=10)
    
    x_frame = ttk.Frame(click_frame)
    x_frame.pack(fill="x")
    ttk.Label(x_frame, text="X coordinate:").pack(side="left")
    x_entry = ttk.Entry(x_frame, width=10)
    x_entry.insert(0, str(config["manual_x"]))
    x_entry.pack(side="left", padx=(5, 10))
    
    y_frame = ttk.Frame(click_frame)
    y_frame.pack(fill="x", pady=(5, 0))
    ttk.Label(y_frame, text="Y coordinate:").pack(side="left")
    y_entry = ttk.Entry(y_frame, width=10)
    y_entry.insert(0, str(config["manual_y"]))
    y_entry.pack(side="left", padx=(5, 10))

    # Speed Multiplier
    speed_frame = ttk.LabelFrame(scrollable_frame, text="Speed Multiplier", padding=10)
    speed_frame.pack(fill="x", padx=10, pady=10)
    
    speed_var = tk.DoubleVar(value=config["speed_multiplier"])
    speed_slider = ttk.Scale(speed_frame, from_=0.5, to=2.0, orient="horizontal", variable=speed_var, length=200)
    speed_slider.pack(fill="x")
    speed_label = ttk.Label(speed_frame, text=f"Current: {speed_var.get():.2f}x")
    speed_label.pack()

    def update_speed_label(event):
        speed_label.config(text=f"Current: {speed_var.get():.2f}x")

    speed_slider.bind("<Motion>", update_speed_label)

    # Closing Options
    closing_frame = ttk.LabelFrame(scrollable_frame, text="Closing Options", padding=10)
    closing_frame.pack(fill="x", padx=10, pady=10)
    
    close_tabs_var = tk.BooleanVar(value=config.get("close_tabs", True))
    close_tabs_check = ttk.Checkbutton(closing_frame, text="Close browser tabs after connection", variable=close_tabs_var)
    close_tabs_check.pack(anchor="w", pady=2)

    close_ivanti_var = tk.BooleanVar(value=config.get("close_ivanti", True))
    close_ivanti_check = ttk.Checkbutton(closing_frame, text="Close Ivanti after connection", variable=close_ivanti_var)
    close_ivanti_check.pack(anchor="w", pady=2)

    # Ivanti Path
    ivanti_frame = ttk.LabelFrame(scrollable_frame, text="Ivanti Path", padding=10)
    ivanti_frame.pack(fill="x", padx=10, pady=10)
    
    ivanti_path_var = tk.StringVar(value=config.get("ivanti_path", r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Pulse Secure\Ivanti Secure Access Client.lnk"))
    ivanti_path_entry = ttk.Entry(ivanti_frame, textvariable=ivanti_path_var, width=50)
    ivanti_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
    
    def browse_ivanti_path():
        path = filedialog.askopenfilename(filetypes=[("Shortcut files", "*.lnk"), ("All files", "*.*")])
        if path:
            ivanti_path_var.set(path)
    
    ttk.Button(ivanti_frame, text="Browse", command=browse_ivanti_path).pack(side="right")

    def save_options():
        config["button_press_method"] = method_var.get()
        try:
            config["manual_x"] = int(x_entry.get())
            config["manual_y"] = int(y_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid integer coordinates.")
            return
        config["speed_multiplier"] = speed_var.get()
        config["close_tabs"] = close_tabs_var.get()
        config["close_ivanti"] = close_ivanti_var.get()
        config["ivanti_path"] = ivanti_path_var.get()
        save_config(config)
        messagebox.showinfo("Saved", "Options have been saved successfully.")
        show_main_menu()
    
    ttk.Button(scrollable_frame, text="Save", command=save_options).pack(pady=(20, 10))
    ttk.Button(scrollable_frame, text="Back to menu", command=show_main_menu).pack(pady=(0, 10))

    # Pack the canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Enable mousewheel scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

def show_manual_click_menu():
    clear_frame()
    
    tk.Label(root, text="Set Manual Click Position", font=("", 12, "bold")).pack(pady=(20, 10))
    
    position_label = tk.Label(root, text="Move your mouse to the desired position and click.")
    position_label.pack(pady=10)
    
    current_pos_label = tk.Label(root, text="Current position: (0, 0)")
    current_pos_label.pack(pady=10)
    
    capture_active = False
    
    def update_position():
        if capture_active:
            x, y = pyautogui.position()
            current_pos_label.config(text=f"Current position: ({x}, {y})")
            root.after(100, update_position)
    
    def start_capture():
        nonlocal capture_active
        capture_active = True
        
        # Open Ivanti Secure Access
        ivanti_path = config.get("ivanti_path", r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Pulse Secure\Ivanti Secure Access Client.lnk")
        os.startfile(ivanti_path)
        time.sleep(1.2)  # Wait for Ivanti to open
        
        start_button.config(state=tk.DISABLED)
        position_label.config(text="Click on the desired position (e.g., the connect button)")
        
        def on_click(x, y, button, pressed):
            if pressed:
                config["manual_x"] = x
                config["manual_y"] = y
                save_config(config)
                messagebox.showinfo("Saved", f"Manual click position set to: ({x}, {y})")
                nonlocal capture_active
                capture_active = False
                root.after(0, show_main_menu)
                return False  # Stop listener
        
        listener = mouse.Listener(on_click=on_click)
        listener.start()
        
        update_position()
    
    start_button = tk.Button(root, text="Start Position Capture", command=start_capture)
    start_button.pack(pady=20)
    
    tk.Button(root, text="Back to menu", command=lambda: [setattr(sys.modules[__name__], 'capture_active', False), show_main_menu()]).pack()

def clear_frame():
    for widget in root.winfo_children():
        widget.destroy()

# Setup window
root = tk.Tk()
root.title("VPN login setup")
root.geometry("700x550")
root.iconbitmap(os.path.join(ASSETS_FOLDER, "programicon.ico"))
root.resizable(False, False)

# Try loading icons
try:
    eye_open_original = tk.PhotoImage(file=os.path.join(ASSETS_FOLDER, "eye_open.png"))
    eye_closed_original = tk.PhotoImage(file=os.path.join(ASSETS_FOLDER, "eye_closed.png"))
    
    subsample_factor = max(eye_open_original.width(), eye_open_original.height()) // 20
    
    eye_open = eye_open_original.subsample(subsample_factor)
    eye_closed = eye_closed_original.subsample(subsample_factor)
    
    use_icons = True
    print("Icons loaded successfully")
except Exception as e:
    print(f"Error loading icons: {e}")
    use_icons = False

# Start GUI
show_main_menu()
root.mainloop()