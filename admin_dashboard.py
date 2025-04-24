import tkinter as tk
from tkinter import ttk, messagebox
from gui_framework import BasePage

class AdminDashboard(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.controller = controller
        self.create_dashboard_ui()

    def create_dashboard_ui(self):
        # Main layout: sidebar and right frame
        main_frame = ttk.Frame(self.content)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Sidebar (optional, can be removed if not needed)
        sidebar = ttk.Frame(main_frame, width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=10)
        ttk.Label(sidebar, text="Admin Menu", font=('Segoe UI', 12, 'bold')).pack(pady=(10, 20))
        ttk.Button(sidebar, text="Dashboard", command=lambda: self.controller.show_page("AdminDashboard")).pack(fill=tk.X, pady=2)
        ttk.Button(sidebar, text="Inventory", command=lambda: self.controller.show_page("Inventory")).pack(fill=tk.X, pady=2)
        ttk.Button(sidebar, text="Users", command=lambda: self.controller.show_page("UserManagement")).pack(fill=tk.X, pady=2)
        ttk.Button(sidebar, text="Suppliers", command=lambda: self.controller.show_page("SupplierManagement")).pack(fill=tk.X, pady=2)
        ttk.Button(sidebar, text="Purchases", command=lambda: self.controller.show_page("PurchaseManagement")).pack(fill=tk.X, pady=2)
        ttk.Button(sidebar, text="Reports", command=lambda: self.controller.show_page("Reports")).pack(fill=tk.X, pady=2)
        ttk.Button(sidebar, text="Settings", command=lambda: self.controller.show_page("SettingsPage")).pack(fill=tk.X, pady=2)

        # Right frame for dashboard content
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Dashboard header
        ttk.Label(right_frame, text="Admin Dashboard", font=('Helvetica', 18, 'bold')).pack(anchor='w', pady=(0, 10))

        # Quick Actions
        qa_frame = ttk.LabelFrame(right_frame, text="Quick Actions", padding=8)
        qa_frame.pack(fill=tk.X, pady=(0,8))
        def open_inventory_add_product():
            inventory_page = self.controller.pages.get("Inventory")
            if inventory_page and hasattr(inventory_page, "add_product"):
                inventory_page.add_product()
            else:
                messagebox.showerror("Error", "Inventory page is not available. Please ensure the Inventory page is loaded.")
        ttk.Button(qa_frame, text="Add Product", command=open_inventory_add_product).pack(fill=tk.X, pady=2)
        ttk.Button(qa_frame, text="Add Purchase", command=lambda: self.controller.show_page("PurchaseManagement")).pack(fill=tk.X, pady=2)
        ttk.Button(qa_frame, text="View Reports", command=lambda: self.controller.show_page("Reports")).pack(fill=tk.X, pady=2)
        ttk.Button(qa_frame, text="Low Stock", command=self.show_low_stock).pack(fill=tk.X, pady=2)

        # Example dashboard stats (customize as needed)
        stats_frame = ttk.LabelFrame(right_frame, text="Statistics", padding=8)
        stats_frame.pack(fill=tk.X, pady=(10,8))
        ttk.Label(stats_frame, text="Total Products:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(stats_frame, text="...").grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(stats_frame, text="Total Users:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(stats_frame, text="...").grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(stats_frame, text="Total Sales:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(stats_frame, text="...").grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)

    def show_low_stock(self):
        # Example implementation for low stock alert
        messagebox.showinfo("Low Stock", "This would show a list of products with low stock.")