import tkinter as tk
from tkinter import ttk
from db_config import get_connection
from models import Habit
from datetime import date, timedelta

COLORS = {
    "bg_main": "#F8F4E6",
    "primary": "#48A048",
    "text": "#333333",
    "white": "#FFFFFF"
}


class HabitDetailWindow(tk.Toplevel):
    def __init__(self, parent, habit):
        super().__init__(parent)
        self.habit = habit
        self.title(f"Details: {habit.name}")
        self.geometry("400x550")
        self.configure(bg=COLORS["bg_main"])

        # --- HEADER ---
        tk.Label(self, text=habit.name, font=("Segoe UI", 18, "bold"),
                 bg=COLORS["bg_main"], fg=COLORS["text"]).pack(pady=(20, 10))

        # --- STATS CARD ---
        stats_frame = tk.Frame(self, bg=COLORS["white"], bd=1, relief="solid")
        stats_frame.pack(pady=10, padx=20, fill="x", ipadx=10, ipady=10)

        def add_stat(row, label, value):
            tk.Label(stats_frame, text=label, font=("Segoe UI", 10, "bold"),
                     bg=COLORS["white"], fg="#555").grid(row=row, column=0, sticky="w", padx=10, pady=5)
            tk.Label(stats_frame, text=value, font=("Segoe UI", 10),
                     bg=COLORS["white"], fg="#000").grid(row=row, column=1, sticky="w", padx=10, pady=5)

        add_stat(0, "Total XP:", f"{habit.xp}")
        add_stat(1, "Daily Goal:", f"{habit.daily_goal} / day")
        current_streak = habit.get_streak()
        add_stat(2, "Current Streak:", f"🔥 {current_streak} days")

        # --- HISTORY SECTION ---
        history_header_frame = tk.Frame(self, bg=COLORS["bg_main"])
        history_header_frame.pack(pady=(20, 5), padx=20, fill="x")

        tk.Label(history_header_frame, text="📅 Recent History", font=("Segoe UI", 12, "bold"),
                 bg=COLORS["bg_main"], fg=COLORS["text"]).pack(side=tk.LEFT)

        self.filter_var = tk.StringVar(self, value="All")
        self.filter_options = ["All", "Completed", "Missed"]
        filter_combo = ttk.Combobox(history_header_frame,
                                    textvariable=self.filter_var,
                                    values=self.filter_options,
                                    width=10,
                                    state="readonly",
                                    font=("Segoe UI", 10))
        filter_combo.pack(side=tk.RIGHT)

        filter_combo.bind("<<ComboboxSelected>>", lambda event: self.load_history())

        list_frame = tk.Frame(self, bg=COLORS["bg_main"])
        list_frame.pack(fill="both", expand=True, padx=20, pady=5)

        self.history_list = tk.Listbox(list_frame, height=10, font=("Segoe UI", 10),
                                       activestyle='none', bd=0, highlightthickness=1)
        self.history_list.pack(side=tk.LEFT, fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.history_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.history_list.config(yscrollcommand=scrollbar.set)

        self.load_history()

        tk.Button(self, text="Close", bg=COLORS["primary"], fg="white", font=("Segoe UI", 10, "bold"),
                  padx=20, pady=5, bd=0, command=self.destroy).pack(pady=20)

    def load_history(self):
        self.history_list.delete(0, tk.END)

        current_filter = self.filter_var.get()
        today = date.today()

        conn = get_connection()
        cursor = conn.cursor()
        try:
            # 1. Fetch ALL logs
            cursor.execute(
                "SELECT log_date, completed FROM habit_logs WHERE habit_id=%s",
                (self.habit.habit_id,)
            )
            rows = cursor.fetchall()

            # Map existing logs
            existing_logs = {row[0]: row[1] for row in rows}
            records_found = False

            # 2. Iterate LAST 30 DAYS
            for i in range(30):
                check_date = today - timedelta(days=i)

                # Check if we have data for this date
                is_completed = existing_logs.get(check_date, False)

                # Skip dates before habit creation
                if not is_completed and check_date < self.habit.created_at:
                    continue

                # Filter Logic
                if current_filter == "Completed" and not is_completed:
                    continue

                if current_filter == "Missed" and is_completed:
                    continue

                records_found = True
                status = "✅ Completed" if is_completed else "❌ Missed"
                self.history_list.insert(tk.END, f" {check_date}  —  {status}")

            if not records_found:
                self.history_list.insert(tk.END, f" No records found for: {current_filter}")

        except Exception as e:
            self.history_list.insert(tk.END, "Error loading history.")
            print(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()