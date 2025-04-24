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

        user = self.controller.current_user
        ttk.Label(self.content, text=f"Logged in as: {user['username']} ({user['role']})", font=('Helvetica', 10, 'italic')).pack(anchor='ne', padx=10, pady=5)
        ttk.Label(self.content, text="User Dashboard", font=('Helvetica', 16)).pack(pady=20)

        ttk.Button(self.content, text="View Inventory", width=30, command=lambda: self.controller.show_page("Inventory")).pack(pady=10)
        ttk.Button(self.content, text="Record Sale", width=30, command=lambda: self.controller.show_page("SalesManagement")).pack(pady=10)
        ttk.Button(self.content, text="Sales History", width=30, command=self.show_my_sales_history).pack(pady=10)
        ttk.Button(self.content, text="Customers", width=30, command=lambda: self.controller.show_page("CustomerManagement")).pack(pady=10)
        ttk.Button(self.content, text="Request Restock", width=30, command=self.request_restock).pack(pady=10)
        ttk.Button(self.content, text="My Performance", width=30, command=self.show_my_performance).pack(pady=10)
        ttk.Button(self.content, text="Profile", width=30, command=self.edit_profile).pack(pady=10)
        ttk.Button(self.content, text="Logout", width=30, command=self.controller.show_login).pack(pady=20)

    def show_my_sales_history(self):
        # Navigate to SalesManagement and filter for this user's sales
        self.controller.show_page("SalesManagement")
        # Optionally, you can implement filtering in the SalesManagement page based on user role

    def request_restock(self):
        # Simple dialog to request restock
        from tkinter import simpledialog, messagebox
        product_name = simpledialog.askstring("Request Restock", "Enter product name to restock:")
        if product_name:
            # Here you would insert a restock request into a table or notify admin
            messagebox.showinfo("Restock Requested", f"Restock request for '{product_name}' has been sent to admin.")

    def show_my_performance(self):
        # Show a simple stats dialog for the user
        from tkinter import messagebox
        # You would fetch these stats from the database in a real implementation
        stats = "Total Sales: 0\nTotal Profit: 0.00\nBest-Selling Product: N/A"
        messagebox.showinfo("My Performance", stats)

    def edit_profile(self):
        # Simple dialog to update profile (username/password)
        from tkinter import simpledialog, messagebox
        new_name = simpledialog.askstring("Edit Profile", "Enter new username:", initialvalue=self.controller.current_user['username'])
        if new_name:
            # Here you would update the username in the database
            self.controller.current_user['username'] = new_name
            messagebox.showinfo("Profile Updated", "Your username has been updated.")
            self.create_content()
