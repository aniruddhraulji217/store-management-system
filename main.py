import tkinter as tk
from tkinter import messagebox
from gui_framework import BasePage
from login import LoginSystem

class MainApplication:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Store Management System")
        self.root.geometry("1200x800")
        self.current_user = None
        self.pages = {}
        self.history = []
        
        self.show_login()

    def show_login(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.login_system = LoginSystem(self.root, self.on_login_success)

    def on_login_success(self, user_type, user_data):
        self.current_user = user_data
        self.initialize_pages()
        self.show_page("Dashboard")
        self.root.update()

    def initialize_pages(self):
        from admin_dashboard import AdminDashboard
        from user_dashboard import UserDashboard
        from pages.product_management import ProductManagement
        from pages.user_management import UserManagement
        from pages.supplier_management import SupplierManagement
        from pages.purchase_management import PurchaseManagement  # <-- Add this line

        self.pages = {}

        if self.current_user['role'] == 'admin':
            self.pages["Dashboard"] = AdminDashboard(self.root, self)
            self.pages["ProductManagement"] = ProductManagement(self.root, self)
            self.pages["UserManagement"] = UserManagement(self.root, self)
            self.pages["SupplierManagement"] = SupplierManagement(self.root, self)
            self.pages["PurchaseManagement"] = PurchaseManagement(self.root, self)  # <-- Add this line
        else:
            self.pages["Dashboard"] = UserDashboard(self.root, self)

    def show_page(self, page_name):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Always create a new instance for each page
        if page_name == "Dashboard":
            from admin_dashboard import AdminDashboard
            from user_dashboard import UserDashboard
            if self.current_user['role'] == 'admin':
                page = AdminDashboard(self.root, self)
            else:
                page = UserDashboard(self.root, self)
        elif page_name == "ProductManagement":
            from pages.product_management import ProductManagement
            page = ProductManagement(self.root, self)
        elif page_name == "UserManagement":
            from pages.user_management import UserManagement
            page = UserManagement(self.root, self)
        elif page_name == "SupplierManagement":
            from pages.supplier_management import SupplierManagement
            page = SupplierManagement(self.root, self)  # <-- Add this line
        elif page_name == "PurchaseManagement":
            from pages.purchase_management import PurchaseManagement
            page = PurchaseManagement(self.root, self)
        else:
            messagebox.showerror("Error", f"Unknown page: {page_name}")
            return

        page.pack(fill=tk.BOTH, expand=True)
        page.update_user_info(self.current_user['username'], self.current_user['role'])
        self.history.append(page_name)
        
    def go_back(self):
        if len(self.history) > 1:
            self.history.pop()
            self.show_page(self.history[-1])

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = MainApplication()
        app.run()
    except Exception as e:
        messagebox.showerror("Startup Error", f"Failed to start application: {str(e)}")
