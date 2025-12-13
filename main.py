import tkinter as tk
import sys
import ctypes
from ui.main_window import MainWindow

# --- WINDOWS TASKBAR ICON SETUP ---
if sys.platform.startswith('win'):
    try:
        # Set a unique Application User Model ID (AUMID)
        app_id = 'HabitGarden.Tracker.1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except AttributeError:
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()