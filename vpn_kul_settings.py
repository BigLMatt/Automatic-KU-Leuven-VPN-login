import tkinter as tk
from tkinter import messagebox
import keyring
import os

ENV_FILE = ".env"
SERVICE_NAME = "kuleuvenvpn"

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

def show_password(event):
    password_entry.config(show="")
    if use_icons:
        eye_button.config(image=eye_open)

def hide_password(event):
    password_entry.config(show="*")
    if use_icons:
        eye_button.config(image=eye_closed)

def show_main_menu():
    clear_frame()
    tk.Label(root, text="What do you want to do?").pack(pady=20)
    tk.Button(root, text="✏️  Setup login", width=30, command=show_modify_view).pack(pady=5)
    tk.Button(root, text="🗑️  Delete login", width=30, command=show_delete_view).pack(pady=5)
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
        eye_button = tk.Button(pw_frame, image=eye_closed, width=25, height=25)  # Adjust width and height as needed
    else:
        eye_button = tk.Button(pw_frame, text="👁", width=3)
    
    eye_button.pack(side=tk.LEFT, padx=(5, 0))
    eye_button.bind("<ButtonPress>", show_password)
    eye_button.bind("<ButtonRelease>", hide_password)

    # Action buttons
    tk.Button(root, text="Save", command=save_credentials).pack(pady=10)
    tk.Button(root, text="Back to menu", command=show_main_menu).pack()

def show_delete_view():
    if messagebox.askyesno("Confirmation", "Are you sure you want to delete your login?"):
        delete_credentials()
    show_main_menu()

def clear_frame():
    for widget in root.winfo_children():
        widget.destroy()

# Setup window
root = tk.Tk()
root.title("VPN login setup")
root.geometry("430x375")
root.iconbitmap("programicon.ico")
root.resizable(False, False)

# Try loading icons
try:
    # Load and resize the icons
    eye_open_original = tk.PhotoImage(file="eye.png")
    eye_closed_original = tk.PhotoImage(file="eye_closed.png")
    
    # Resize to 20x20 pixels (adjust this size as needed)
    eye_open = eye_open_original.subsample(int(eye_open_original.width() / 20), int(eye_open_original.height() / 20))
    eye_closed = eye_closed_original.subsample(int(eye_closed_original.width() / 20), int(eye_closed_original.height() / 20))
    
    use_icons = True
except Exception as e:
    print(f"Error loading icons: {e}")
    use_icons = False

# Start GUI
show_main_menu()
root.mainloop()
