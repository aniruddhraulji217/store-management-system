import tkinter as tk
from tkinter import ttk
from gui_framework import BasePage

class UserDashboard(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.create_content()

    def create_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        ttk.Label(self.content, text="Welcome to User Dashboard", font=('Helvetica', 16)).pack(pady=20)

        ttk.Button(self.content, text="View Inventory", width=30).pack(pady=10)
        ttk.Button(self.content, text="Add Sales Entry", width=30).pack(pady=10)
        ttk.Button(self.content, text="Request Restock", width=30).pack(pady=10)

        # You can later connect these to separate views
