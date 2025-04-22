import tkinter as tk
from tkinter import ttk
from gui_framework import BasePage
import mysql.connector

class AdminDashboard(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.create_content()

    def create_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        ttk.Label(self.content, text="Welcome to Admin Dashboard", font=('Helvetica', 18, 'bold')).pack(pady=10)

        btn_frame = ttk.Frame(self.content)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="Manage Products",
                   command=lambda: self.controller.show_page("ProductManagement")).pack(padx=10, pady=5)
        # --- Add User Management Button ---
        ttk.Button(btn_frame, text="User Management",
                   command=lambda: self.controller.show_page("UserManagement")).pack(padx=10, pady=5)
        # --- Add Supplier Management Button ---
        ttk.Button(btn_frame, text="Supplier Management",
                   command=lambda: self.controller.show_page("SupplierManagement")).pack(padx=10, pady=5)
        # --- Add Purchase Management Button ---
        ttk.Button(btn_frame, text="Purchase Management",
                   command=lambda: self.controller.show_page("PurchaseManagement")).pack(padx=10, pady=5)
        # --- End Add ---

        stats_frame = ttk.LabelFrame(self.content, text="Quick Stats", padding=10)
        stats_frame.pack(pady=10, fill=tk.X, padx=20)

        self.total_users_label = ttk.Label(stats_frame, text="Total Users: Loading...")
        self.total_users_label.pack(anchor='w', pady=2)
        self.inventory_label = ttk.Label(stats_frame, text="Store Inventory Overview: Loading...")
        self.inventory_label.pack(anchor='w', pady=2)

        self.update_stats()

    def update_stats(self):
        try:
            db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Aniruddh@217",
                database="inventory_db"
            )
            cursor = db.cursor()

            # Get total users
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            self.total_users_label.config(text=f"Total Users: {total_users}")

            # Get total inventory (sum of all product quantities)
            cursor.execute("SELECT SUM(quantity) FROM products")
            total_inventory = cursor.fetchone()[0]
            total_inventory = total_inventory if total_inventory is not None else 0
            self.inventory_label.config(text=f"Store Inventory Overview: {total_inventory} items")

            cursor.close()
            db.close()
        except Exception as e:
            self.total_users_label.config(text="Total Users: Error")
            self.inventory_label.config(text="Store Inventory Overview: Error")
            print(f"Error fetching stats: {e}")

        # Future: Add User Management, Reports, etc.

