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
        ttk.Label(self.content, text=f"Welcome, {user['username']}", font=('Helvetica', 14)).pack(pady=20)

        ttk.Button(self.content, text="Record Sale", width=30, command=lambda: self.controller.show_page("SalesManagement")).pack(pady=10)
        # Remove the old button for sales history
        # ttk.Button(self.content, text="Sales History", width=30, command=self.show_my_sales_history).pack(pady=10)
        ttk.Button(self.content, text="Logout", width=30, command=self.controller.show_login).pack(pady=20)

        # Add sales history table
        ttk.Label(self.content, text="My Sales History", font=('Helvetica', 12, 'bold')).pack(pady=(10, 0))
        columns = ("Sale ID", "Date", "Total Amount")
        self.sales_tree = ttk.Treeview(self.content, columns=columns, show='headings', height=10)
        for col in columns:
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, anchor=tk.CENTER, width=120)
        self.sales_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.load_sales_history()

    def load_sales_history(self):
        # Fetch and display sales for the current user
        import mysql.connector
        try:
            db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Aniruddh@217",
                database="inventory_db"
            )
            cursor = db.cursor(dictionary=True)
            user_id = self.controller.current_user['user_id']
            cursor.execute("""
                SELECT sale_id, sale_date, total_amount
                FROM sales
                WHERE user_id = %s
                ORDER BY sale_date DESC
            """, (user_id,))
            rows = cursor.fetchall()
            for i in self.sales_tree.get_children():
                self.sales_tree.delete(i)
            for row in rows:
                self.sales_tree.insert('', 'end', values=(row['sale_id'], row['sale_date'], row['total_amount']))
            cursor.close()
            db.close()
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Database Error", f"Failed to load sales history: {e}")

    def show_my_sales_history(self):
        self.controller.show_page("SalesManagement")
