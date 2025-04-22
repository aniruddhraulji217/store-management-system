import tkinter as tk
from tkinter import ttk, messagebox

class BasePage(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master, bg="#f4f4f4")
        self.controller = controller
        self.create_navbar()
        self.create_sidebar()
        self.create_main_content()

    def create_navbar(self):
        self.navbar = ttk.Frame(self, padding=10)
        self.navbar.pack(side=tk.TOP, fill=tk.X)

        # Back button
        ttk.Button(self.navbar, text="← Back", command=self.controller.go_back).pack(side=tk.LEFT)

        # Title
        ttk.Label(self.navbar, text="Store Management System", font=('Helvetica', 14, 'bold')).pack(side=tk.LEFT, padx=10)

        # User info and logout
        self.user_label = ttk.Label(self.navbar, text="")
        self.user_label.pack(side=tk.RIGHT)

        self.logout_button = ttk.Button(self.navbar, text="Logout", command=self.logout)
        self.logout_button.pack(side=tk.RIGHT, padx=(0, 10))

    def logout(self):
        username = self.user_label.cget("text").split(" ")[0]
        if messagebox.askyesno("Logout", f"Are you sure you want to logout{f' ({username})' if username else ''}?"):
            messagebox.showinfo("Logged Out", "You have been logged out successfully.")
            self.controller.show_login()

    def create_sidebar(self):
        self.sidebar = ttk.Frame(self, width=200, padding=10)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(self.sidebar, text="Menu", font=('Helvetica', 12, 'bold')).pack(anchor=tk.W, pady=10)

        ttk.Button(self.sidebar, text="Dashboard", command=lambda: self.controller.show_page("Dashboard")).pack(fill=tk.X, pady=2)
        ttk.Button(self.sidebar, text="Inventory", command=lambda: self.controller.show_page("Inventory")).pack(fill=tk.X, pady=2)
        # More menu buttons (Reports, Settings) can go here

    def create_main_content(self):
        self.content = ttk.Frame(self, padding=20)
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def update_user_info(self, username, role):
        self.user_label.config(text=f"{username} ({role})")
