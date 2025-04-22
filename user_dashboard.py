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

        # Display user info
        user = self.controller.current_user
        user_info = f"Logged in as: {user['username']} ({user['role'].capitalize()})"
        ttk.Label(self.content, text=user_info, font=('Helvetica', 10, 'italic')).pack(anchor='ne', padx=10, pady=5)

        ttk.Label(self.content, text="Welcome to User Dashboard", font=('Helvetica', 16)).pack(pady=20)

        # Inventory View
        ttk.Button(
            self.content,
            text="View Inventory",
            width=30,
            command=lambda: self.controller.show_page("Inventory")
        ).pack(pady=10)

        # Sales Entry
        ttk.Button(
            self.content,
            text="Add Sales Entry",
            width=30,
            command=lambda: self.controller.show_page("SalesManagement")
        ).pack(pady=10)

        # Request Restock
        ttk.Button(
            self.content,
            text="Request Restock",
            width=30,
            command=self.request_restock
        ).pack(pady=10)

        # Optionally: View own sales history
        ttk.Button(
            self.content,
            text="My Sales History",
            width=30,
            command=self.view_my_sales
        ).pack(pady=10)

        # Logout
        ttk.Button(
            self.content,
            text="Logout",
            width=30,
            command=self.controller.show_login
        ).pack(pady=20)

    def request_restock(self):
        # Open a dialog or page for restock request
        from tkinter import simpledialog
        product_name = simpledialog.askstring("Request Restock", "Enter product name to restock:")
        if product_name:
            # Here you would insert a restock request into a table or notify admin
            # For now, just show a confirmation
            from tkinter import messagebox
            messagebox.showinfo("Restock Requested", f"Restock request for '{product_name}' has been sent to admin.")

    def view_my_sales(self):
        # Open a filtered sales page or dialog showing only this user's sales
        # You would implement this in your sales management page
        from tkinter import messagebox
        messagebox.showinfo("My Sales", "This would show your sales history (implement filtering in SalesManagement).")
