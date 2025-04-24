import tkinter as tk
from tkinter import messagebox
from database import DatabaseManager

class LoginSystem:
    def __init__(self, master, login_success_callback):
        self.master = master
        self.login_success_callback = login_success_callback

        self.master.title("Login | Store Management System")
        self.master.geometry("600x400")
        self.master.minsize(400, 300)
        self.master.resizable(True, True)

        # Gradient background
        self.canvas = tk.Canvas(master, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.canvas.bind("<Configure>", self.on_resize)  # Redraw gradient and reposition frame on resize

        # Glass-like login frame
        self.frame = tk.Frame(self.canvas, bg="#ffffff", bd=0, relief="ridge")
        self.frame.configure(bg='#ffffff', highlightbackground='#ccc', highlightthickness=1)
        self.frame_id = self.canvas.create_window(0, 0, window=self.frame, anchor='center')

        self.db_manager = DatabaseManager(
            host="localhost",
            user="root",
            password="Aniruddh@217",
            database="inventory_db"
        )
        self.create_login_gui()

        # Initial placement
        self.master.after(100, self.center_login_frame)

    def on_resize(self, event):
        # Redraw gradient
        self.gradient_bg(event.width, event.height)
        # Center and resize login frame
        self.center_login_frame(event.width, event.height)

    def gradient_bg(self, width=600, height=400):
        self.canvas.delete("gradient")
        for i in range(height):
            r = int(244 - (i * 0.2))
            g = int(246 - (i * 0.1))
            b = int(255 - (i * 0.3))
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            hex_color = f'#{r:02x}{g:02x}{b:02x}'
            self.canvas.create_line(0, i, width, i, fill=hex_color, tags="gradient")

    def center_login_frame(self, width=None, height=None):
        if width is None or height is None:
            width = self.master.winfo_width()
            height = self.master.winfo_height()
        # Set frame size to 60% of window, min 320x220, max 500x400
        frame_w = max(320, min(int(width * 0.6), 500))
        frame_h = max(220, min(int(height * 0.6), 400))
        self.canvas.coords(self.frame_id, width // 2, height // 2)
        self.canvas.itemconfig(self.frame_id, width=frame_w, height=frame_h)
        self.frame.config(width=frame_w, height=frame_h)
        self.frame.update_idletasks()

    def create_login_gui(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.grid_propagate(True)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=2)

        title = tk.Label(self.frame, text="🔐 Login to Store Management", font=('Segoe UI', 16, 'bold'),
                         bg="#ffffff", fg="#2c3e50")
        title.grid(row=0, column=0, columnspan=2, pady=(10, 20), sticky="ew")

        tk.Label(self.frame, text="👤 Username:", font=('Segoe UI', 11), bg="#ffffff").grid(row=1, column=0, sticky="e", pady=6, padx=10)
        self.username_entry = tk.Entry(self.frame, font=('Segoe UI', 11), bg="#f0f0f0", relief="flat")
        self.username_entry.grid(row=1, column=1, pady=6, sticky="ew", padx=(0, 10))

        tk.Label(self.frame, text="🔑 Password:", font=('Segoe UI', 11), bg="#ffffff").grid(row=2, column=0, sticky="e", pady=6, padx=10)
        self.password_entry = tk.Entry(self.frame, font=('Segoe UI', 11), bg="#f0f0f0", relief="flat", show="*")
        self.password_entry.grid(row=2, column=1, pady=6, sticky="ew", padx=(0, 10))

        self.show_pass_var = tk.IntVar()
        show_pass = tk.Checkbutton(self.frame, text="Show Password", variable=self.show_pass_var,
                                   command=self.toggle_password, bg="#ffffff", font=('Segoe UI', 9))
        show_pass.grid(row=3, column=1, sticky="w", pady=6)

        login_btn = tk.Button(self.frame, text="🚀 Login", command=self.on_login_button_click, bg="#007acc",
                              fg="white", font=('Segoe UI', 11, 'bold'), activebackground="#005999",
                              relief='flat', cursor="hand2")
        login_btn.grid(row=4, column=0, columnspan=2, pady=(20, 10), sticky="ew", padx=30)

    def toggle_password(self):
        self.password_entry.config(show="" if self.show_pass_var.get() else "*")

    def verify_login(self, username, password):
        user = self.db_manager.verify_user(username, password)
        if user:
            self.login_success_callback(user['role'], user)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def on_login_button_click(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.verify_login(username, password)
