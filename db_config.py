import os
import json
from tkinter import Tk, filedialog

CONFIG_FILE = "config.json"

def select_db_folder():
    try:
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        folder = filedialog.askdirectory(title="Select Database Folder")
        return folder
    except:
        False

def save_path(path):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"db_path": path}, f)

def load_path():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)["db_path"]
    return None

def get_db_path():
    path = load_path()

    # ✅ agar user ne path select kiya hai
    if path:
        return os.path.join(path, "database.db")

    # ❗ first time run → default (optional)
    default = os.path.join(os.environ["PUBLIC"], "StudentSystem")

    if not os.path.exists(default):
        os.makedirs(default)

    return os.path.join(default, "database.db")

def change_db_path():
    try:
        path = select_db_folder()

        if path:
            if not os.path.exists(path):
                os.makedirs(path)

            save_path(path)
            return True

        return False
    except:
        return False