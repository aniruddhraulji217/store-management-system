import tkinter as tk
from tkinter import messagebox
from database import DatabaseManager

class LoginSystem:
    def __init__(self, master, login_success_callback):
        self.master = master
        self.login_success_callback = login_success_callback
        self.frame = tk.Frame(master, bg="#f5f5f5", padx=30, pady=30)
        self.frame.pack(expand=True)

        self.db_manager = DatabaseManager(
            host="localhost",
            user="root",
            password="Aniruddh@217",
            database="inventory_db"
        )
        self.create_login_gui()

    def create_login_gui(self):
        tk.Label(self.frame, text="Login to Store Management", font=('Helvetica', 16, 'bold'), bg="#f5f5f5").grid(row=0, column=0, columnspan=2, pady=(0, 20))

        tk.Label(self.frame, text="Username:", bg="#f5f5f5").grid(row=1, column=0, sticky="e")
        self.username_entry = tk.Entry(self.frame)
        self.username_entry.grid(row=1, column=1)

        tk.Label(self.frame, text="Password:", bg="#f5f5f5").grid(row=2, column=0, sticky="e")
        self.password_entry = tk.Entry(self.frame, show="*")
        self.password_entry.grid(row=2, column=1)

        self.show_pass_var = tk.IntVar()
        show_pass = tk.Checkbutton(self.frame, text="Show Password", variable=self.show_pass_var,
                                   command=self.toggle_password, bg="#f5f5f5")
        show_pass.grid(row=3, column=1, sticky="w")

        tk.Button(self.frame, text="Login", command=self.on_login_button_click, bg="#007acc", fg="white", width=20).grid(row=4, column=0, columnspan=2, pady=20)

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
