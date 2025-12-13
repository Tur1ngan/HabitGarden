import tkinter as tk
from tkinter import ttk, messagebox
from models import Habit
from PIL import Image, ImageTk
import os

from .add_habit_window import AddHabitWindow
from .habit_detail_window import HabitDetailWindow

# --- THEME CONFIGURATION ---
COLORS = {
    "bg_main": "#F8F4E6",
    "bg_frame": "#E4E0C0",
    "primary": "#48A048",
    "primary_hover": "#60B860",
    "secondary": "#A89040",
    "danger": "#D05050",
    "text": "#333333",
    "white": "#FFFFFF"
}

FONT_MAIN = ("Arial", 10)
FONT_BOLD = ("Arial", 10, "bold")
FONT_TITLE = ("Arial", 22, "bold")


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Habit Garden")
        self.root.geometry("850x700")
        self.root.configure(bg=COLORS["bg_main"])

        # --- SET APPLICATION ICON ---
        icon_path = os.path.join("assets", "icon.png")

        if os.path.exists(icon_path):
            try:
                icon_img = Image.open(icon_path).resize((64, 64), Image.LANCZOS)
                self.app_icon = ImageTk.PhotoImage(icon_img)
                self.root.iconphoto(True, self.app_icon)
            except Exception as e:
                print(f"Error loading icon: {e}")
        # ------------------------------------------------

        # --- STYLE CONFIGURATION ---
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # 1. Blocky Button Style
        self.style.configure("TButton",
                             background=COLORS["primary"],
                             foreground=COLORS["white"],
                             font=FONT_BOLD,
                             padding=[10, 5],
                             borderwidth=3,
                             relief="raised")
        self.style.map("TButton",
                       background=[('active', COLORS["primary_hover"]),
                                   ('pressed', COLORS["primary"])],
                       foreground=[('disabled', COLORS["text"])])

        # 2. Treeview Colors
        self.style.configure("Treeview",
                             background=COLORS["bg_frame"],
                             fieldbackground=COLORS["bg_frame"],
                             foreground=COLORS["text"],
                             rowheight=30,
                             font=FONT_MAIN)

        self.style.configure("Treeview.Heading",
                             background=COLORS["primary"],
                             foreground=COLORS["white"],
                             font=FONT_BOLD,
                             relief="flat")
        self.style.map("Treeview.Heading", background=[('active', COLORS["primary_hover"])])

        self.style.map("Treeview",
                       background=[('selected', COLORS["primary_hover"])],
                       foreground=[('selected', COLORS["white"])])

        # 3. Custom Button Styles
        self.style.configure("Secondary.TButton",
                             background=COLORS["secondary"],
                             foreground=COLORS["white"])
        self.style.map("Secondary.TButton",
                       background=[('active', COLORS["secondary"]), ('pressed', COLORS["secondary"])])

        self.style.configure("Danger.TButton",
                             background=COLORS["danger"],
                             foreground=COLORS["white"])
        self.style.map("Danger.TButton",
                       background=[('active', COLORS["danger"]), ('pressed', COLORS["danger"])])

        # --- TITLE SECTION ---
        header_frame = tk.Frame(root, bg=COLORS["bg_main"])
        header_frame.pack(fill="x", pady=(20, 10))

        tk.Label(header_frame, text="🌿 Habit Garden",
                 font=FONT_TITLE, bg=COLORS["bg_main"], fg=COLORS["primary"]).pack()

        tk.Label(header_frame, text="Plant seeds, track habits, watch them grow!",
                 font=("Arial", 10, "italic"), bg=COLORS["bg_main"], fg=COLORS["text"]).pack()

        # --- ACTION BUTTONS ---
        self.button_frame = tk.Frame(root, bg=COLORS["bg_main"])
        self.button_frame.pack(pady=20, fill="x", side=tk.BOTTOM)

        container = tk.Frame(self.button_frame, bg=COLORS["bg_main"])
        container.pack()

        ttk.Button(container, text="➕ New Habit",
                   command=self.add_habit).pack(side=tk.LEFT, padx=10)

        ttk.Button(container, text="✅ Complete Today",
                   command=self.complete_habit_today,
                   style="Secondary.TButton").pack(side=tk.LEFT, padx=10)

        ttk.Button(container, text="🗑 Delete",
                   command=self.delete_habit,
                   style="Danger.TButton").pack(side=tk.LEFT, padx=10)

        # --- PLANT DISPLAY AREA ---
        self.plant_frame = tk.Frame(root, bg=COLORS["bg_main"], bd=0, relief="flat")
        self.plant_frame.pack(pady=15, padx=20, ipadx=20, ipady=10, side=tk.BOTTOM)

        self.image_label = tk.Label(self.plant_frame, bg=COLORS["bg_main"])
        self.image_label.pack()

        self.status_label = tk.Label(self.plant_frame, text="Select a habit to see your plant",
                                     font=FONT_BOLD, bg=COLORS["bg_main"], fg=COLORS["text"])
        self.status_label.pack(pady=5)

        # --- TREEVIEW (HABIT LIST) ---
        list_frame = tk.Frame(root, bg=COLORS["bg_main"], padx=20)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(list_frame, columns=("XP", "Stage", "Streak"), style="Treeview")

        self.tree.heading("#0", text="Habit Name", anchor="w")
        self.tree.column("#0", width=250, stretch=tk.YES)

        # Headings
        self.tree.heading("XP", text="✨ XP")
        self.tree.column("XP", width=80, anchor="center")
        self.tree.heading("Stage", text="🌱 Plant Stage")
        self.tree.column("Stage", width=150, anchor="center")
        self.tree.heading("Streak", text="🔥 Streak")
        self.tree.column("Streak", width=80, anchor="center")

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", lambda event: self.update_plant_image())
        self.tree.bind("<Double-1>", self.open_habit_detail)

        self.habits = []
        self.streaks = {}
        self.load_habits()

    # --- Methods ---
    def load_habits(self):
        self.habits = Habit.get_all()

        for i in self.tree.get_children():
            self.tree.delete(i)

        for i, h in enumerate(self.habits):
            streak = h.get_streak()
            self.streaks[h.habit_id] = streak
            stage = self.get_stage(h.xp)

            tag = "even" if i % 2 == 0 else "odd"

            self.tree.insert("", tk.END, iid=h.habit_id, text=h.name,
                             values=(f"{h.xp}", stage, f"{streak} days"), tags=(tag,))

        self.tree.tag_configure("odd", background=COLORS["bg_frame"])
        self.tree.tag_configure("even", background=COLORS["white"])

        self.update_plant_image()

    def add_habit(self):
        AddHabitWindow(self.root, self.load_habits)

    def open_habit_detail(self, event):
        selected = self.tree.selection()
        if not selected: return
        habit_id = selected[0]
        habit_obj = next((h for h in self.habits if str(h.habit_id) == str(habit_id)), None)
        if habit_obj:
            HabitDetailWindow(self.root, habit_obj)

    def delete_habit(self):
        selected = self.tree.selection()
        if selected:
            confirm = messagebox.askyesno("Delete", "Are you sure you want to delete this habit?", parent=self.root)
            if confirm:
                Habit.delete(selected[0])
                self.load_habits()
        else:
            messagebox.showwarning("Select", "Please select a habit to delete.", parent=self.root)

    def complete_habit_today(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a habit to complete.", parent=self.root)
            return

        habit_id = selected[0]
        habit_obj = next((h for h in self.habits if str(h.habit_id) == str(habit_id)), None)

        if habit_obj:
            logged_successfully = habit_obj.log_today()

            if logged_successfully:
                messagebox.showinfo("Habit Completed! 🎉",
                                    f"You completed '{habit_obj.name}' today! Keep up the good work!",
                                    parent=self.root)

                self.show_xp_feedback()
                self.load_habits()
            else:
                messagebox.showwarning("Already Completed",
                                       f"You have already completed '{habit_obj.name}' for today. Come back tomorrow!",
                                       parent=self.root)

    def show_xp_feedback(self):
        xp_feedback_label = tk.Label(self.root,
                                     text="+50 XP! 🎉",
                                     font=("Arial", 30, "bold"),
                                     bg=COLORS["bg_main"],
                                     fg=COLORS["primary"])

        xp_feedback_label.place(relx=0.5, rely=0.7, anchor=tk.CENTER)
        self.root.after(1500, xp_feedback_label.destroy)

    def update_plant_image(self):
        selected = self.tree.selection()
        habit_obj = None

        if selected:
            habit_id = selected[0]
            habit_obj = next((h for h in self.habits if str(h.habit_id) == str(habit_id)), None)
        elif self.habits:
            habit_obj = self.habits[0]

        if habit_obj:
            img = self.get_stage_image(habit_obj.xp)
            if img:
                self.image_label.config(image=img)
                self.image_label.image = img
                self.status_label.config(text=f"{habit_obj.name}: {self.get_stage(habit_obj.xp)}")
            else:
                self.image_label.config(image="")
                self.status_label.config(text=f"{habit_obj.name}: (Image missing)")
        else:
            self.image_label.config(image="")
            self.status_label.config(text="Welcome! Add a habit to start.")

    def get_stage(self, xp):
        if xp >= 500:
            return "Tree"
        elif xp >= 400:
            return "Blooming"
        elif xp >= 300:
            return "Budding"
        elif xp >= 200:
            return "Small Plant"
        elif xp >= 100:
            return "Sprout"
        else:
            return "Seed"

    def get_stage_image(self, xp):
        stage = self.get_stage(xp)
        file_map = {
            "Seed": "seed.png",
            "Sprout": "sprout.png",
            "Small Plant": "small_plant.png",
            "Budding": "budding.png",
            "Blooming": "blooming.png",
            "Tree": "tree.png"
        }
        path = os.path.join("assets", file_map[stage])
        if os.path.exists(path):
            try:
                img = Image.open(path).resize((200, 200), Image.LANCZOS)
                return ImageTk.PhotoImage(img)
            except Exception:
                return None
        return None