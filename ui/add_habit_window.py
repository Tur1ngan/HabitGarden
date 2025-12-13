import tkinter as tk
from tkinter import ttk, messagebox
from models import Habit


class AddHabitWindow(tk.Toplevel):
    def __init__(self, parent, refresh_callback):
        super().__init__(parent)
        self.title("Add New Habit")
        self.geometry("350x250")
        self.refresh_callback = refresh_callback

        # Make this window modal
        self.transient(parent)
        self.grab_set()

        # --- UI Elements ---

        # Title
        tk.Label(self, text="New Habit", font=("Helvetica", 14, "bold")).pack(pady=15)

        # Name Input
        input_frame = tk.Frame(self)
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Habit Name:").grid(row=0, column=0, padx=5, sticky="e")
        self.name_entry = tk.Entry(input_frame, width=25)
        self.name_entry.grid(row=0, column=1, padx=5)
        self.name_entry.focus()

        # Daily Goal Input
        tk.Label(input_frame, text="Daily Goal:").grid(row=1, column=0, padx=5, pady=10, sticky="e")
        self.goal_entry = tk.Entry(input_frame, width=10)
        self.goal_entry.insert(0, "1")
        self.goal_entry.grid(row=1, column=1, padx=5, pady=10, sticky="w")

        # Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Save Habit", bg="#4CAF50", fg="white", command=self.save_habit).pack(side=tk.LEFT,
                                                                                                           padx=10)

    def save_habit(self):
        name = self.name_entry.get().strip()
        goal_str = self.goal_entry.get().strip()

        # Validation
        if not name:
            messagebox.showwarning("Required", "Please enter a habit name.")
            return

        try:
            daily_goal = int(goal_str)
            if daily_goal < 1:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid Input", "Daily goal must be a number greater than 0.")
            return

        # Save to Database
        Habit.add(name, daily_goal)

        # Refresh the main list and close window
        if self.refresh_callback:
            self.refresh_callback()

        self.destroy()