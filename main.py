import tkinter as tk
from tkinter import messagebox
from gui_framework import BasePage
from login import LoginSystem

class MainApplication:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Store Management System")
        self.root.geometry("1200x800")  # Adjust size as needed
        self.current_user = None
        self.pages = {}
        self.history = []
        self.future = []  # Add this line to track redo history
        self.root.bind('<Control-z>', lambda event: self.go_back())  # Existing undo binding
        self.root.bind('<Control-y>', lambda event: self.go_forward())  # Add this line for redo

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
        from pages.purchase_management import PurchaseManagement
        from pages.inventory_management import InventoryManagement
        from pages.customer_management import CustomerManagement  # <-- Add this line
        from pages.sales_management import SalesManagement        # <-- Add this line

        self.pages = {}

        if self.current_user['role'] == 'admin':
            self.pages["Dashboard"] = AdminDashboard(self.root, self)
            self.pages["ProductManagement"] = ProductManagement(self.root, self)
            self.pages["UserManagement"] = UserManagement(self.root, self)
            self.pages["SupplierManagement"] = SupplierManagement(self.root, self)
            self.pages["PurchaseManagement"] = PurchaseManagement(self.root, self)
            self.pages["Inventory"] = InventoryManagement(self.root, self)
            self.pages["CustomerManagement"] = CustomerManagement(self.root, self)  # <-- Add this line
            self.pages["SalesManagement"] = SalesManagement(self.root, self)  # Add back the second argument
        else:
            self.pages["Dashboard"] = UserDashboard(self.root, self)
            self.pages["Inventory"] = InventoryManagement(self.root, self)
            self.pages["CustomerManagement"] = CustomerManagement(self.root, self)  # <-- Add this line
            self.pages["SalesManagement"] = SalesManagement(self.root, self)  # Add back the second argument

    def show_page(self, page_name, add_to_history=True):
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
            page = SupplierManagement(self.root, self)
        elif page_name == "PurchaseManagement":
            from pages.purchase_management import PurchaseManagement
            page = PurchaseManagement(self.root, self)
        elif page_name == "Inventory":
            from pages.inventory_management import InventoryManagement
            page = InventoryManagement(self.root, self)  
        elif page_name == "CustomerManagement":
            from pages.customer_management import CustomerManagement
            page = CustomerManagement(self.root, self)
        elif page_name == "SalesManagement":
            from pages.sales_management import SalesManagement
            page = SalesManagement(self.root, self)  # Add the controller argument
        else:
            messagebox.showerror("Error", f"Unknown page: {page_name}")
            return

        page.pack(fill=tk.BOTH, expand=True)
        page.update_user_info(self.current_user['username'], self.current_user['role'])
        if add_to_history:
            self.history.append(page_name)
            self.future = []  # Clear redo history when new page is added

    def go_back(self):
        if len(self.history) > 1:
            current = self.history.pop()
            self.future.append(current)  # Add current page to redo history
            self.show_page(self.history[-1], add_to_history=False)

    def go_forward(self):
        if self.future:
            next_page = self.future.pop()
            self.history.append(next_page)
            self.show_page(next_page, add_to_history=False)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = MainApplication()
        app.run()
    except Exception as e:
        messagebox.showerror("Startup Error", f"Failed to start application: {str(e)}")
